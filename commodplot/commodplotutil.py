import pandas as pd
from commodutil import dates
default_line_col = 'khaki'

# margin to use in HTML charts - make charts bigger but leave space for title
narrow_margin = {'l':2, 'r':2, 't':30, 'b':10}

# try to put deeper colours for recent years, lighter colours for older years
year_col_map = {
    -10: 'wheat',
    -9: 'burlywood',
    -8: 'steelblue',
    -7: 'aquamarine',
    -6: 'orange',
    -5: 'yellow',
    -4: 'saddlebrown',
    -3: 'mediumblue',
    -2: 'darkgreen',
    -1: 'coral',
    0: 'black',
    1: 'red',
    2: 'firebrick',
    3: 'darkred',
    4: 'crimson',
}

"""
Given a year, calculate a consistent line colour across charts
"""
def get_year_line_col(year):
    if isinstance(year, str):
        year = int(year)

    delta = year - dates.curyear

    return year_col_map.get(delta, default_line_col)


"""
Given a dataframe with yearly columns, determine the line colour to use
"""
def std_yr_col(df, asdict=False):
    if isinstance(df, pd.Series):
        df = pd.DataFrame(df)

    yearmap = dates.find_year(df, use_delta=True)
    colmap = {}
    for colname, delta in yearmap.items():
        colmap[colname] = year_col_map.get(delta, default_line_col)

    if asdict:
        return colmap

    # return array of colours to use - this can be passed into cufflift iplot method
    return [colmap[x] for x in df]


def delta_summary_str(df):
    """
    Given a timeseries, produce a string which shows the latest change
    For example if T-1 value is 50 and T-2 is 45, return 50.00  △: +5
    """
    if isinstance(df, pd.DataFrame):
        df = pd.Series(df[df.columns[0]])

    df = df.dropna()
    val1 = df.iloc[-1]
    val2 = df.iloc[-2]
    delta = (val1-val2).round(2)
    symb = '+' if delta > 0.0 else ''

    s = '{}   △: {}{}'.format(val1.round(2), symb,delta)
    return s


