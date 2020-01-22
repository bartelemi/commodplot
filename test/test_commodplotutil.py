import unittest
import pandas as pd
import cufflinks as cf
from commodplot import commodplotutil as cpu


class TestCommodPlotUtil(unittest.TestCase):

    def test_delta_summary_str(self):
        df = cf.datagen.lines(2,1000)
        col = df.columns[0]

        m1 = df.iloc[-1, 0]
        m2 = df.iloc[-2, 0]
        diff = m1 - m2
        res = cpu.delta_summary_str(df)

        self.assertIn(str(m1.round(2)), res)
        self.assertIn(str(diff.round(2)), res)


if __name__ == '__main__':
    unittest.main()


