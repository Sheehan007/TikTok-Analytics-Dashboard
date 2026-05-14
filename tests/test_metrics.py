import unittest

from scripts.metrics import cpa, cpc, cpm, ctr, cvr, growth, retention, roas, safe_divide


class MetricCalculationTests(unittest.TestCase):
    def test_safe_divide_handles_zero(self):
        self.assertEqual(safe_divide(10, 0), 0.0)
        self.assertEqual(safe_divide(10, None), 0.0)

    def test_advertising_metrics(self):
        self.assertAlmostEqual(ctr(250, 10000), 0.025)
        self.assertAlmostEqual(cvr(25, 250), 0.1)
        self.assertAlmostEqual(cpc(500, 250), 2.0)
        self.assertAlmostEqual(cpm(500, 10000), 50.0)
        self.assertAlmostEqual(cpa(500, 25), 20.0)
        self.assertAlmostEqual(roas(2500, 500), 5.0)

    def test_retention_and_growth(self):
        self.assertAlmostEqual(retention(72, 100), 0.72)
        self.assertAlmostEqual(growth(1250, 1000), 0.25)


if __name__ == "__main__":
    unittest.main()
