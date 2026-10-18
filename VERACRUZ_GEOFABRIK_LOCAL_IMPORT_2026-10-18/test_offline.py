"""No network, no real PBF decoder; verifies feature selection and centroid/data pipeline with mock reader."""
import importlib.util, types, sys, json
from pathlib import Path
pkg=Path(__file__).parent
spec=importlib.util.spec_from_file_location('localosm',pkg/'import_local_osm.py');mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
class Loc:
    def __init__(self,lat,lon):self.lat=lat;self.lon=lon
    def valid(self):return True
class Node:
    def __init__(self,id,lat,lon,tags=None):self.id=id;self.location=Loc(lat,lon);self.tags=tags or {}
class Way:
    def __init__(self,id,refs,tags=None):self.id=id;self.nodes=[types.SimpleNamespace(ref=i) for i in refs];self.tags=tags or {}
class Relation:
    def __init__(self,id,members,tags):self.id=id;self.members=[types.SimpleNamespace(type=k,ref=i) for k,i in members];self.tags=tags
class Handler:
    def apply_file(self,p):
        for n in nodes:
            cb=getattr(self,'node',None)
            if cb:cb(n)
        for w in ways:
            cb=getattr(self,'way',None)
            if cb:cb(w)
        for r in relations:
            cb=getattr(self,'relation',None)
            if cb:cb(r)
nodes=[Node(1,19.51,-96.91,{'name':'Museum Test','tourism':'museum'}),Node(2,19.52,-96.92),Node(3,19.54,-96.94),Node(4,25,-104,{'name':'Wrong state','tourism':'attraction'}),Node(5,19.53,-96.91,{'name':'Hotel','tourism':'hotel'})]
ways=[Way(100,[2,3],{'name':'Cascada Test','waterway':'waterfall'}),Way(101,[1,2])]
relations=[Relation(300,[('w',101)],{'name':'Archaeology Test','historic':'archaeological_site'})]
sys.modules['osmium']=types.SimpleNamespace(SimpleHandler=Handler)
results=mod.parse_pbf(Path('unused.osm.pbf'),[(-96.92,19.52)]*212)
assert len(results)==3,results
assert {r['tags']['name'] for r in results}=={'Museum Test','Cascada Test','Archaeology Test'}
assert any(r['type']=='way' and abs(r['center']['lat']-19.53)<1e-6 for r in results)
assert any(r['type']=='relation' for r in results)
assert not mod.close_to_seeds(25,-104,[(-96.92,19.52)])
assert mod.eligible({'name':'Museo','tourism':'museum'})
assert not mod.eligible({'name':'Hotel','tourism':'hotel'})
print('PASS: point / way / relation extraction, referenced-node lookup, OSM tag filtering, geographic proximity')
