import pandas as pd
import networkx as nx
import math

def haversine(lon1, lat1, lon2, lat2):
    R = 6371.0
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat / 2) * math.sin(dlat / 2) +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * 
         math.sin(dlon / 2) * math.sin(dlon / 2))
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    return R * c

df = pd.read_csv('liste-des-gares.csv', delimiter=';', encoding='utf-8')

# Tri des gares selon la ligne et le point kilométrique
df = df.sort_values(by=['CODE_LIGNE', 'PK'])

G = nx.Graph()

# Ajout des nœuds
for _, row in df.iterrows():
    G.add_node(row['CODE_UIC'], pos=(row['X_WGS84'], row['Y_WGS84']), label=row['LIBELLE'])

# Ajout des arêtes en fonction des gares consécutives sur la même ligne
for _, group in df.groupby('CODE_LIGNE'):
    previous_row = None
    for _, row in group.iterrows():
        if previous_row is not None:
            distance = haversine(previous_row['X_WGS84'], previous_row['Y_WGS84'], row['X_WGS84'], row['Y_WGS84'])
            G.add_edge(previous_row['CODE_UIC'], row['CODE_UIC'], weight=distance)
        previous_row = row

def find_shortest_path(start_label, end_label):
    start_uic = df[df['LIBELLE'] == start_label]['CODE_UIC'].values[0]
    end_uic = df[df['LIBELLE'] == end_label]['CODE_UIC'].values[0]

    path = nx.shortest_path(G, source=start_uic, target=end_uic, weight='weight')
    station_names = [df[df['CODE_UIC'] == uic]['LIBELLE'].values[0] for uic in path]

    return station_names

# Test avec deux noms de gares
start_station = "Nice-Ville"
end_station = "Verberie"
result = find_shortest_path(start_station, end_station)
print(" -> ".join(result))
