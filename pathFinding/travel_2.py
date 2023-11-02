import pandas as pd
import networkx as nx
import math

vitesses = pd.read_csv('vitesse-maximale-nominale-sur-ligne.csv')


def pk_to_km(pk_string):
    if not pk_string or any(c.isalpha() for c in pk_string):
        return 0.0
    if '+' in pk_string:
        main, fractional = pk_string.split('+')
        return float(main) + float(fractional) / 1000
    elif '-' in pk_string:
        main, fractional = pk_string.split('-')
        return float(main) - float(fractional) / 1000
    else:
        return float(pk_string)

vitesses['PKD'] = vitesses['PKD'].apply(pk_to_km)
vitesses['PKF'] = vitesses['PKF'].apply(pk_to_km)
def get_vitesse(pkd, pkf):
    troncon = vitesses[(vitesses['PKD'] <= pkd) & (vitesses['PKF'] >= pkf)]
    if not troncon.empty:
        return troncon['V_MAX'].values[0]
    else:
        return None

def get_temps(pkd, pkf):
    vitesse = get_vitesse(pkd, pkf)
    if vitesse:
        distance = pkf - pkd
        temps = distance / vitesse
        return temps  # temps en heures
    else:
        return None

def temps_total(trajet):
    total = 0
    for segment in trajet:
        temps = get_temps(segment['PKD'], segment['PKF'])
        if temps:
            total += temps
    return total

def compute_distance(row1, row2):
    if row1['CODE_LIGNE'] == row2['CODE_LIGNE']:
        return abs(pk_to_km(row1['PK']) - pk_to_km(row2['PK']))
    else:
        return haversine(row1['X_WGS84'], row1['Y_WGS84'], row2['X_WGS84'], row2['Y_WGS84'])

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
    G.add_node(row['CODE_UIC'], pos=(row['X_WGS84'], row['Y_WGS84']), label=row['LIBELLE'], line=row['CODE_LIGNE'], PK=row['PK'])

for _, group in df.groupby('CODE_LIGNE'):
    previous_row = None
    for _, row in group.iterrows():
        if previous_row is not None:
            distance = compute_distance(previous_row, row)
            G.add_edge(previous_row['CODE_UIC'], row['CODE_UIC'], weight=distance)
        previous_row = row

def find_shortest_path(start_uic, end_uic):
    try:
        path = nx.shortest_path(G, source=start_uic, target=end_uic, weight='weight')
    except nx.NetworkXNoPath:
        return None, [f"Pas de chemin trouvé entre {G.nodes[start_uic]['label']} et {G.nodes[end_uic]['label']}"], None, None

    stations_to_display = []
    lines_used = set()
    prev_line = None
    segments = []
    for i in range(len(path)-1):
        if 'PK' in G.nodes[path[i]] and 'PK' in G.nodes[path[i+1]]:
            segments.append({
                'PKD': pk_to_km(G.nodes[path[i]]['PK']),
                'PKF': pk_to_km(G.nodes[path[i+1]]['PK'])
            })
    
    for i, uic in enumerate(path):
        station_name = G.nodes[uic]['label']
        available_lines = df[df['CODE_UIC'] == uic]['CODE_LIGNE'].tolist()
        if i == 0 or prev_line not in available_lines:
            line_counts = {line: sum(1 for u in path if line in df[df['CODE_UIC'] == u]['CODE_LIGNE'].tolist()) for line in available_lines}
            line = max(line_counts, key=line_counts.get)
        else:
            line = prev_line
        if line != prev_line:
            lines_used.add(line)
            prev_line = line
        if i == 0:
            stations_to_display.append(f"{station_name}")
        else:
            stations_to_display.append(f"{station_name} (Ligne {line})")

    return path, stations_to_display, list(lines_used), segments

def find_best_path(start_label, end_label):
    start_uics = df[df['LIBELLE'] == start_label]['CODE_UIC'].tolist()
    end_uics = df[df['LIBELLE'] == end_label]['CODE_UIC'].tolist()

    best_path = None
    best_stations = None
    best_length = float('inf')
    best_segments = None

    for s_uic in start_uics:
        for e_uic in end_uics:
            result = find_shortest_path(s_uic, e_uic)
            if result[0] is None:
                continue

            path, message, stations, segments = result
            path_length = sum([G[path[i]][path[i+1]]['weight'] for i in range(len(path)-1)])
            if path_length < best_length:
                best_length = path_length
                best_path = message
                best_stations = stations
                best_segments = segments

    return best_path, best_stations , best_length, best_segments

def get_station_from_user(prompt):
    while True:
        print(prompt)
        user_input = input().strip()
        matches = df[df['LIBELLE'].str.contains(user_input, case=False, na=False)]

        if matches.empty:
            print("Aucune gare trouvée. Essayez à nouveau.")
            continue

        # Affichage des suggestions
        print("Veuillez choisir une gare parmi les suggestions suivantes :")
        for idx, (_, row) in enumerate(matches.iterrows(), start=1):
            print(f"{idx}. {row['LIBELLE']}")

        # Demander à l'utilisateur de choisir une gare
        try:
            selection = int(input("Entrez le numéro de la gare: "))
            if 1 <= selection <= len(matches):
                return matches.iloc[selection - 1]['LIBELLE']
            else:
                print("Numéro invalide. Essayez à nouveau.")
        except ValueError:
            print("Entrée invalide. Veuillez entrer un numéro.")

# Demander à l'utilisateur de saisir les gares de départ et d'arrivée
start_station = get_station_from_user("Gare de départ:")
end_station = get_station_from_user("Gare d'arrivé:")

# Calculer le meilleur chemin, la distance totale et le temps total
message, stations, total_distance, best_segments = find_best_path(start_station, end_station)
total_time = temps_total(best_segments)

# Afficher les résultats
print("\n".join(message))
print(f"Total Distance: {total_distance:.2f} km")
# print(f"Temps Total: {total_time:.2f} heures")
