"""
CS410 Mountain Group
UkrainianConflict Dashboard
"""

from datetime import date, timedelta

from dash import Dash, dcc, html, Input, Output, dash_table
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Global Variables
## For QA purposes, we will cut off date ranges to this set time period
START_DATE = date(2022, 11, 16)
END_DATE = date(2022, 12, 5)
TIME_DELTA = (END_DATE - START_DATE).days

CITIES = {
    "Kyiv": [50.449644, 30.519342],
    "Kharkiv": [49.988321, 36.233442],
    "Odesa": [46.460506, 30.731895],
    "Dnipro": [48.459777, 35.039044],
    "Donetsk": [47.986991, 37.788138],
    "Zaporizhzhia": [47.844157, 35.158049],
    "Lviv": [49.836399, 24.021443],
    "Kryvyi Rih": [47.904343, 33.410210],
    "Mykolaiv": [46.959381, 32.003766],
    "Sevastopol": [44.560571, 33.615098],
    "Mariupol": [47.106867, 37.562065],
    "Luhansk": [48.560943, 39.348395]
    }
CITIES = pd.DataFrame(CITIES).T.rename({0:"lat", 1:"lon"}, axis=1)

# App Dataframe Initializations
headlines = pd.read_csv("https://cs410-redis-sentiment-project.s3.us-west-2.amazonaws.com/UkrainianConflict-headlines-labeled.csv")
headlines['created_utc'] = pd.to_datetime(headlines['created_utc'])
headlines = headlines[(headlines['created_utc'] >= str(START_DATE)) & (headlines['created_utc'] <= str(END_DATE))]

comments = pd.read_csv("https://cs410-redis-sentiment-project.s3.us-west-2.amazonaws.com/UkrainianConflict-comments-labeled-updated.csv", lineterminator="\n")
comments['created_utc'] = pd.to_datetime(comments['created_utc'])
comments = comments[(comments['created_utc'] >= str(START_DATE)) & (comments['created_utc'] <= str(END_DATE))]

# Dash Server + App Config
app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP, './assets/custom.css'])
server = app.server

# Figures/functions that do not require any callbacks
def sizer(val: int) -> int:
    """
    Apply set sizes to chloroplath scatter given number of posts in day

    Notes:
        This function is used in conjunction with the callback for updating
        the 'cities' figure given the date of the slider

    Keyword Arguments:
        val (int): Number of posts per a city

    Returns:
        int: Corresponding size given value
    """

    ranges = [0, 1, 3, 5, 7, 10, 15, 20, 30, 40, 50, 75, 100, 150, 200]
    sizes = [10, 15, 20, 25, 30, 35, 40, 45, 50, 55, 60, 65, 70, 75, 80]

    for i, j in zip(ranges, sizes):
        if val <= i:
            return j

    return 0

def sentiment_over_time() -> go.Figure:
    """
    Track mean sentiment of headlines and comments over time

    Notes:
        Figure does not require any callbacks, so can be set explicitly
        as the figure argument

    Returns:
        go.Figure: Figure showing sentiment over time
    """

    fig = go.Figure()

    headlines_group = headlines.groupby(headlines['created_utc'])['compound'].mean()
    comments_group = comments.groupby(comments['created_utc'])['compound'].mean()

    fig.add_trace(go.Scatter(x=headlines_group.index,
                             y=headlines_group.values,
                             mode='lines+markers',
                             name='Headlines'))
    fig.add_trace(go.Scatter(x=comments_group.index,
                             y=comments_group.values,
                             mode='lines+markers',
                             name='Comments'))

    fig.update_xaxes(title_text="Dates")
    fig.update_yaxes(title_text="Net Composite Vader Score")
    fig.update_layout(
        hovermode='closest',
        margin=dict(l=10, r=10, t=10, b=10),
        yaxis_range=[-1, 1],
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1),
        template="plotly_white"
        )

    return fig


