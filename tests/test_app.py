from pathlib import Path
import shutil
import tempfile
import unittest

from streamlit.testing.v1 import AppTest

ROOT = Path(__file__).resolve().parents[1]
EMPTY = 'No counties meet this minimum origination count. Lower the threshold.'
ERROR = 'Dataset unavailable or failed validation. Contact the project team.'


class AppTests(unittest.TestCase):
    def launch(self, path=None):
        app = AppTest.from_file(str(path or ROOT/'app.py'), default_timeout=20).run()
        self.assertEqual(len(app.exception), 0)
        return app

    def test_default_view(self):
        app = self.launch()
        self.assertEqual(app.selectbox(key='county').value, '06037')
        self.assertEqual([m.value for m in app.metric[:4]], ['25', '64', '9,966', '6.42'])
        self.assertEqual([m.value for m in app.metric[4:]], ['13', '3,211', '4.05'])
        self.assertEqual(len(app.dataframe[0].value), 25)
        self.assertEqual(app.dataframe[0].value.iloc[0]['County'], 'Butte County')

    def test_filter_keeps_selected_detail_and_summaries(self):
        app = self.launch()
        app.selectbox(key='county').set_value('06007').run()
        app.number_input(key='minimum').set_value(100).run()
        self.assertFalse(app.exception)
        self.assertNotIn('Butte County', set(app.dataframe[0].value['County']))
        self.assertEqual([m.value for m in app.metric[:4]], ['25', '64', '9,966', '6.42'])
        self.assertEqual([m.value for m in app.metric[4:]], ['1', '16', '62.50'])
        self.assertTrue(any('excluded from the ranking' in item.value for item in app.info))

    def test_empty_ranking_keeps_detail(self):
        app = self.launch()
        app.number_input(key='minimum').set_value(3212).run()
        self.assertFalse(app.exception)
        self.assertTrue(any(item.value == EMPTY for item in app.info))
        self.assertEqual(len(app.dataframe), 0)
        self.assertEqual([m.value for m in app.metric], ['25', '64', '9,966', '6.42', '13', '3,211', '4.05'])

    def test_top_n_is_only_a_ranking_limit(self):
        app = self.launch()
        app.selectbox(key='top_n').set_value(5).run()
        self.assertFalse(app.exception)
        self.assertEqual(len(app.dataframe[0].value), 5)
        self.assertEqual(app.metric[3].value, '6.42')
        self.assertEqual(app.metric[-1].value, '4.05')
        self.assertTrue(any('outside the selected top-N' in item.value for item in app.info))

    def test_data_failure_stops_outputs_and_does_not_reuse_stale_state(self):
        for kind in ['missing', 'corrupt_index', 'consistent_but_changed']:
            with self.subTest(kind=kind), tempfile.TemporaryDirectory() as folder:
                temp = Path(folder)
                for name in ['app.py', 'analysis_backend.py', 'county_metrics_2024.csv']:
                    shutil.copyfile(ROOT/name, temp/name)
                app = self.launch(temp/'app.py')
                self.assertEqual(len(app.metric), 7)
                csv_path = temp/'county_metrics_2024.csv'
                if kind == 'missing':
                    csv_path.unlink()
                elif kind == 'corrupt_index':
                    csv_path.write_text(csv_path.read_text().replace('62.5', '999.0'), encoding='utf-8')
                else:
                    # A coherent changed row would pass the older formula-only validator.
                    csv_path.write_text(csv_path.read_text().replace('Butte County,1,16,62.5', 'Butte County,2,16,125.0'), encoding='utf-8')
                app.run()
                self.assertFalse(app.exception)
                self.assertEqual(app.error[0].value, ERROR)
                self.assertEqual(len(app.metric), 0)
                self.assertEqual(len(app.dataframe), 0)


if __name__ == '__main__':
    unittest.main()
