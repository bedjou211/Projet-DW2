import dash
from dash import dcc, html
import plotly.express as px
import pandas as pd
import sqlite3
from dash.dependencies import Input, Output

conn = sqlite3.connect("nyc_taxi_data.db")
df_final = pd.read_sql("SELECT * FROM taxi_trips", conn)

df_final['pickup_date'] = pd.to_datetime(df_final['pickup_date'])

df_final['month_name'] = df_final['pickup_date'].dt.month_name()
df_final['day_of_week'] = df_final['pickup_date'].dt.day_name()  # Jour de la semaine
df_final['pickup_date_hour'] = df_final['pickup_date'].dt.floor('H')  # Arrondir à l'heure

df_aggregated = df_final.groupby('pickup_date_hour').agg(
    total_rides=('total_rides', 'sum'),
    total_tips=('total_tips', 'sum'),
    temp=('temp', 'mean')  
).reset_index()

df_aggregated['month_name'] = df_aggregated['pickup_date_hour'].dt.month_name()


# 1. Pourcentage des courses par jour de la semaine
df_day_of_week = df_final.groupby('day_of_week').agg(total_rides=('total_rides', 'sum')).reset_index()
df_day_of_week = df_day_of_week.set_index('day_of_week').reindex(['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'])

df_houre_of_day = df_final.groupby('pickup_hour').agg(total_rides=('total_rides', 'sum')).reset_index()
df_houre_of_day = df_houre_of_day.set_index('pickup_hour').reindex([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11,
                                                                        12, 13, 14,15,16,17,18,19,20,21,22,23])


app = dash.Dash(__name__)

# Graphique 1 : Nombre de courses par mois
fig_rides = px.line(df_aggregated, x='pickup_date_hour', y='total_rides', 
                    title="Nombre de courses par mois", 
                    labels={'pickup_date_hour': 'Date', 'total_rides': 'Nombre de Courses'})

# Graphique 2 : Total des pourboires par mois
fig_tips = px.bar(df_aggregated, x='pickup_date_hour', y='total_tips', 
                  title="Total des pourboires par mois", 
                  labels={'pickup_date_hour': 'Date', 'total_tips': 'Montant des Pourboires'})

# Graphique 3 : Température moyenne par mois
fig_temp = px.line(df_aggregated, x='pickup_date_hour', y='temp', 
                   title="Température moyenne par mois", 
                   labels={'pickup_date_hour': 'Date ', 'temp': 'Température (°C)'})

# Graphique 4 : Comparaison des courses et des pourboires
fig_comparison = px.scatter(df_aggregated, x='total_rides', y='total_tips', color='month_name', 
                            title="Relation entre Nombre de Courses et Pourboires",
                            labels={'total_rides': 'Nombre de Courses', 'total_tips': 'Montant des Pourboires'})

# Graphique 5 : Relation entre la température et le nombre de courses
fig_temp_rides = px.scatter(df_aggregated, x='temp', y='total_rides', 
                            title="Relation entre Température et Nombre de Courses",
                            labels={'temp': 'Température (°C)', 'total_rides': 'Nombre de Courses'})

# Graphique 6 : Pourcentage des courses par jour de la semaine (Graphique circulaire)
fig_day_of_week = px.pie(df_day_of_week, names=df_day_of_week.index, values='total_rides', 
                         title="Répartition des courses par jour de la semaine")

# Graphique 7 : Répartition des moyens de paiement
# Pour le moment, nous simulons cette répartition avec des données fictives
payment_data = {'payment_type': ['Carte', 'Espèces', 'Autres'], 'total_rides': [5000, 3500, 1500]}
df_payment_type = pd.DataFrame(payment_data)
fig_payment_type = px.pie(df_payment_type, names='payment_type', values='total_rides', 
                          title="Répartition des moyens de paiement")

# Graphique 8 : Pourcentage des courses par heure (Graphique circulaire)
fig_houre_of_week = px.pie(df_houre_of_day, names=df_houre_of_day.index, values='total_rides', 
                         title="Répartition des courses par heure")

