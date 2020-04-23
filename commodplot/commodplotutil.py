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


def get_year_line_delta(year):
    if isinstance(year, str):
        year = int(year)

    delta = year - dates.curyear
    return delta


def get_year_line_col(year):
    """
    Given a year, calculate a consistent line colour across charts
    """
    delta = get_year_line_delta(year)
    return year_col_map.get(delta, default_line_col)


def get_year_line_width(year):
    delta = get_year_line_delta(year)
    if delta == 0:
        return 3

    return 2


def line_visible(year):
    delta = get_year_line_delta(year)
    return None if delta >= -5 else "legendonly"


def std_yr_col(df, asdict=False):
    """
    Given a dataframe with yearly columns, determine the line colour to use
    """

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


def min_max_range(seas, shaded_range):
    """
    Calculate min and max for seas
    If an int eg 5, then do curyear -1 and curyear -6
    If list then do the years in that list eg 2012-2019
    :param seas:
    :param shaded_range:
    :return:
    """
    if isinstance(shaded_range, int):
        end_year = seas.columns[-2]
        start_year = end_year - shaded_range
    else:
        start_year, end_year = shaded_range[0], shaded_range[1]

    r = seas[[x for x in seas.columns if x >= start_year and x <= end_year]]
    r['min'] = r.min(1)
    r['max'] = r.max(1)
    r = r[['min', 'max']]

    rangeyr = end_year - start_year
    return r, rangeyr


def format_date_col(col, date_format='%d-%b'):
    """
    Format a column heading as a data
    :param col:
    :param date_format:
    :return:
    """
    try:
        if isinstance(col, str):

            col = pd.to_datetime(col).strftime(date_format)
        if isinstance(col, pd.Timestamp):
            col = col.strftime(date_format)
    except Exception:
        pass # ignore - just return original

    return col


def reindex_year_df_rel_col(df):
    """
    Given a reindexed year dataframe, figure out which column to use for change summary
    Basic algorithm is use current year, unless you are 10 days from end of dataframe
    :param df:
    :return:
    """
    res_col = df.columns[0]

    years = dates.find_year(df)
    last_val_date = df.index[-1]

    colyears = [x for x in df if str(dates.curyear) in str(x)]
    if len(colyears) > 0:
        res_col = colyears[0]
        relyear = (pd.to_datetime('{}-01-01'.format(years.get(res_col)))) # year of this column

        dft = df[colyears].dropna()
        if len(dft) > 0:
            relcol_date = df[res_col].dropna().index[-1] # last date of this column

            delta = last_val_date - relcol_date
            if delta.days < 10:
                relyear1 = (relyear + pd.DateOffset(years=1)).year
                relyear1 = [x for x in df if str(relyear1) in x]
                if len(relyear1) > 0:
                    return relyear1[0]
            else:
                return res_col

    return res_col


