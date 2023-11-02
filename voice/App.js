import React, { useState } from 'react';
import { Text, View, StyleSheet, Button } from 'react-native';
import { Audio } from 'expo-av';
import axios from 'axios';

export default function App() {
  const [recording, setRecording] = useState();
  const [transcription, setTranscription] = useState("");
  const [apiTestResponse, setApiTestResponse] = useState('');  // Ajout pour stocker la réponse du test

  async function startRecording() {
    try {
      console.log('Requesting permissions..');
      await Audio.requestPermissionsAsync();
      await Audio.setAudioModeAsync({
        allowsRecordingIOS: true,
        playsInSilentModeIOS: true,
      });

      console.log('Starting recording..');
      const { recording: newRecording } = await Audio.Recording.createAsync(Audio.RecordingOptionsPresets.HIGH_QUALITY);
      setRecording(newRecording);
      console.log('Recording started');
    } catch (err) {
      console.error('Failed to start recording', err);
    }
  }

  async function sendAudioToAPI(uri) {
    try {
      const formData = new FormData();
      formData.append('file', {
        uri: uri,
        type: 'audio/wav',
        name: 'audio.wav',
      });
      const response = await axios.post('http://10.73.189.154:5000/recognize', formData);
      setTranscription(response.data.text);
      console.log(response.data.text)
    } catch (error) {
      console.error("Erreur lors de l'envoi de l'audio : ", error);
    }
  }
  const handleTestButtonClick = async () => {  // Fonction ajoutée pour tester l'API
    try {
      const response = await axios.get('http://10.73.189.154:5000/test');
      setApiTestResponse(response.data);
    } catch (error) {
      console.error("Erreur lors de la récupération de la réponse de l'API:", error);
      setApiTestResponse('Erreur lors de la récupération de la réponse de l\'API');
    }
  };
  async function stopRecording() {
    console.log('Stopping recording..');
    setRecording(undefined);
    await recording.stopAndUnloadAsync();
    const uri = recording.getURI();
    console.log('Recording stopped and stored at', uri);

    // Envoyer l'audio à l'API pour transcription
    sendAudioToAPI(uri);
  }

  return (
    <View style={styles.container}>
      <Button
        title={recording ? 'Stop Recording' : 'Start Recording'}
        onPress={recording ? stopRecording : startRecording}
      />
      <Text>Transcription : {transcription}</Text>
      <Button title="Tester l'API" onPress={handleTestButtonClick} />
      <Text>Réponse de l'API : {apiTestResponse}</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: 'center',
    backgroundColor: '#ecf0f1',
    padding: 10,
  },
});
