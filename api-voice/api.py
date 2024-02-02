#!/usr/bin/env python3

from flask import Flask, request, jsonify
import os
import json
import wave
import subprocess
from pydub import AudioSegment

from os import path
import speech_recognition as sr

app = Flask(__name__)
app.debug = True

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

    if path.exists(m4a_file):
        audio = AudioSegment.from_file(m4a_file, format="m4a")

        audio.export(wav_file, format="wav")

        AUDIO_FILE1 = wav_file
    else:
        print("The input M4A file does not exist.")

    r = sr.Recognizer()
    with sr.AudioFile(AUDIO_FILE1) as source:
        audio1 = r.record(source)

    try:
        answer = r.recognize_google(audio1, language='fr-FR')
        print("you said: " + answer)
    except sr.UnknownValueError:
        print("Google Speech Recognition could not understand audio")
    except sr.RequestError as e:
        print("Could not request results from Google Speech Recognition service; {0}".format(e))
    return answer

@app.route('/test', methods=['GET'])
def test():
    return "test"

@app.route('/clear', methods=['GET'])
def clear():
    return ""

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