# HTML
title = dbc.Row([
    dbc.Row(
        html.H3("Sentiment Analysis on r/UkrainianConflict")
        ),
    dbc.Row(
        html.H4("Mountain Group")
        )],
    style={"textAlign": "center"})

overall_sentiment_analysis = dbc.Row([
    dbc.Row(
        html.H4("Overall Sentiment")
        ),
    dbc.Row([
        dbc.Col([
            dbc.Row(
                html.Div("Net Sentiment Over Time")
                ),
            dbc.Row(
                dcc.Graph(figure=sentiment_over_time()),
                style={"borderRight": "2px lightgray solid"})],
            width=6),
        dbc.Col([
            dbc.Row(
                html.Div("Sentiment by Top 10 Cities")
                ),
            dbc.Row(
                dcc.Graph(id='cities')
                ),
            dcc.Slider(min=0,
                       max=TIME_DELTA,
                       step=None,
                       id='slider',
                       marks={i:(START_DATE + timedelta(i)).strftime("%m/%d")
                              for i in range(TIME_DELTA+1)})],
            width=6),
        ])],
    style={"borderBottom": "2px lightgray solid", "marginBottom": "1%"})

sentiment_by_post = dbc.Row([
    dbc.Row(
        html.H4("Sentiment by Post")
        ),
    dbc.Row([
        dbc.Col([
            dbc.Row([
                dbc.Col(
                    html.Div("Top Post by Date")
                    ),
                dbc.Col(
                    dcc.DatePickerSingle(
                        id='post-date-filter',
                        month_format='MMM Do, YY',
                        placeholder='MMM Do, YY',
                        date=START_DATE
                        ),
                    style={"textAlign": "right"})
                ]),
            dbc.Row([
                dbc.Col(
                    dash_table.DataTable(
                        headlines.to_dict('records'),
                        [{"name": i, "id": i} for i in ['Headline', 'Upvotes', 'Downvotes']],
                        style_cell={
                            'overflow': 'hidden',
                            'textOverflow': 'ellipsis',
                            'maxWidth': 0,
                        },
                        style_cell_conditional=[
                            {'if': {'column_id': 'Headline'},
                             'width': '60%'},
                            {'if': {'column_id': 'Up Votes'},
                             'width': '20%'},
                            {'if': {'column_id': 'Down Votes'},
                             'width': '20%'},
                        ],
                    id="post-table"),
                    style={"borderRight": "2px lightgray solid"})
                ])
            ], width=3),
        dbc.Col([
            dbc.Col([
                dbc.Row(
                    html.Div("Thread Data")
                    ),
                dbc.Row([
                    dbc.Col(
                        html.Div("Sentiment by Upvoted Comments")
                        ),
                    dbc.Col(
                        dcc.RadioItems([{"label": "Compound", "value": "compound"},
                                        {"label": "Upvotes", "value": "ups"}],
                                        value="ups",
                                        id='comment-sort-by',
                                        inline=True),
                            style={'textAlign': 'right'})
                    ]),
                dbc.Row(
                    dcc.Graph(id="comment-barchart")
                    )
                ])],
            width=6),
        dbc.Col([
            dbc.Row(
                html.Div("Net Thread Sentiment")
                ),
            dbc.Row(
                dcc.Graph(id="comment-pie")
                )],
            width=3)
        ])
    ])

app.layout = html.Div([
    title,
    overall_sentiment_analysis,
    sentiment_by_post
    ], style={"marginLeft": "3%", "marginRight": "3%"})

# Dashboard Callbacks
@app.callback(
    Output('cities', 'figure'),
    Input('slider', 'value')
    )
