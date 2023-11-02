import pandas as pd
import networkx as nx
import math
import matplotlib.pyplot as plt

def haversine(lon1, lat1, lon2, lat2):
    R = 6371.0
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat / 2) * math.sin(dlat / 2) +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * 
         math.sin(dlon / 2) * math.sin(dlon / 2))
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    return R * c

# Charger les données des gares depuis un fichier CSV
df = pd.read_csv('liste-des-gares.csv', delimiter=';', encoding='utf-8')
df = df.sort_values(by=['CODE_LIGNE', 'PK'])

# Créer un graphe NetworkX
G = nx.Graph()

# Ajouter les nœuds correspondant aux gares au graphe
for _, row in df.iterrows():
    G.add_node(row['CODE_UIC'], pos=(row['X_WGS84'], row['Y_WGS84']), label=row['LIBELLE'], line=row['CODE_LIGNE'])

# Ajouter des arêtes entre les gares connectées
for _, group in df.groupby('CODE_LIGNE'):
    previous_row = None
    for _, row in group.iterrows():
        if previous_row is not None:
            distance = haversine(previous_row['X_WGS84'], previous_row['Y_WGS84'], row['X_WGS84'], row['Y_WGS84'])
            G.add_edge(previous_row['CODE_UIC'], row['CODE_UIC'], weight=distance)
        previous_row = row

# Créer un dictionnaire de positions des gares à partir des attributs de nœuds
node_positions = {node: data['pos'] for node, data in G.nodes(data=True)}

# Dessiner le graphe NetworkX avec les gares et leurs liaisons
plt.figure(figsize=(12, 12))
nx.draw_networkx_nodes(G, pos=node_positions, node_size=10, node_color='b')
nx.draw_networkx_edges(G, pos=node_positions, alpha=0.5)
plt.axis('off')
plt.title('Carte des Gares de France')
plt.show()