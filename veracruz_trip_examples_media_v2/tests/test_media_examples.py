import json, tempfile, shutil, unittest, subprocess
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]

class ExampleTests(unittest.TestCase):
    def test_four_examples_clearly_not_real_purchases(self):
        data=json.loads((ROOT/'site/data/trip_examples.json').read_text())
        self.assertEqual(4,len(data['trips']))
        for t in data['trips']:
            self.assertEqual(t['kind'],'example')
            self.assertEqual(t['trip']['expenses'],[]) # never published as real traveler spending
            self.assertEqual(t['exampleBudget']['kind'],'hypothetical_scenario')
            self.assertTrue(t['coverPhoto']['page'].startswith('https://commons.wikimedia.org/wiki/File:'))
            self.assertGreaterEqual(len(t['exampleBudget']['items']),4)
            for e in t['exampleBudget']['items']:
                self.assertGreater(e['amount'],0)
                self.assertLess(e['stopIndex'],len(t['trip']['stops']))
                self.assertEqual(e['priceBasis'],'illustrative_allowance_not_observed')
    def test_idempotent_and_do_not_overwrite_published(self):
        with tempfile.TemporaryDirectory() as d:
            site=Path(d)/'site'; (site/'js').mkdir(parents=True); (site/'data').mkdir()
            (site/'viajes.html').write_text('<head><script defer src="js/trip-gallery.js?v=old"></script></head><main></main>',encoding='utf8')
            (site/'js/trip-journal-core.js').write_text('/* existing */')
            saved='{"version":1,"trips":[{"kind":"traveler_reported","id":"real-story"}]}'
            (site/'data/community_trips.json').write_text(saved)
            for i in range(2):
                subprocess.run(['python',str(ROOT/'install.py'),d],check=True,capture_output=True,text=True)
            txt=(site/'viajes.html').read_text()
            self.assertEqual(1,txt.count('js/trip-example-budget.js'))
            self.assertEqual(1,txt.count('js/trip-gallery.js'))
            self.assertEqual(saved,(site/'data/community_trips.json').read_text())

if __name__=='__main__': unittest.main()
