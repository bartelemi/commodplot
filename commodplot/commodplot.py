import pandas as pd
import plotly as py
import plotly.graph_objects as go
from commodplot import commodplotutil as cpu
from commodutil import transforms

hist_hover_temp = '<i>%{text}</i>: %{y:.2f}'


def add_shaded_range_traces(fig, seas, shaded_range):
    r, rangeyr = cpu.min_max_range(seas, shaded_range)
    if rangeyr is not None:
        max_trace = go.Scatter(x=r.index, y=r['max'].values, fill=None, name='%syr Max' % rangeyr, mode='lines',
                                 line_color='lightsteelblue', line_width=0.1)
        fig.add_trace(max_trace)
        min_trace = go.Scatter(x=r.index, y=r['min'].values, fill='tonexty', name='%syr Min' % rangeyr, mode='lines',
                                 line_color='lightsteelblue', line_width=0.1)
        fig.add_trace(min_trace)


def gen_title(df, **kwargs):
    title = kwargs.get('title', '')
    inc_change_sum = kwargs.get('inc_change_sum', True)
    if inc_change_sum:
        title = '{}   {}'.format(title, cpu.delta_summary_str(df))

    return title


def seas_line_plot(df, fwd=None, **kwargs):
    """
     Given a DataFrame produce a seasonal line plot (x-axis - Jan-Dec, y-axis Yearly lines)
     Can overlay a forward curve on top of this
    """
    if isinstance(df, pd.Series):
        df = pd.DataFrame(df)

    histfreq = kwargs.get('histfreq', None)
    if histfreq is None:
        histfreq = pd.infer_freq(df.index)
        if histfreq is None:
            histfreq = 'D' # sometimes infer_freq returns null - assume mostly will be a daily series

    if histfreq.startswith('W'):
        seas = transforms.seasonalise_weekly(df, freq=histfreq  )
    else:
        seas = transforms.seasonailse(df)

    text = seas.index.strftime('%b')
    if histfreq in ['B', 'D']:
        text = seas.index.strftime('%d-%b')
    if histfreq.startswith('W'):
        text = seas.index.strftime('%d-%b')

    fig = go.Figure()

    shaded_range = kwargs.get('shaded_range', None)
    if shaded_range is not None:
        add_shaded_range_traces(fig, seas, shaded_range)

    for col in seas.columns:
        fig.add_trace(
            go.Scatter(x=seas.index, y=seas[col], hoverinfo='y', name=col, hovertemplate=hist_hover_temp, text=text,
                       visible=cpu.line_visible(col), line=dict(color=cpu.get_year_line_col(col), width=cpu.get_year_line_width(col))))

    title = gen_title(df, **kwargs)

    if fwd is not None:
        fwdfreq = pd.infer_freq(fwd.index)
        # for charts which are daily, resample the forward curve into a daily series
        if histfreq in ['B', 'D'] and fwdfreq in ['MS', 'ME']:
            fwd = transforms.format_fwd(fwd, df.iloc[-1].name) # only applies for forward curves
        fwd = transforms.seasonailse(fwd)

        for col in fwd.columns:
            fig.add_trace(
                go.Scatter(x=fwd.index, y=fwd[col], hoverinfo='y', name=col, hovertemplate=hist_hover_temp, text=text,
                           line=dict(color=cpu.get_year_line_col(col), dash='dot')))

    legend = go.layout.Legend(font=dict(size=10))
    yaxis_title = kwargs.get('yaxis_title', None)
    fig.layout.xaxis.tickvals = pd.date_range(seas.index[0], seas.index[-1], freq='MS')
    fig.update_layout(title=title,  xaxis_tickformat='%b', yaxis_title=yaxis_title, legend=legend)

    return fig


def seas_box_plot(hist, fwd=None, **kwargs):
    hist = transforms.monthly_mean(hist)
    hist = hist.T

    data = []
    monthstr = {x.month: x.strftime('%b') for x in pd.date_range(start='2018', freq='M', periods=12)}
    for x in hist.columns:
        trace = go.Box(
            name=monthstr[x],
            y=hist[x]
        )
        data.append(trace)

    fwdl = transforms.seasonailse(fwd)
    fwdl.index = fwdl.index.strftime('%b')
    for col in fwdl.columns:
        ser = fwdl[col].copy()
        trace = go.Scatter(
            name=col,
            x=ser.index,
            y=ser,
            line=dict(color=cpu.get_year_line_col(col), dash='dot')
        )
        data.append(trace)

    fig = go.Figure(data=data)
    title = kwargs.get('title', '')
    fig.update_layout(title=title)

    return fig


def seas_table_plot(hist, fwd=None):
    df = cpu.seas_table(hist, fwd)

    colsh = list(df.columns)
    colsh.insert(0, 'Period')

    cols = [df[x] for x in df]
    cols.insert(0, list(df.index))
    fillcolor = ['lavender'] * 12
    fillcolor.extend(['aquamarine'] * 4)
    fillcolor.extend(['darkturquoise'] * 2)
    fillcolor.append('dodgerblue')

    figm = go.Figure(data=[go.Table(
        header=dict(values=colsh, fill_color='paleturquoise', align='left'),
        cells=dict(values=cols, fill_color=[fillcolor], align='left'))
    ])
    return figm


