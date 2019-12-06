import plotly.graph_objects as go
from commodplot import commodplotutil
from commodutil import transforms
import cufflinks as cf

cf.go_offline()

hist_hover_temp = '<i>%{text}</i>: $%{y:.2f}'


"""
 Given a Dataframe produce a seasonal line plot (x-axis - Jan-Dec, y-axis Yearly lines)
 Can overlay a forward curve on top of this
"""
def seas_line_plot(df, fwd=None, title=None, yaxis_title=None, inc_change_sum=True):
    seas = transforms.seasonailse(df)
    seas = seas.fillna(method='ffill', limit=4) # fill in weekend, but only 4 to cover weekend/bank holidays

    fig = go.Figure()

    text = seas.index.strftime('%d-%b')
    for col in seas.columns:

        fig.add_trace(
            go.Scatter(x=seas.index, y=seas[col], hoverinfo='y', name=col, hovertemplate=hist_hover_temp, text=text,
                       line=dict(color=commodplotutil.get_year_line_col(col))))

    if title is None:
        title = ''
    if inc_change_sum:
        title = '{}   {}'.format(title, commodplotutil.delta_summary_str(df))

    if fwd is not None:
        fwdf = transforms.format_fwd(fwd, df.iloc[-1].name)
        fwdf = transforms.seasonailse(fwdf)

        for col in fwdf.columns:
            fig.add_trace(
                go.Scatter(x=fwdf.index, y=fwdf[col], hoverinfo='y', name=col, hovertemplate=hist_hover_temp, text=text,
                           line=dict(color=commodplotutil.get_year_line_col(col), dash='dot' )))

    fig.update_layout(title=title, xaxis_title='Date', yaxis_title=yaxis_title)

    return fig


"""
 Given a dataframe of a curve's pricing history, plot a line chart showing how it has evolved over time 
"""
def forward_history_plot(df, title=None):
    df = df.rename(columns={x:x.strftime('%d-%b') for x in df.columns}) # make nice labels for legend eg 05-Dec

    df = df[df.columns[::-1]] # reverse sort columns so newest curve is first (and hence darkest line)
    fig = df.iplot(title=title, colorscale='Blues')
    return fig


