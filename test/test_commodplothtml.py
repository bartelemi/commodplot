import unittest
import plotly.express as px
from commodplot import commodplothtml as cph
import plotly.express as px
from pathlib import Path


class TestCommodPlotHtml(unittest.TestCase):

    def test_output_html(self):
        t = Path('../templates/test_template.html')
        t = Path('C:/dev/commodplot/templates/test_template.html')

        df = px.data.stocks()
        fig = px.line(df, x='date', y="GOOG")
        data = {'pagetitle' : 'test', 'c1': fig}

        cph.output_html(data, template=t, filename='test_output.html')



    def test_convert_dict_plotly_fig_html_div(self):
        df = px.data.gapminder().query("country=='Canada'")
        fig = px.line(df, x="year", y="lifeExp", title='Life expectancy in Canada')

        data = {}
        data['ch1'] = fig
        data['el'] = 1
        data['innerd'] = {}
        data['innerd']['ch2'] = fig

        res = cph.convert_dict_plotly_fig_html_div(data)
        self.assertTrue(isinstance(res['ch1'], str))
        self.assertTrue(isinstance(res['innerd']['ch2'], str))


if __name__ == '__main__':
    unittest.main()


