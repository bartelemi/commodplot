import unittest
import os
import pandas as pd
from commodplot import commodplot
from commodutil import forwards
import plotly.graph_objects as go


class TestCommodplot(unittest.TestCase):

    def test_seas_line_plot(self):
        dirname, filename = os.path.split(os.path.abspath(__file__))
        cl = pd.read_csv(os.path.join(dirname, 'test_cl.csv'), index_col=0, parse_dates=True, dayfirst=True)
        cl = cl.dropna(how='all', axis=1)

        res = commodplot.seas_line_plot(cl[cl.columns[-1]], shaded_range=5)
        self.assertTrue(isinstance(res, go.Figure))

    def test_reindex_year_line_plot(self):
        dirname, filename = os.path.split(os.path.abspath(__file__))
        cl = pd.read_csv(os.path.join(dirname, 'test_cl.csv'), index_col=0, parse_dates=True, dayfirst=True)
        cl = cl.dropna(how='all', axis=1)
        cl = cl.rename(columns={x: pd.to_datetime(forwards.convert_contract_to_date(x)) for x in cl.columns})

        sp = forwards.time_spreads(cl, 12, 12)

        res = commodplot.reindex_year_line_plot(sp)
        self.assertTrue(isinstance(res, go.Figure))

    def test_seas_box_plot(self):
        dirname, filename = os.path.split(os.path.abspath(__file__))
        cl = pd.read_csv(os.path.join(dirname, 'test_cl.csv'), index_col=0, parse_dates=True, dayfirst=True)
        cl = cl.dropna(how='all', axis=1)
        fwd = cl[cl.columns[-1]].resample('MS').mean()

        res = commodplot.seas_box_plot(cl[cl.columns[-1]], fwd)
        self.assertTrue(isinstance(res, go.Figure))

    def test_seas_table(self):
        dirname, filename = os.path.split(os.path.abspath(__file__))
        cl = pd.read_csv(os.path.join(dirname, 'test_cl.csv'), index_col=0, parse_dates=True, dayfirst=True)
        cl = cl.dropna(how='all', axis=1)
        fwd = cl[cl.columns[-1]].resample('MS').mean()

        res = commodplot.seas_table_plot(cl[cl.columns[-1]], fwd)
        self.assertTrue(isinstance(res, go.Figure))


if __name__ == '__main__':
    unittest.main()


