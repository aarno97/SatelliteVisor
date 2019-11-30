import math
import numpy as np
import plotly.graph_objects as go
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import mysql.connector


# Get access to the database
mydb = mysql.connector.connect(
     host="localhost",
    user="root",
    passwd="Q.E.D.",
    database="satellite"
)

# Query the database with the sql string and return the result
def query(sql):

    mycursor = mydb.cursor()

    mycursor.execute(sql)

    result = mycursor.fetchall()

    return result

# Return the y value of ellipse equation in 2-D plane 
# int x int  x  int  ->  int
def ellipse_equation(apogee,perigee,x):
    # y = sqrt of  (1- x^2 / a^2) * b^2
    return math.sqrt((1 - (x**2)/(apogee ** 2))*(perigee ** 2))

# Vectorize the first ellipse equation function
v_ellipse_equation= np.vectorize(ellipse_equation, excluded = ['apogee, perigee'])

# Retrieve results from query function
results = query("SELECT Apogee_km, Perigee_km FROM orbit_table LIMIT 5")



def plot_ellipsis(results,fig):

    for r in results:

        # Random points along the x axis
        t_1 = np.linspace(-r[0],r[0],500)

        # More random points along the x axis
        t_2 = np.linspace(-r[0],r[0],500)

        #Concatenate and compine x values
        t = np.concatenate([t_1,t_2])

        # Get corresponding y values
        y = v_ellipse_equation(r[0], r[1], t_1)

        # Other value of sqrt
        new_vals = [-x for x in y]

        # Combine y and old values
        y = np.concatenate([y,new_vals])

        fig.add_trace(go.Scatter(x = t, y = y, mode='lines'))


fig = go.Figure()

plot_ellipsis(results,fig)

app = dash.Dash()

app.layout = html.Div(children = [
    html.H1("Databases Project"),
    html.Div(dcc.Dropdown(

    id = 'orbit-selector',

    options=[

        {'label': 'LEO', 'value': 'LEO'},
        {'label': 'GEO', 'value': 'GEO'}
    ],

    multi=True,
    value="MTL")),

    dcc.Graph(
        id = 'satellites'
        
             
    )])

@app.callback(
    Output('satellites', 'figure'),
    [Input('orbit-selector', 'value')])
def update_graph(orbit):
    fig = go.Figure()
    orbit = str(orbit).strip('[]')
    graph_query = 'SELECT Apogee_km, Perigee_km, Class_of_Orbit FROM orbit_table WHERE Class_of_Orbit = {} LIMIT 5'.format(orbit)
    print(graph_query)
    results = query(graph_query)
    plot_ellipsis(results,fig)
    return fig

if __name__ == '__main__':
    app.run_server(debug=True)
