import pandas as pd
import plotly.offline as pl
import plotly.graph_objects as go
from commodplot import commodplotutil as cpu
from commodutil import transforms
import cufflinks as cf

cf.go_offline()

hist_hover_temp = '<i>%{text}</i>: %{y:.2f}'


def shaded_range_traces(seas, shaded_range):
    r, rangeyr = cpu.min_max_range(seas, shaded_range)
    max_trace = go.Scatter(x=r.index, y=r['max'].values, fill=None, name='%syr Max' % rangeyr, mode='lines',
                             line_color='lightsteelblue', line_width=0.1)
    min_trace = go.Scatter(x=r.index, y=r['min'].values, fill='tonexty', name='%syr Min' % rangeyr, mode='lines',
                             line_color='lightsteelblue', line_width=0.1)
    return max_trace, min_trace


def seas_line_plot(df, fwd=None, title=None, yaxis_title=None, inc_change_sum=True, histfreq=None, shaded_range=None):
    """
     Given a DataFrame produce a seasonal line plot (x-axis - Jan-Dec, y-axis Yearly lines)
     Can overlay a forward curve on top of this
    """
    if isinstance(df, pd.Series):
        df = pd.DataFrame(df)

    if histfreq is None:
        histfreq = pd.infer_freq(df.index)
        if histfreq is None:
            histfreq = 'D' # sometimes infer_freq returns null - assume mostly will be a daily series
    seas = transforms.seasonailse(df)

    text = seas.index.strftime('%b')
    if histfreq in ['B', 'D']:
        text = seas.index.strftime('%d-%b')
    if histfreq.startswith('W'):
        text = seas.index.strftime('%d-%b')

    fig = go.Figure()

    if shaded_range is not None:
        maxtrace, mintrace = shaded_range_traces(seas, shaded_range)
        fig.add_trace(maxtrace)
        fig.add_trace(mintrace)

    for col in seas.columns:
        fig.add_trace(
            go.Scatter(x=seas.index, y=seas[col], hoverinfo='y', name=col, hovertemplate=hist_hover_temp, text=text,
                       visible=cpu.line_visible(col), line=dict(color=cpu.get_year_line_col(col), width=cpu.get_year_line_width(col))))

    if title is None:
        title = ''
    if inc_change_sum:
        title = '{}   {}'.format(title, cpu.delta_summary_str(df))

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
    fig.layout.xaxis.tickvals = pd.date_range(seas.index[0], seas.index[-1], freq='MS')
    fig.update_layout(title=title,  xaxis_tickformat='%b', yaxis_title=yaxis_title, legend=legend)

    return fig


def seas_box_plot(hist, fwd=None, title=''):
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
    fig.update_layout(title=title)

    return fig


def seas_table_plot(hist, fwd):
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


def forward_history_plot(df, title=None, asFigure=False):
    """
     Given a dataframe of a curve's pricing history, plot a line chart showing how it has evolved over time
    """
    df = df.rename(columns={x: pd.to_datetime(x) for x in df.columns})
    df = df[sorted(list(df.columns), reverse=True)] # have latest column first
    df = df.rename(columns={x:cpu.format_date_col(x, '%d-%b') for x in df.columns}) # make nice labels for legend eg 05-Dec

    fig = df.iplot(title=title, colorscale='-Blues', asFigure=asFigure)
    fig['data'][0]['line']['width'] = 2.2 # make latest line thicker
    return fig


def bar_line_plot(df, linecol='Total', title=None, yaxis_title=None, yaxis_range=None):
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
    fig.update_layout(title=title, xaxis_title='Date', yaxis_title=yaxis_title)
    if yaxis_range is not None:
        fig.update_layout(yaxis=dict(range=yaxis_range))
    return fig


def reindex_year_line_plot(df, title='', yaxis_title=None, inc_change_sum=True, shaded_range=None):
    """
    Given a dataframe of timeseries, reindex years and produce line plot
    :param df:
    :return:
    """

    dft = transforms.reindex_year(df)
    dft = dft.tail(365 * 2) # normally 2 years is relevant for these type of charts
    colsel = cpu.reindex_year_df_rel_col(dft)
    if inc_change_sum:
        delta_summ = cpu.delta_summary_str(dft[colsel])
        title = '{}    {}: {}'.format(title, str(colsel).replace(title, ''), delta_summ)

    text = dft.index.strftime('%d-%b')
    fig = go.Figure()

    if shaded_range is not None:
        maxtrace, mintrace = shaded_range_traces(dft, shaded_range)
        fig.add_trace(maxtrace)
        fig.add_trace(mintrace)

    for col in dft.columns:
        width = 2.2 if col == colsel else 1.2
        colyear = cpu.dates.find_year(dft)[col]
        visibile = cpu.line_visible(colyear)
        color = cpu.get_year_line_col(colyear)
        fig.add_trace(
            go.Scatter(x=dft.index, y=dft[col], hoverinfo='y', name=col, hovertemplate=hist_hover_temp, text=text,
                       visible=visibile, line=dict(color=color, width=width)))

    legend = go.layout.Legend(font=dict(size=10))
    fig.update_layout(title=title, xaxis_tickformat='%b-%y', yaxis_title=yaxis_title, legend=legend)

    return fig


# TODO remove once transitioned over legacy code
# Moved to commodplotutil
def plhtml(fig, margin=cpu.narrow_margin, **kwargs):
    """
    Given a plotly figure, return it as a div
    """
    # if 'margin' in kwargs:
    if fig is not None:
        fig.update_layout(margin=margin)

        fig.update_xaxes(automargin=True)
        fig.update_yaxes(automargin=True)
        return pl.plot(fig, include_plotlyjs=False, output_type='div')

    return ''


