import pandas as pd
import plotly.offline as pl
import plotly.graph_objects as go
from commodplot import commodplotutil as cpu
from commodutil import transforms
import cufflinks as cf

cf.go_offline()

hist_hover_temp = '<i>%{text}</i>: %{y:.2f}'


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

    if title is None:
        title = ''

    fig = go.Figure()

    if shaded_range is not None:
        r, rangeyr = cpu.min_max_range(seas, shaded_range)
        fig.add_trace(go.Scatter(x=r.index, y=r['max'].values, fill=None, name='%syr Max' % rangeyr, mode='lines',
                                 line_color='lightsteelblue', line_width=0.1))
        fig.add_trace(go.Scatter(x=r.index, y=r['min'].values, fill='tonexty', name='%syr Min' % rangeyr, mode='lines',
                                 line_color='lightsteelblue', line_width=0.1))

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

    # xaxis=go.layout.XAxis(title_font={"size": 10}), if making date label smaller
    legend = go.layout.Legend(font=dict(size=10))
    fig.update_layout(title=title,  xaxis_tickformat='%b', yaxis_title=yaxis_title, legend=legend)

    return fig


def seas_table(hist, fwd):
    hist = hist.resample('MS').mean()

    if fwd.index[0] == hist.index[-1]:
        hist = hist[:-1]

    df = pd.concat([hist, fwd], sort=False)
    df = transforms.seasonailse(df)

    summary = df.resample('Q').mean()
    winter = summary.iloc[[0, 3], :].mean()
    winter.name = 'Q1+Q4'
    summer = summary.iloc[[1, 2], :].mean()
    summer.name = 'Q2+Q3'
    summary.index = ['Q1', 'Q2', 'Q3', 'Q4']
    summary = summary.append(winter)
    summary = summary.append(summer)
    cal = df.resample('Y').mean().iloc[0]
    cal.name = 'Year'
    summary = summary.append(cal)
    summary = summary.round(2)

    df.index = df.index.strftime('%b')
    df = pd.concat([df, summary], sort=False).round(2)

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
    df = df.rename(columns={x:cpu.format_date_col(x, '%d-%b') for x in df.columns}) # make nice labels for legend eg 05-Dec
    # df = df[df.columns[::-1]] # reverse sort columns so newest curve is first (and hence darkest line)
    fig = df.iplot(title=title, colorscale='-Blues', asFigure=asFigure)
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


def reindex_year_line_plot(df, title=None, yaxis_title=None, inc_change_sum=True, asFigure=False):
    """
    Given a dataframe of timeseries, reindex years and produce line plot
    :param df:
    :return:
    """

    dft = transforms.reindex_year(df)
    dft = dft.tail(365 * 2) # normally 2 years is relevant for these type of charts
    if inc_change_sum:
        colsel = cpu.reindex_year_df_rel_col(dft)
        title = '{}    {}: {}'.format(title, str(colsel).replace(title, ''), cpu.delta_summary_str(dft[colsel]))

    fig = dft.iplot(color=cpu.std_yr_col(dft), title=title, yTitle=yaxis_title, asFigure=asFigure)
    return fig


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
