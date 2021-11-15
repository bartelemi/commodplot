import os
import unittest

import plotly.express as px

from commodplot import jinjautils


class TestCommodPlotUtil(unittest.TestCase):

    def test_convert_dict_plotly_fig_html_div(self):
        df = px.data.gapminder().query("country=='Canada'")
        fig = px.line(df, x="year", y="lifeExp", title='Life expectancy in Canada')

        data = {}
        data['ch1'] = fig
        data['el'] = 1
        data['innerd'] = {}
        data['innerd']['ch2'] = fig

        res = jinjautils.convert_dict_plotly_fig_html_div(data)
        self.assertTrue(isinstance(res['ch1'], str))
        self.assertTrue(isinstance(res['innerd']['ch2'], str))

    def test_render_html(self):
        dirname, filename = os.path.split(os.path.abspath(__file__))
        test_out_loc = os.path.join(dirname, 'test.html')
        if os.path.exists(test_out_loc):
            os.remove(test_out_loc)

        data = {'name': 'test'}

        f = jinjautils.render_html(data, 'base.html', 'test.html', package_loader_name='commodplot')

        self.assertTrue(test_out_loc)
        if os.path.exists(test_out_loc):
            os.remove(test_out_loc)


if __name__ == '__main__':
    unittest.main()