app.layout = html.Div([
    html.H1("Analyse des Données des Courses de Taxi à New York", style={'textAlign': 'center'}),
    
    html.Div([
        dcc.Dropdown(
            id='month-dropdown',
            options=[{'label': month, 'value': month} for month in df_aggregated['month_name'].unique()],
            value=None,  # Valeur initiale vide (pas de filtre)
            placeholder="Sélectionnez un mois",
            style={'width': '50%'}
        ),
    ], style={'padding': '10px'}),
    
    html.Div([
        html.Div([
            html.H3("Nombre de courses par mois"),
            dcc.Graph(id='rides-graph', figure=fig_rides)
        ], className='six columns'),
        
        html.Div([
            html.H3("Total des pourboires par mois"),
            dcc.Graph(id='tips-graph', figure=fig_tips)
        ], className='six columns'),
    ], className='row'),

    html.Div([
        html.Div([
            html.H3("Température moyenne par mois"),
            dcc.Graph(id='temp-graph', figure=fig_temp)
        ], className='six columns'),
        
        html.Div([
            html.H3("Relation entre Nombre de Courses et Pourboires"),
            dcc.Graph(id='comparison-graph', figure=fig_comparison)
        ], className='six columns'),
    ], className='row'),

    html.Div([
        html.Div([
            html.H3("Relation entre Température et Nombre de Courses"),
            dcc.Graph(id='temp-rides-graph', figure=fig_temp_rides)
        ], className='six columns'),
    ], className='row'),

    html.Div([
        html.Div([
            html.H3("Répartition des Courses par Jour de la Semaine"),
            dcc.Graph(id='day-of-week-graph', figure=fig_day_of_week)
        ], className='six columns'),

        html.Div([
            html.H3("Répartition des Moyens de Paiement"),
            dcc.Graph(id='payment-type-graph', figure=fig_payment_type)
        ], className='six columns'),
        html.Div([
            html.H3("Répartition des Courses par heure"),
            dcc.Graph(id='houre-of-week-graph', figure=fig_houre_of_week)
        ], className='six columns')
    ], className='row'),
])

@app.callback(
    [Output('rides-graph', 'figure'),
     Output('tips-graph', 'figure'),
     Output('temp-graph', 'figure'),
     Output('comparison-graph', 'figure'),
     Output('temp-rides-graph', 'figure'),
     Output('day-of-week-graph', 'figure'),
     Output('payment-type-graph', 'figure'),
     Output('houre-of-week-graph', 'figure'),
     Output('month-dropdown', 'value')],  
    [Input('month-dropdown', 'value')]
)
def update_graphs(selected_month):
    if selected_month:
        df_filtered = df_aggregated[df_aggregated['month_name'] == selected_month]
        df_day_of_week_filtered = df_final[df_final['month_name'] == selected_month].groupby('day_of_week').agg(total_rides=('total_rides', 'sum')).reset_index()
        df_day_of_week_filtered = df_day_of_week_filtered.set_index('day_of_week').reindex(['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'])

        df_houre_of_day_filtred = df_final.groupby('pickup_hour').agg(total_rides=('total_rides', 'sum')).reset_index()
        df_houre_of_day_filtred = df_houre_of_day_filtred.set_index('pickup_hour').reindex([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11,
                                                                        12, 13, 14,15,16,17,18,19,20,21,22,23])
    

    else:
        df_filtered = df_aggregated  
        df_day_of_week_filtered = df_day_of_week
        df_houre_of_day_filtred = df_houre_of_day

    # Mettre à jour les graphiques
    fig_rides = px.line(df_filtered, x='pickup_date_hour', y='total_rides', 
                        title="Nombre de courses par mois", 
                        labels={'pickup_date_hour': 'Date', 'total_rides': 'Nombre de Courses'})
    
    fig_tips = px.bar(df_filtered, x='pickup_date_hour', y='total_tips', 
                      title="Total des pourboires par mois", 
                      labels={'pickup_date_hour': 'Date et Heure', 'total_tips': 'Montant des Pourboires'})
    
    fig_temp = px.line(df_filtered, x='pickup_date_hour', y='temp', 
                       title="Température moyenne par mois", 
                       labels={'pickup_date_hour': 'Date ', 'temp': 'Température (°C)'})
    
    fig_comparison = px.scatter(df_filtered, x='total_rides', y='total_tips', color='month_name', 
                                title="Relation entre Nombre de Courses et Pourboires",
                                labels={'total_rides': 'Nombre de Courses', 'total_tips': 'Montant des Pourboires'})
    
    fig_temp_rides = px.scatter(df_filtered, x='temp', y='total_rides', 
                                title="Relation entre Température et Nombre de Courses",
                                labels={'temp': 'Température (°C)', 'total_rides': 'Nombre de Courses'})
    
    fig_day_of_week = px.pie(df_day_of_week_filtered, names=df_day_of_week_filtered.index, values='total_rides', 
                             title="Répartition des courses par jour de la semaine")
    
    fig_houre_of_week = px.pie(df_houre_of_day_filtred, names=df_houre_of_day_filtred.index, values='total_rides', 
                             title="Répartition des courses par heure")
    
    fig_payment_type = px.pie(df_payment_type, names='payment_type', values='total_rides', 
                              title="Répartition des moyens de paiement")
    
    return fig_rides, fig_tips, fig_temp, fig_comparison, fig_temp_rides, fig_day_of_week, fig_payment_type, fig_houre_of_week,selected_month

if __name__ == '__main__':
    app.run_server(debug=True)