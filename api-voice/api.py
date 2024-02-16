#!/usr/bin/env python3

from flask import Flask, request, jsonify
import os
import json
import wave
import subprocess
import requests  
import pandas as pd
import networkx as nx
import math
from travel_2 import find_best_path, temps_total

# from pydub import AudioSegment

from os import path
import speech_recognition as sr

app = Flask(__name__)
app.debug = True
vitesses = pd.read_csv('vitesse-maximale-nominale-sur-ligne.csv')
df = pd.read_csv('liste-des-gares.csv', delimiter=';', encoding='utf-8')

@app.route('/recognize', methods=['POST'])
def recognize():
    if 'file' not in request.files:
        return jsonify({"error": "Aucun fichier reçu"}), 401

    file = request.files['file']

    # Sauvegarde temporaire du fichier
    # file_path = "temp1.mp3"
    m4a_file = "./recording.m4a"
    file.save(m4a_file)

    # m4a_file = "./temp_0202_4.m4a"

    wav_file = "./recording.wav"

    # if path.exists(m4a_file):
    #     audio = AudioSegment.from_file(m4a_file, format="m4a")

    #     audio.export(wav_file, format="wav")

    #     AUDIO_FILE1 = wav_file
    # else:
    #     print("The input M4A file does not exist.")

    r = sr.Recognizer()
    with sr.AudioFile(m4a_file) as source:
        audio1 = r.record(source)

    try:
        answer = r.recognize_google(audio1, language='fr-FR')
        print("you said: " + answer)
    except sr.UnknownValueError:
        print("Google Speech Recognition could not understand audio")
    except sr.RequestError as e:
        print("Could not request results from Google Speech Recognition service; {0}".format(e))
    return answer

@app.route('/testo', methods=['GET'])
def testo():
    data = request.json
    start_station = 'Bouchain'
    end_station = 'Paris-St-Lazare'
    
    if not start_station or not end_station:
        return jsonify({"error": "Les champs 'depart' et 'arrivee' sont requis."}), 400

    # Utilisation des fonctions de travel_2.py pour trouver le meilleur chemin
    best_path, best_stations, best_length, best_segments = find_best_path(start_station, end_station)
    if best_path is None:
        return jsonify({"error": "Aucun chemin trouvé."}), 404

    total_time = temps_total(best_segments)

    return jsonify({
        "path": best_stations,
        "total_distance": best_length,
        "total_time": total_time
    })

@app.route('/text', methods=['POST'])
def text():
    # Extrait le texte de la requête entrante, si nécessaire
    data = request.json
    text_input = data.get('text')

    # URL de l'API du modèle d'IA
    model_api_url = 'http://192.168.1.105:1234/v1/chat/completions'

    # Prépare les données à envoyer à l'API du modèle d'IA
    model_payload = {
        "model": "local-model",
        "messages": [{"role": "system", "content": "Votre prompt ici avec " + text_input}],
        "temperature": 0.7,
    }

    # Fait l'appel à l'API du modèle d'IA
    response = requests.post(model_api_url, json=model_payload)

    # Vérifie si l'appel à l'API a réussi
    if response.status_code == 200:
        # Retourne la réponse de l'API du modèle d'IA
        return jsonify(response.json())
    else:
        # Retourne un message d'erreur si l'appel à l'API échoue
        return jsonify({"error": "Failed to get response from the model API"}), 500

@app.route('/clear', methods=['GET'])
def clear():
    return ""

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
