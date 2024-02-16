import React, { useState } from 'react';
import { Text, View, StyleSheet, TouchableOpacity, ActivityIndicator } from 'react-native';
import { Audio } from 'expo-av';
import axios from 'axios';

export default function Ask() {
  const [recording, setRecording] = useState();
  const [transcription, setTranscription] = useState("");
  const [apiTestResponse, setApiTestResponse] = useState('');

  async function startRecording() {
    try {
      console.log('Requesting permissions..');
      await Audio.requestPermissionsAsync();
      await Audio.setAudioModeAsync({
        allowsRecordingIOS: true,
        playsInSilentModeIOS: true,
      });

      console.log('Starting recording..');
      const { recording: newRecording } = await Audio.Recording.createAsync(
        Audio.RecordingOptionsPresets.HIGH_QUALITY
      );
      setRecording(newRecording);
      console.log('Recording started');
    } catch (err) {
      console.error('Failed to start recording', err);
    }
  }

  async function stopRecording() {
    console.log('Stopping recording..');
    setRecording(undefined);
    await recording.stopAndUnloadAsync();
    const uri = recording.getURI();
    console.log('Recording stopped and stored at', uri);
    sendAudioToAPI(uri);
  }

  async function sendAudioToAPI(uri) {
    try {
      const formData = new FormData();
      formData.append('file', {
        uri: uri,
        type: 'audio/wav',
        name: 'audio.wav',
      });
      const response = await axios.post('http://192.168.1.105:5001/recognize', formData);
      setTranscription(response.data.text);
      console.log(response);
    } catch (error) {
      console.error("Erreur lors de l'envoi de l'audio : ", error);
    }
  }
  
  const handleTestButtonClick = async () => {
    try {
      const response = await axios.get('http://192.168.1.105:5001/test');
      setApiTestResponse(response.data);
    } catch (error) {
      console.error("Erreur lors de la récupération de la réponse de l'API:", error);
      setApiTestResponse('Erreur lors de la récupération de la réponse de l\'API');
    }
  };

  return (
    <View style={styles.container}>
      <TouchableOpacity style={styles.button} onPress={recording ? stopRecording : startRecording}>
        <Text style={styles.buttonText}>{recording ? 'Stop Recording' : 'Start Recording'}</Text>
      </TouchableOpacity>
      <Text style={styles.transcriptionText}>Transcription : {transcription}</Text>
      <TouchableOpacity style={styles.button} onPress={handleTestButtonClick}>
        <Text style={styles.buttonText}>Tester l'API</Text>
      </TouchableOpacity>
      <Text style={styles.apiResponseText}>Réponse de l'API : {apiTestResponse}</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#121212', // Gris très foncé
    padding: 20,
  },
  button: {
    backgroundColor: '#0DB4D7', // Bleu néon
    padding: 10,
    borderRadius: 5,
    marginBottom: 20,
    alignItems: 'center',
    width: '80%',
  },
  buttonText: {
    color: '#FFFFFF', // Texte blanc
    fontSize: 18,
  },
  transcriptionText: {
    color: '#FFFFFF', // Texte blanc
    fontSize: 16,
    marginBottom: 10,
  },
  apiResponseText: {
    color: '#FFFFFF', // Texte blanc
    fontSize: 16,
  },
});
