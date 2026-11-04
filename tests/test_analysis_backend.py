import os
from pathlib import Path
import tempfile
import unittest

import numpy as np
import pandas as pd

from analysis_backend import (
    COUNTY_ID, COUNTY_NAME, COMPLAINTS, ORIGINATIONS, RATE,
    load_county_metrics, overview_metrics, rank_counties, county_detail,
)


class BackendTests(unittest.TestCase):
    def setUp(self):
        self.data = load_county_metrics()

    def test_known_totals(self):
        summary = overview_metrics(self.data)
        self.assertEqual(summary['counties_with_mapped_complaints'], 25)
        self.assertEqual(summary['mapped_complaints'], 64)
        self.assertEqual(summary['originations_in_these_counties'], 9966)
        self.assertAlmostEqual(summary['pooled_complaints_per_1000_originations'], 64000/9966)

    def test_known_counties(self):
        for fips, complaints, originations, rate in [
            ('06037', 13, 3211, 13000/3211), ('06007', 1, 16, 62.5),
        ]:
            with self.subTest(fips=fips):
                row = county_detail(self.data, fips).iloc[0]
                self.assertEqual(row[COUNTY_ID], fips)
                self.assertEqual(row[COMPLAINTS], complaints)
                self.assertEqual(row[ORIGINATIONS], originations)
                self.assertAlmostEqual(row[RATE], rate)

    def test_filters_limits_and_empty_schema(self):
        self.assertEqual(rank_counties(self.data).iloc[0][COUNTY_ID], '06007')
        filtered = rank_counties(self.data, 100)
        self.assertNotIn('06007', set(filtered[COUNTY_ID]))
        self.assertTrue((filtered[ORIGINATIONS] >= 100).all())
        self.assertEqual(len(rank_counties(self.data, limit=5)), 5)
        self.assertIn('06037', set(rank_counties(self.data, 3211)[COUNTY_ID]))
        empty = rank_counties(self.data, 3212)
        self.assertTrue(empty.empty)
        self.assertEqual(list(empty.columns), list(self.data.columns))
        self.assertTrue(empty.dtypes.equals(self.data.dtypes))

    def test_invalid_filter_parameters(self):
        for value in [-1, 1.5, '100']:
            with self.subTest(value=value), self.assertRaises(ValueError):
                rank_counties(self.data, min_originations=value)
        for value in [0, -1, 1.5]:
            with self.subTest(limit=value), self.assertRaises(ValueError):
                rank_counties(self.data, limit=value)

    def test_tie_breaking_by_fips(self):
        sample = self.data.iloc[:2].copy()
        sample[RATE] = 5.0
        self.assertEqual(rank_counties(sample)[COUNTY_ID].tolist(), sorted(sample[COUNTY_ID]))

    def test_unknown_county_and_copy_isolation(self):
        original = self.data.copy(deep=True)
        with self.assertRaises(KeyError):
            county_detail(self.data, '06003')
        returned = county_detail(self.data, '06037')
        returned.loc[0, COMPLAINTS] = 999
        pd.testing.assert_frame_equal(self.data, original)

    def test_bad_input_files_are_rejected(self):
        mutations = {
            'corrupt_index': (RATE, 999), 'zero_denominator': (ORIGINATIONS, 0),
            'blank_name': (COUNTY_NAME, ' '), 'fractional_count': (COMPLAINTS, 1.5),
            'infinite_index': (RATE, np.inf), 'missing_index': (RATE, np.nan),
            'invalid_fips': (COUNTY_ID, '6037'),
        }
        with tempfile.TemporaryDirectory() as folder:
            for label, (column, value) in mutations.items():
                wrong = self.data.copy()
                if label == 'fractional_count':
                    wrong[column] = wrong[column].astype(float)
                wrong.loc[0, column] = value
                path = Path(folder)/f'{label}.csv'
                wrong.to_csv(path, index=False)
                with self.subTest(label=label), self.assertRaises((ValueError, TypeError)):
                    load_county_metrics(path)
            duplicate = pd.concat([self.data, self.data.iloc[[0]]])
            path = Path(folder)/'duplicate.csv'
            duplicate.to_csv(path, index=False)
            with self.assertRaises(ValueError):
                load_county_metrics(path)

    def test_default_path_works_from_another_directory(self):
        old = Path.cwd()
        with tempfile.TemporaryDirectory() as folder:
            try:
                os.chdir(folder)
                self.assertEqual(len(load_county_metrics()), 25)
            finally:
                os.chdir(old)


if __name__ == '__main__':
    unittest.main()
