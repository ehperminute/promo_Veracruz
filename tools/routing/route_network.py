#!/usr/bin/env python3
"""Veracruz PP: offline drivable OSM road graph + distance-minimizing Dijkstra.

No network requests; does not modify the website or tourism database.
Requirements for `build`: pip install osmium
"""
from __future__ import annotations
import argparse, csv, gzip, heapq, json, math, sys, time, unicodedata
from pathlib import Path

DRIVABLE = {'motorway','trunk','primary','secondary','tertiary','unclassified',
            'residential','living_street','service','motorway_link','trunk_link',
            'primary_link','secondary_link','tertiary_link'}
EARTH_KM = 6371.0088


def km_between(a, b):
    lat1, lon1 = map(math.radians, a)
    lat2, lon2 = map(math.radians, b)
    dlat, dlon = lat2-lat1, lon2-lon1
    h = math.sin(dlat/2)**2 + math.cos(lat1)*math.cos(lat2)*math.sin(dlon/2)**2
    return 2 * EARTH_KM * math.asin(min(1, math.sqrt(h)))


def build_graph(pbf: Path, bbox, output: Path):
    try:
        import osmium
    except ImportError as err:
        raise RuntimeError('Missing osmium. Install: python -m pip install osmium') from err
    south, west, north, east = bbox
    if not(-90 <= south < north <= 90 and -180 <= west < east <= 180):
        raise ValueError('Invalid bbox; expected SOUTH WEST NORTH EAST')
    t0 = time.monotonic()
    nodes = {}
    adj = {}
    counters = {'eligible_ways':0, 'edge_segments':0, 'ways_before_nodes':0, 'private_roads_skipped':0}
    def add_edge(a, b, distance):
        neighbors = adj.setdefault(a, {})
        if distance < neighbors.get(b, math.inf):
            neighbors[b] = round(distance, 3)

    class RoadCollector(osmium.SimpleHandler):
        # Geofabrik extracts normally list nodes before ways. We explicitly detect
        # an unsupported unordered input rather than returning an incomplete graph.
        def __init__(self):
            super().__init__()
            self.seen_node = False
            self.seen_way = False

        def node(self, n):
            self.seen_node = True
            if not n.location.valid():
                return
            lat, lon = n.location.lat, n.location.lon
            if south <= lat <= north and west <= lon <= east:
                nodes[n.id] = [lat, lon]

        def way(self, w):
            self.seen_way = True
            if not self.seen_node:
                counters['ways_before_nodes'] += 1
                return
            highway = w.tags.get('highway')
            if highway not in DRIVABLE:
                return
            access = w.tags.get('access')
            motor_vehicle = w.tags.get('motor_vehicle')
            motorcar = w.tags.get('motorcar')
            if access in ('private','no') or motor_vehicle in ('private','no') or motorcar in ('private','no'):
                counters['private_roads_skipped'] += 1
                return
            counters['eligible_ways'] += 1
            oneway = w.tags.get('oneway')
            reverse_only = oneway == '-1'
            forward_only = (oneway in ('yes','true','1') or
                            (oneway is None and (highway == 'motorway' or w.tags.get('junction') == 'roundabout')))
            refs = [ref.ref for ref in w.nodes]
            for a, b in zip(refs, refs[1:]):
                if a not in nodes or b not in nodes or a == b:
                    continue
                distance = km_between(nodes[a], nodes[b])
                if not distance:
                    continue
                counters['edge_segments'] += 1
                if not reverse_only:
                    add_edge(a, b, distance)
                if not forward_only:
                    add_edge(b, a, distance)

    collector = RoadCollector()
    print('Building road graph from local OSM data (one streaming pass).', flush=True)
    collector.apply_file(str(pbf), locations=False)
    if counters['ways_before_nodes']:
        raise RuntimeError('OSM objects not sorted nodes-before-ways. Use a standard Geofabrik extract.')
    road_nodes = set(adj)
    for neighbors in adj.values():
        road_nodes.update(neighbors)
    if len(road_nodes) < 2:
        raise RuntimeError('No driveable road edges found in bbox; nothing written.')
    # Discard unused geocoded vertices.
    coords = {str(n):nodes[n] for n in road_nodes}
    compact = {str(n):{str(k):v for k,v in adj.get(n,{}).items()} for n in road_nodes}
    payload = {
        'metadata':{'source':str(pbf.name),'bbox':[south,west,north,east],
                    'weight':'approximate road-segment distance, km, haversine over OSM segments',
                    'limitations':'No turn restrictions, road closures, verified entrances or travel times',
                    'nodes':len(coords),'directed_arcs':sum(map(len,compact.values())),
                    'elapsed_s':round(time.monotonic()-t0,1),**counters},
        'coords':coords,'adj':compact}
    output.parent.mkdir(parents=True,exist_ok=True)
    with gzip.open(output,'wt',encoding='utf-8',compresslevel=5) as f:
        json.dump(payload,f,separators=(',',':'))
    print(json.dumps({'graph':str(output),**payload['metadata']},indent=2))
    return payload


def dijkstra(adjacency, start, finish):
    """Pure Python Dijkstra with nonnegative edge weights, no NetworkX dependency."""
    best = {start:0.0}
    previous = {}
    heap = [(0.0,start)]
    expanded = 0
    while heap:
        distance, node = heapq.heappop(heap)
        if distance > best.get(node,math.inf) + 1e-9:
            continue
        expanded += 1
        if node == finish:
            route = [node]
            while route[-1] != start:
                route.append(previous[route[-1]])
            route.reverse()
            return distance, route, expanded
        for neighbor, weight in adjacency.get(node, {}).items():
            if weight < 0:
                raise ValueError('Dijkstra requires nonnegative weights')
            candidate = distance+weight
            if candidate + 1e-9 < best.get(neighbor,math.inf):
                best[neighbor]=candidate
                previous[neighbor]=node
                heapq.heappush(heap,(candidate,neighbor))
    raise ValueError('No route found between chosen graph nodes')


