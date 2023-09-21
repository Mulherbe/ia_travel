from flask import Flask, request, jsonify
from vosk import Model, KaldiRecognizer
import os
import json
import wave
import subprocess

app = Flask(__name__)
app.debug = True

# Chemin vers le modèle Vosk
MODEL_PATH = "vosk-model-fr-0.22"
if not os.path.exists(MODEL_PATH):
    raise ValueError(f"Le modèle n'a pas été trouvé à l'emplacement: {MODEL_PATH}")

model = Model(MODEL_PATH)

def convert_m4a_to_wav(m4a_path, wav_path):
    cmd = ['ffmpeg', '-i', m4a_path, wav_path]
    subprocess.run(cmd, check=True)

@app.route('/recognize', methods=['POST'])
def recognize():
    # Vérification de la présence d'un fichier
    if 'file' not in request.files:
        return jsonify({"error": "Aucun fichier reçu"}), 401

    file = request.files['file']

    # Sauvegarde temporaire du fichier
    file_path = "temp_audio.m4a"
    file.save(file_path)

    # Conversion du fichier m4a en wav
    converted_path = "temp_audio_converted.wav"
    convert_m4a_to_wav(file_path, converted_path)

    try:
        with wave.open(converted_path, "rb") as wave_file:
            framerate = wave_file.getframerate()
            print(f"Le taux d'échantillonnage du fichier est: {framerate}")
    except wave.Error:
        return jsonify({"error": "Le fichier fourni n'est pas un fichier WAV valide."}), 402

    # Initialisation du recognizer avec la fréquence d'échantillonnage du fichier
    recognizer = KaldiRecognizer(model, framerate)

    results = []
    with open(converted_path, "rb") as f:
        data = f.read(4000)
        while data:
            if recognizer.AcceptWaveform(data):
                results.append(json.loads(recognizer.Result()))
            data = f.read(4000)
    results.append(json.loads(recognizer.FinalResult()))
    print(results)

    # Suppression des fichiers temporaires
    os.remove(file_path)
    os.remove(converted_path)

    # Pour une meilleure représentation, vous pouvez concaténer tous les résultats en un seul texte
    full_text = " ".join([res["text"] for res in results])
    return jsonify({"text": full_text}), 200

@app.route('/test', methods=['GET'])
def test():
    return "test"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