def posts_by_top_cities(day: int) -> go.Figure:
    """
    Shows total number of post and mean sentiment through main cities of Ukraine

    Notes:
        Cities are cutoff to be the top 11 most populated cities to avoid
        oversaturating the visual with too many points. See CITIES global
        variable for all encapsulated cities

    Keyword Arguments:
        day (int): Day since beginning of data parsing

    Returns:
        go.Figure: Mapbox figure with scatter points showing number of post and sentiment
    """

    # If no day selected, will set day argument to None, therefore will just
    # default with 0th day
    day = 0 if day is None else day

    fig = go.Figure()

    cities_at_date = CITIES.copy()
    day = (START_DATE + timedelta(day)).strftime("%m/%d/%y")

    cities_at_date['count'] = headlines[headlines['created_utc'] == day]['city'].value_counts()
    cities_at_date['compound'] = headlines.compound.groupby(headlines['city']).mean()
    cities_at_date['size'] = cities_at_date['count'].apply(sizer)
    cities_at_date.fillna(0.0, inplace=True)

    for i, col in cities_at_date.iterrows():
        fig.add_trace(go.Scattermapbox(lat=[col['lat']],
                                       lon=[col['lon']],
                                       text=[i],
                                       mode='markers',
                                       showlegend=False,
                                       marker=go.scattermapbox.Marker(size=col['size'],
                                                                      cmax=0.25,
                                                                      cmin=-0.25,
                                                                      opacity=0.5,
                                                                      color=[col['compound']],
                                                                      colorscale="Bluered_r",
                                                                      colorbar=dict(thickness=20)),
                                       hovertemplate="<b>%{text}</b><br>Mean Sentiment: %{marker.color:,}<extra></extra>"))

    fig.update_layout(
        hovermode='closest',
        margin=dict(l=10, r=10, t=10, b=10),
        mapbox_style="open-street-map",
        mapbox=dict(
            center=go.layout.mapbox.Center(
                lat=49.289663,
                lon=32.821629
            ),
            zoom=4.75
        ))

    return fig

@app.callback(
   Output('post-table', 'data'),
   Input('post-date-filter', 'date')
    )
def headline_table_filter(day: str) -> list:
    """
    Filter Headline post table by date

    Notes:
        Output of dcc.SingleDatePicker is str, which can easily be used
        with pandas datetime filtering.
        Dashtable by default will have all entries in the object, callback
        will only send few back to show based on filter conditions

    Keyword Arguments:
        day (str): Date to filter headline posts

    Returns:
        list: Records of filtered headlines
    """

    headlines_at_date = headlines.copy()

    headlines_at_date = headlines_at_date[headlines_at_date['created_utc'] == day]
    headlines_at_date.sort_values('ups', ascending=False, inplace=True)
    headlines_at_date.drop_duplicates('id', inplace=True)
    headlines_at_date = headlines_at_date.iloc[0:10]
    headlines_at_date.rename({'ups': "Upvotes",
                              'downs': "Downvotes",
                              'headline': "Headline"},
                             axis=1,
                             inplace=True)

    headlines_at_date = headlines_at_date[['Headline', 'Upvotes', 'Downvotes']]

    return headlines_at_date.to_dict('records')

@app.callback(
    Output('comment-barchart', 'figure'),
    [Input('post-date-filter', 'date'),
     Input('comment-sort-by', 'value'),
     Input('post-table', 'active_cell')]
    )