def fold(s):
    return ''.join(c for c in unicodedata.normalize('NFD',s.casefold()) if unicodedata.category(c) != 'Mn')


def read_attractions(csv_path):
    with csv_path.open(encoding='utf-8-sig',newline='') as f:
        return list(csv.DictReader(f))


def find_attraction(records, query):
    q = fold(query)
    exact = [r for r in records if fold(r.get('name','')) == q]
    if len(exact)==1:
        return exact[0]
    matched = exact or [r for r in records if q in fold(r.get('name',''))]
    if len(matched) == 1:
        return matched[0]
    if not matched:
        raise ValueError(f'No attraction named {query!r} in current site/data/attractions.csv')
    raise ValueError(f'Ambiguous attraction {query!r}: '+', '.join(r['name'] for r in matched[:10]))


def snap(coord, coords, max_km):
    """Snap to nearby OSM road vertex; straight-line offset is not a driveable entrance."""
    best = min(((km_between(coord, position), identifier)
                for identifier,position in coords.items()), default=None)
    if best is None or best[0] > max_km:
        raise ValueError(f'No mapped road vertex within {max_km:g} km of {coord}. Try a larger regional bbox or verify entrance.')
    return best[1], best[0]


def solve(graph_file, attractions_csv, src_query, dst_query, output, max_snap):
    with gzip.open(graph_file,'rt',encoding='utf-8') as f:
        graph=json.load(f)
    records=read_attractions(attractions_csv)
    src=find_attraction(records,src_query)
    dst=find_attraction(records,dst_query)
    start=(float(src['lat']),float(src['lon']))
    finish=(float(dst['lat']),float(dst['lon']))
    for pt, r in ((start,src),(finish,dst)):
        if not all(math.isfinite(v) for v in pt):
            raise ValueError('Invalid site coordinates: '+r['name'])
    origin, off1=snap(start,graph['coords'],max_snap)
    target, off2=snap(finish,graph['coords'],max_snap)
    started=time.perf_counter()
    length,path,expanded=dijkstra(graph['adj'],origin,target)
    search_ms=(time.perf_counter()-started)*1000
    geojson={'type':'FeatureCollection','features':[
        {'type':'Feature','properties':{'kind':'route','from':src['name'],'to':dst['name'],
            'road_distance_km':round(length,3),'algorithm':'manual Dijkstra',
            'warning':'Road graph only: site positions are not verified vehicle entrances.'},
         'geometry':{'type':'LineString','coordinates':[
             [graph['coords'][n][1],graph['coords'][n][0]] for n in path]}},
        *[{'type':'Feature','properties':{'kind':'attraction','name':r['name'],
                  'snapped_distance_km':round(offset,3),
                  'coordinate_status':r.get('status','unknown')},
            'geometry':{'type':'Point','coordinates':[float(r['lon']),float(r['lat'])]}}
          for r,offset in ((src,off1),(dst,off2))]]}
    output.parent.mkdir(parents=True,exist_ok=True)
    output.write_text(json.dumps(geojson,ensure_ascii=False,indent=2),encoding='utf-8')
    report={'from':src['name'],'to':dst['name'],'road_distance_km':round(length,3),
            'straight_line_km':round(km_between(start,finish),3),
            'dijkstra_search_ms':round(search_ms,2),
            'snapped_from_site_km':round(off1,3),'snapped_to_site_km':round(off2,3),
            'dijkstra_expanded_nodes':expanded,'road_graph_nodes':len(graph['coords']),
            'route_polyline_nodes':len(path),'result':str(output),
            'interpretation':'Distance-minimizing path in simplified OSM vehicle graph. NOT verified driving directions, ETA, or entrance access.'}
    print(json.dumps(report,indent=2,ensure_ascii=False))
    return report


def main():
    p=argparse.ArgumentParser(description=__doc__)
    subs=p.add_subparsers(dest='task',required=True)
    b=subs.add_parser('build',help='Extract regional road network from local Mexico PBF')
    b.add_argument('--pbf',required=True,type=Path)
    b.add_argument('--bbox',nargs=4,type=float,required=True,metavar=('SOUTH','WEST','NORTH','EAST'))
    b.add_argument('--out',default='data/processed/xalapa_roads.json.gz',type=Path)
    r=subs.add_parser('route',help='Route between two attractions by name')
    r.add_argument('--graph',default='data/processed/xalapa_roads.json.gz',type=Path)
    r.add_argument('--attractions',default='site/data/attractions.csv',type=Path)
    r.add_argument('--from',dest='origin',required=True)
    r.add_argument('--to',dest='destination',required=True)
    r.add_argument('--out',default='data/processed/shortest_route.geojson',type=Path)
    r.add_argument('--max-snap-km',type=float,default=2.0)
    a=p.parse_args()
    if a.task=='build':
        build_graph(a.pbf,a.bbox,a.out)
    else:
        solve(a.graph,a.attractions,a.origin,a.destination,a.out,a.max_snap_km)

if __name__=='__main__':
    try:main()
    except Exception as err:
        print(f'ERROR: {err}',file=sys.stderr)
        sys.exit(1)
