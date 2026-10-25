import importlib.util
import io
import json
import tempfile
import unittest
from pathlib import Path

from PIL import Image

BASE=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('publisher', BASE/'tools/publish_reviewed_trip.py')
pub=importlib.util.module_from_spec(spec);spec.loader.exec_module(pub)


class CommunityTests(unittest.TestCase):
    def test_four_templates_documented_and_unpriced(self):
        data=json.loads((BASE/'site/data/trip_examples.json').read_text())
        self.assertEqual(4,len(data['trips']))
        self.assertTrue(all(x['kind']=='example' and len(x['trip']['stops'])>=2 for x in data['trips']))
        self.assertTrue(all(x['trip']['expenses']==[] for x in data['trips']))
        self.assertTrue(all(x['trip']['stops'][0]['id'].startswith('municipality:') for x in data['trips']))

    def sample(self, with_photo=False):
        trip=json.loads((BASE/'site/data/trip_examples.json').read_text())['trips'][0]['trip']
        photos=[]
        if with_photo:
            import base64
            x=Image.new('RGB',(240,160),'orange');b=io.BytesIO();x.save(b,'WEBP')
            photos=[{'mime':'image/webp','name':'example','dataUrl':'data:image/webp;base64,'+base64.b64encode(b.getvalue()).decode(),'alt':'River landscape'}]
        return {'schema_version':1,'submission_type':'traveler_story','rights_confirmed':True,
                'nickname':'Test traveler','title':'Tested sample (private fixture)','story':'An example text for moderation testing.',
                'trip':trip, 'photos':photos}

    def test_publish_only_after_explicit_review_and_deduplicate(self):
        with tempfile.TemporaryDirectory() as t:
            site=Path(t); (site/'data').mkdir()
            (site/'data/community_trips.json').write_text('{"version":1,"trips":[]}')
            raw=self.sample(with_photo=True)
            obj=pub.publish(raw, site)
            self.assertEqual('traveler_reported',obj['kind'])
            self.assertEqual(1,len(obj['photos']))
            self.assertTrue((site/obj['photos'][0]['src']).exists())
            meta=json.loads((site/'data/community_trips.json').read_text())
            self.assertEqual(1,len(meta['trips']))
            self.assertNotIn('dataUrl',json.dumps(meta))
            self.assertIn('self_reported',json.dumps(meta))
            with self.assertRaises(ValueError):pub.publish(raw,site)

    def test_invalid_exact_date(self):
        raw=self.sample();raw['trip']['month']='2026-10-25'
        with self.assertRaises(ValueError):pub.validate(raw)

    def test_bad_expense_and_invalid_image_rejected(self):
        raw=self.sample();raw['trip']['expenses']=[{'stopIndex':0,'category':'food','amount':-50}]
        with self.assertRaises(ValueError):pub.validate(raw)
        raw=self.sample();raw['photos']=[{'mime':'image/svg+xml','dataUrl':'data:image/svg+xml;base64,PHN2Zz4='}]
        with self.assertRaises(ValueError):pub.validate(raw)


if __name__=='__main__': unittest.main()
