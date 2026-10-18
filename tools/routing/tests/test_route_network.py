import csv
import json
import gzip
import math
import sys
import tempfile
import types
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from route_network import dijkstra,km_between,build_graph,solve

class Geo:
    def __init__(self,lat,lon): self.lat,self.lon=lat,lon
    def valid(self): return True
class Node:
    def __init__(self,ident,lat,lon): self.id,self.location=ident,Geo(lat,lon)
class Ref:
    def __init__(self,ident): self.ref=ident
class Way:
    def __init__(self,ident,refs,tags):
        self.id,self.nodes,self.tags=ident,[Ref(i) for i in refs],tags

NODES=[Node(1,19.500,-96.900),Node(2,19.500,-96.899),Node(3,19.501,-96.899),
       Node(4,19.501,-96.898),Node(5,19.500,-96.898),Node(6,19.505,-96.89)]
WAYS=[Way(101,[1,2,3,4],{'highway':'residential'}),
      Way(102,[2,5,4],{'highway':'residential','oneway':'yes'}),
      Way(103,[3,6],{'highway':'footway'}),
      Way(104,[6,4],{'highway':'service','access':'private'})]

class FakeHandler:
    def apply_file(self,path,locations=False):
        for n in NODES: self.node(n)
        for w in WAYS: self.way(w)

class RouteTests(unittest.TestCase):
    def test_manual_dijkstra_vs_networkx(self):
        adj={'A':{'B':2,'C':5},'B':{'A':2,'C':1,'D':6},
             'C':{'A':5,'B':1,'D':2},'D':{'B':6,'C':2}}
        distance,route,expanded=dijkstra(adj,'A','D')
        self.assertEqual(distance,5)
        self.assertEqual(route,['A','B','C','D'])
        import networkx as nx
        g=nx.DiGraph()
        for u,vs in adj.items():
            for v,w in vs.items():g.add_edge(u,v,weight=w)
        self.assertEqual(nx.shortest_path_length(g,'A','D',weight='weight'),distance)
        self.assertGreater(expanded,0)

    def test_build_oneway_and_route_geojson(self):
        with tempfile.TemporaryDirectory() as t:
            tmp=Path(t)
            fake=types.ModuleType('osmium'); fake.SimpleHandler=FakeHandler
            with patch.dict(sys.modules,{'osmium':fake}):
                graph=build_graph(tmp/'fake.osm.pbf',(19.49,-96.91,19.51,-96.88),tmp/'roads.json.gz')
            self.assertGreaterEqual(graph['metadata']['nodes'],5)
            self.assertNotIn('2',graph['adj'].get('5',{}))  # one way 2 -> 5
            self.assertIn('5',graph['adj']['2'])
            self.assertNotIn('6',graph['adj'].get('3',{})) # footway not drivable
            self.assertNotIn('6',graph['adj'].get('4',{})) # private road not drivable
            attractions=tmp/'attractions.csv'
            with attractions.open('w',encoding='utf-8',newline='') as f:
                wr=csv.DictWriter(f,fieldnames=['name','lat','lon','status'])
                wr.writeheader()
                wr.writerow({'name':'Point Uno','lat':'19.500','lon':'-96.900','status':'mapped_site'})
                wr.writerow({'name':'Point Dos','lat':'19.501','lon':'-96.898','status':'mapped_site'})
            report=solve(tmp/'roads.json.gz',attractions,'Point Uno','Point Dos',tmp/'route.geojson',0.1)
            self.assertGreater(report['road_distance_km'],0)
            self.assertTrue((tmp/'route.geojson').exists())
            geojson=json.loads((tmp/'route.geojson').read_text())
            self.assertEqual(geojson['features'][0]['geometry']['type'],'LineString')
            self.assertEqual(len(geojson['features']),3)
            self.assertEqual(report['road_graph_nodes'],len(graph['coords']))

    def test_unreachable(self):
        with self.assertRaisesRegex(ValueError,'No route'):
            dijkstra({'A':{'B':1},'B':{},'C':{}},'A','C')

if __name__=='__main__':unittest.main()
