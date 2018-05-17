import os
import datetime
import numpy as np
import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
from pandas.io import gbq
import plotly as py
import plotly.graph_objs as go

# Imports the Google Cloud client library
from google.cloud import bigquery
import calendar

#query = (
#    'SELECT lsoa_code, borough, major_category, minor_category, value, year, month '
#    ' FROM `bigquery-public-data.london_crime.crime_by_lsoa` '
#    ' WHERE year = 2016 '
#    'LIMIT 1000')

query = (
    'SELECT borough, month, sum(value) as value'
    ' FROM `bigquery-public-data.london_crime.crime_by_lsoa` '
    ' WHERE year = 2016 ' 
    ' GROUP BY borough, month'
)

# client = bigquery.Client()
# query_job = client.query(
#    query
#)

# Explicitly use service account credentials by specifying the private
# key file. All clients in google-cloud-python have this helper.
# client = bigquery.Client.from_service_account_json(os.environ['GOOGLE_APPLICATION_CREDENTIALS'])

# df = gbq.read_gbq(query, project_id="gcp-application-development", dialect="standard", private_key=os.environ['GOOGLE_APPLICATION_CREDENTIALS'] )
df = gbq.read_gbq(query, project_id="plotly-london-crime", dialect="standard")
boroughs = df.borough.unique()
months = sorted(df.month.unique())
#print("boroughs: {0}".format(boroughs))
#print("months: {0}".format(months))

values = []
avg_values = []
for b in boroughs:
    print("borough: {0}".format(b))
    values_row = []
    for m in months:
        #print("month: {0}".format(m))
        v = df.loc[(df['borough'] == b) & (df['month'] == m)].value
        #print("v: {0}".format(v))
        values_row.append(v.values[0])
    values.append(values_row)
    avg_values.append(sum(values_row)/len(values_row))

print(avg_values)
# Sort boroughs by avg values
boroughs = [x for _,x in sorted(zip(avg_values,boroughs))]
values = [x for _,x in sorted(zip(avg_values,values))]
#print("values: {0}".format(values))

#for row in query_job: # API request - fetches results
    # Row values can be accessed by field name or index
    #assert row[0] == row.name == row['name']
#    print(row)
app = dash.Dash()

months = [calendar.month_name[x] for x in months]

data = [
    go.Heatmap(
        x=months,
        y=boroughs,
        z=values,
        colorscale='Viridis',
    )
]

layout = go.Layout(
    title='London Crime Hotspots in 2016 (BigQuery free dataset)',
    xaxis= dict(
            title="Month",
            automargin=True
    ),
    yaxis= dict(
            title="Borough",
            automargin=True
    )

)

fig = go.Figure(data=data, layout=layout)
app.layout = html.Div([
    dcc.Graph(
        id="heatmap",
        figure=fig
    )
])

if __name__ == '__main__':
    app.run_server()
