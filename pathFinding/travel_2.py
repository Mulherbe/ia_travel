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
df = df.sort_values(by=['CODE_LIGNE', 'PK'])

G = nx.Graph()

for _, row in df.iterrows():
    G.add_node(row['CODE_UIC'], pos=(row['X_WGS84'], row['Y_WGS84']), label=row['LIBELLE'], line=row['CODE_LIGNE'])

for _, group in df.groupby('CODE_LIGNE'):
    previous_row = None
    for _, row in group.iterrows():
        if previous_row is not None:
            distance = haversine(previous_row['X_WGS84'], previous_row['Y_WGS84'], row['X_WGS84'], row['Y_WGS84'])
            G.add_edge(previous_row['CODE_UIC'], row['CODE_UIC'], weight=distance)
        previous_row = row

def find_shortest_path(start_uic, end_uic):
    try:
        path = nx.shortest_path(G, source=start_uic, target=end_uic, weight='weight')
    except nx.NetworkXNoPath:
        return None, [f"Pas de chemin trouvé entre {G.nodes[start_uic]['label']} et {G.nodes[end_uic]['label']}"], None

    stations_to_display = []
    lines_used = set()
    prev_line = None

    for i, uic in enumerate(path):
        station_name = G.nodes[uic]['label']
        available_lines = df[df['CODE_UIC'] == uic]['CODE_LIGNE'].tolist()

        # Si on est à la première station ou si la ligne précédente ne dessert pas la station actuelle
        if i == 0 or prev_line not in available_lines:
            # Choisir la ligne avec le plus grand nombre de stations communes sur le chemin
            line_counts = {line: sum(1 for u in path if line in df[df['CODE_UIC'] == u]['CODE_LIGNE'].tolist()) for line in available_lines}
            line = max(line_counts, key=line_counts.get)
        else:
            line = prev_line  # utiliser la ligne précédente

        # Si la ligne a changé par rapport à la précédente, l'ajouter à la liste des lignes utilisées
        if line != prev_line:
            lines_used.add(line)
            prev_line = line

        # Ajouter la station et la ligne à la liste des stations à afficher
        if i == 0:
            stations_to_display.append(f"{station_name}")
        else:
            stations_to_display.append(f"{station_name} (Ligne {line})")

    return path, stations_to_display, list(lines_used)

# ... [Reste du code]

def find_best_path(start_label, end_label):
    start_uics = df[df['LIBELLE'] == start_label]['CODE_UIC'].tolist()
    end_uics = df[df['LIBELLE'] == end_label]['CODE_UIC'].tolist()

    best_path = None
    best_stations = None
    best_length = float('inf')
    
    for s_uic in start_uics:
        for e_uic in end_uics:
            result = find_shortest_path(s_uic, e_uic)
            
            if result[0] is None:
                continue
            
            path, message, stations = result
            path_length = sum([G[path[i]][path[i+1]]['weight'] for i in range(len(path)-1)])
            
            if path_length < best_length:
                best_length = path_length
                best_path = message
                best_stations = stations
    
    return best_path, best_stations

# start_station = "Paris-Gare-de-Lyon-Souterrain"
# end_station = "Nice-Ville"
# message, stations = find_best_path(start_station, end_station)
# print(message)
start_station = "Paris-Gare-de-Lyon-Souterrain"
end_station = "Nice-Ville"
message, stations = find_best_path(start_station, end_station)
print(message)

prev_line = None

for station in stations:
    if isinstance(station, str):
        station_name, line = station.split(" (Ligne ")
        
        if line != prev_line:
            print(f"{station_name} (Ligne {line})")
            prev_line = line
        else:
            print(station_name)
    else:
        print(station)


# for station in stations:
#     print(f"{station} : {type(station)}")
# print(" -> ".join(stations))
