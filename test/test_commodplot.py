import unittest
import os
import pandas as pd
from commodplot import commodplot
import plotly.graph_objects as go


class TestCommodplot(unittest.TestCase):

    def test_seas_line_plot(self):
        dirname, filename = os.path.split(os.path.abspath(__file__))
        cl = pd.read_csv(os.path.join(dirname, 'test_cl.csv'), index_col=0, parse_dates=True, dayfirst=True)
        cl = cl.dropna(how='all', axis=1)

        res = commodplot.seas_line_plot(cl[cl.columns[-1]])
        self.assertTrue(isinstance(res, go.Figure))

    def test_seas_box_plot(self):
        dirname, filename = os.path.split(os.path.abspath(__file__))
        cl = pd.read_csv(os.path.join(dirname, 'test_cl.csv'), index_col=0, parse_dates=True, dayfirst=True)
        cl = cl.dropna(how='all', axis=1)
        fwd = cl[cl.columns[-1]].resample('MS').mean()

        res = commodplot.seas_box_plot(cl[cl.columns[-1]], fwd)
        self.assertTrue(isinstance(res, go.Figure))



if __name__ == '__main__':
    unittest.main()