def sentiment_by_comment(day: str, sort_by: str, headline: dict) -> go.Figure:
    """
    Show overall mean sentiment and upvotes associated with top comments

    Keyword Arguments:
        day (str): Date to filter comments
        sort_by (str): Argument to show which sort for comments
        headline (dict): Active cell showing which post selected

    Notes:
        Dashtable active cell does not return active cell value but rather
        table indices, therefore we need to recreate table from previous
        function and select from local object

    Returns:
        go.Figure: Figure showing comments by upvotes and mean sentiment
    """

    if headline is None:
        row, col = 0, 'id'
    else:
        row, col = headline['row'], 'id'

    fig = make_subplots(specs=[[{"secondary_y": True}]])

    headlines_at_date = headlines.copy()

    headlines_at_date = headlines_at_date[headlines_at_date['created_utc'] == day]
    headlines_at_date.sort_values('ups', ascending=False, inplace=True)
    headlines_at_date.drop_duplicates('id', inplace=True)
    headlines_at_date = headlines_at_date.iloc[0:10]

    post_id = headlines_at_date.iloc[row][col]

    comments_at_date = comments.copy()

    comments_at_date = comments_at_date[comments_at_date['created_utc'] == day]
    comments_at_date = comments_at_date[comments_at_date['link_id'].str.contains(post_id)]
    comments_at_date.sort_values(sort_by, ascending=False, inplace=True)
    # comments_at_date = comments_at_date.iloc[0:10]
    comments_at_date['headline_axis'] = comments_at_date['headline'].str.slice(0, 30)
    comments_at_date['headline_hover'] = comments_at_date['headline'].str.wrap(30)
    comments_at_date['headline_hover'] = comments_at_date['headline_hover'].apply(lambda x: x.replace('\n', '<br>'))

    if not len(comments_at_date): # No comments found
        comments_at_date = pd.DataFrame({"headline_axis": "No comments found",
                                         "headline_hover": "No comments found",
                                         "ups": 0,
                                         "compound": 0},
                                        index=[0])

    fig.add_trace(
        go.Bar(
            x=comments_at_date['headline_axis'],
            y=comments_at_date['ups'],
            hovertext=comments_at_date['headline_hover'],
            showlegend=False),
        secondary_y=False)

    fig.add_trace(
        go.Scatter(
            x=comments_at_date['headline_axis'],
            y=comments_at_date['compound'],
            mode="markers",
            showlegend=False),
        secondary_y=True)

    fig.update_yaxes(title_text="Upvotes", secondary_y=False)
    fig.update_yaxes(title_text="Net Composite Vader Score", secondary_y=True)
    fig.update_layout(template="plotly_white",
                      margin=dict(l=10, r=10, t=10, b=10),
                      xaxis_tickangle=-45)

    return fig

@app.callback(
    Output('comment-pie', 'figure'),
    [Input('post-date-filter', 'date'),
     Input('post-table', 'active_cell')]
    )
def net_comment_sentiment(day: str, headline: dict) -> go.Figure:
    """
    Display net sentiment and distribution of sentiment for comments of day

    Keyword Arguments:
        day (str): Date to filter comments
        headline (dict): Active cell showing which post selected

    Notes:
        Dashtable active cell does not return active cell value but rather
        table indices, therefore we need to recreate table from previous
        function and select from local object

    Returns:
        go.Figure: Pie Chart with sentiment distribution and mean sentiment
    """

    if headline is None:
        row, col = 0, 'id'
    else:
        row, col = headline['row'], 'id'

    fig = go.Figure()

    headlines_at_date = headlines.copy()

    headlines_at_date = headlines_at_date[headlines_at_date['created_utc'] == day]
    headlines_at_date.sort_values('ups', ascending=False, inplace=True)
    headlines_at_date.drop_duplicates('id', inplace=True)
    headlines_at_date = headlines_at_date.iloc[0:10]

    post_id = headlines_at_date.iloc[row][col]

    comments_at_date = comments.copy()

    comments_at_date = comments_at_date[comments_at_date['created_utc'] == day]
    comments_at_date = comments_at_date[comments_at_date['link_id'].str.contains(post_id)]
    if not len(comments_at_date):
        mean_sentiment = "N/A"
        sentiment_distribution = pd.Series(1, [1])
    else:
        mean_sentiment = round(comments_at_date['compound'].mean(), 3)
        sentiment_distribution = comments_at_date['label'].value_counts()
        sentiment_distribution.rename({-1: "Negative", 1: "Positive", 0: "Neutral"}, inplace=True)

    fig.add_trace(
        go.Pie(
            labels=sentiment_distribution.index,
            values=sentiment_distribution.values)
        )

    fig.update_traces(hole=.4, hoverinfo="label+percent+name")
    fig.update_layout(template="plotly_white",
                      margin=dict(l=10, r=10, t=10, b=10),
                      annotations=[dict(text=f"Mean Sentiment:<br>{mean_sentiment}",
                                        font_size=16,
                                        showarrow=False)])

    return fig

if __name__ == '__main__':
    app.run_server(debug=False)