def table_plot(df, **kwargs):
    row_even_colour = kwargs.get('row_even_colour', 'lightgrey')
    row_odd_color = kwargs.get('row_odd_colour', 'white')

    # include index col as part of plot
    indexname = '' if df.index.name is None else df.index.name
    colheaders = [indexname] + list(df.columns)
    headerfill = ['white' if x == '' else 'grey' for x in colheaders]


    cols = [df[x] for x in df.columns]
    # apply red/green to formatted_cols
    fcols = kwargs.get('formatted_cols', [])
    font_color = [['red' if str(y).startswith('-') else 'green' for y in df[x]] if x in fcols else 'black' for x in colheaders]

    if isinstance(df.index, pd.DatetimeIndex): # if index is datetime, format dates
        df.index = df.index.map(lambda x: x.strftime('%d-%m-%Y'), 1)
    cols.insert(0, df.index)

    fig = go.Figure(data=[go.Table(
        header=dict(values=colheaders, fill_color=headerfill, align='center', font=dict(color='white', size=12)),
        cells=dict(values=cols,
                   line= dict(color='#506784'),
                   fill_color= [[row_odd_color,row_even_colour]*len(df)],
                   align='right',
                   font_color=font_color,
            ))
    ])
    return fig


def forward_history_plot(df, title=None, **kwargs):
    """
     Given a dataframe of a curve's pricing history, plot a line chart showing how it has evolved over time
    """
    df = df.rename(columns={x: pd.to_datetime(x) for x in df.columns})
    df = df[sorted(list(df.columns), reverse=True)] # have latest column first
    df = df.rename(columns={x: cpu.format_date_col(x, '%d-%b') for x in df.columns}) # make nice labels for legend eg 05-Dec

    colseq = py.colors.sequential.Aggrnyl

    fig = go.Figure()
    colcount = 0
    for col in df.columns:
        color = colseq[colcount] if colcount < len(colseq) else colseq[-1]
        fig.add_trace(
            go.Scatter(x=df.index, y=df[col], hoverinfo='y', name=str(col), line=dict(color=color)))
        colcount = colcount + 1

    fig['data'][0]['line']['width'] = 2.2 # make latest line thicker
    legend = go.layout.Legend(font=dict(size=10))
    yaxis_title = kwargs.get('yaxis_title', None)
    fig.update_layout(title=title, xaxis_tickformat='%b-%y', yaxis_title=yaxis_title, legend=legend)
    return fig


def bar_line_plot(df, linecol='Total', **kwargs):
    """
    Give a dataframe, make a stacked bar chart along with overlaying line chart.
    """
    if linecol not in df:
        df[linecol] = df.sum(1, skipna=False)

    barcols = [x for x in df.columns if linecol not in x]
    barspecs = {'kind': 'bar', 'barmode': 'relative', 'title': 'd', 'columns': barcols}
    linespecs = {'kind': 'scatter', 'columns': linecol, 'color': 'black'}

    fig = cf.tools.figures(df, [barspecs, linespecs]) # returns dict
    fig = go.Figure(fig)
    yaxis_title = kwargs.get('yaxis_title', None)
    yaxis_range = kwargs.get('yaxis_range', None)
    title = kwargs.get('title', None)
    fig.update_layout(title=title, xaxis_title='Date', yaxis_title=yaxis_title)
    if yaxis_range is not None:
        fig.update_layout(yaxis=dict(range=yaxis_range))
    return fig


def reindex_year_line_plot(df, **kwargs):
    """
    Given a dataframe of timeseries, reindex years and produce line plot
    :param df:
    :return:
    """

    dft = transforms.reindex_year(df)
    dft = dft.tail(365 * 2) # normally 2 years is relevant for these type of charts
    colsel = cpu.reindex_year_df_rel_col(dft)
    inc_change_sum = kwargs.get('inc_change_sum', True)
    title = kwargs.get('title', '')
    if inc_change_sum:
        delta_summ = cpu.delta_summary_str(dft[colsel])
        title = '{}    {}: {}'.format(title, str(colsel).replace(title, ''), delta_summ)

    text = dft.index.strftime('%d-%b')
    fig = go.Figure()

    shaded_range = kwargs.get('shaded_range', None)
    if shaded_range is not None:
        add_shaded_range_traces(fig, dft, shaded_range)

    for col in dft.columns:
        width = 2.2 if col >= colsel else 1.2
        colyear = cpu.dates.find_year(dft)[col]
        visibile = cpu.line_visible(colyear)
        color = cpu.get_year_line_col(colyear)
        fig.add_trace(
            go.Scatter(x=dft.index, y=dft[col], hoverinfo='y', name=col, hovertemplate=hist_hover_temp, text=text,
                       visible=visibile, line=dict(color=color, width=width)))

    legend = go.layout.Legend(font=dict(size=10))
    yaxis_title = kwargs.get('yaxis_title', None)
    fig.update_layout(title=title, xaxis_tickformat='%b-%y', yaxis_title=yaxis_title, legend=legend)

    return fig

