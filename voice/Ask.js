import React, { useState } from 'react';
import { View, Text, TextInput, TouchableOpacity, StyleSheet, ActivityIndicator } from 'react-native';
import { Audio } from 'expo-av';
import axios from 'axios';

const Ask = () => {
  const [isRecording, setIsRecording] = useState(false);
  const [userInput, setUserInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [apiResponse, setApiResponse] = useState('');
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
    setIsLoading(true); 

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
    setIsLoading(false); 

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

  const handleSubmit = async () => {
    setIsLoading(true);

    const prompt = `Create a simple JSON with only two fields, 'depart' and 'arrivee', for the following request: ${userInput} Do not add any additional comments or information.`;

    try {
      const response = await fetch('http://192.168.1.105:5001/pathF', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          text: prompt, // Modification ici pour envoyer `text` comme attendu par votre API Flask
        }),
      });

      const responseBody = await response.text();
      const data = JSON.parse(responseBody);

      if (data.choices && data.choices[0] && data.choices[0].message && data.choices[0].message.content) {
        const content = data.choices[0].message.content.trim();
        const startIndex = content.indexOf('{');
        const endIndex = content.lastIndexOf('}') + 1;
        const jsonContent = content.substring(startIndex, endIndex);
        const result = JSON.parse(jsonContent);
        
        setApiResponse(result);
      }
    } catch (error) {
      console.error(error);
      setApiResponse({ error: "Erreur lors de la connexion à l'API ou dans le parsing du JSON." });
    } finally {
      setIsLoading(false);
    }
  };
  const handleNewSearch = () => {
    setApiResponse(null);
    setUserInput('');
  };

  return (
    <View style={styles.container}>
      <Text style={styles.title}>Demandez votre itinéraire</Text>
      {isLoading ? (
        <ActivityIndicator size="large" color="#0DB4D7" />
      ) : (
        <>
          {apiResponse ? (
            // Afficher uniquement la réponse de l'API
            <View style={styles.apiResponse}>
              <Text style={styles.infoText}>Départ : {apiResponse.depart}</Text>
              <Text style={styles.infoText}>Arrivée : {apiResponse.arrivee}</Text>
              <TouchableOpacity style={styles.button} onPress={handleNewSearch}>
                <Text style={styles.buttonText}>Nouvelle recherche</Text>
              </TouchableOpacity>
            </View>
          ) : (
            // Afficher les champs de saisie et boutons si aucune réponse de l'API
            <>
              {isRecording ? (
                <TouchableOpacity style={styles.button} onPress={recording ? stopRecording : startRecording}>
                  <Text style={styles.buttonText}>{recording ? 'Stop Recording' : 'Start Recording'}</Text>
                </TouchableOpacity>
              ) : (
                <>
                  <TouchableOpacity style={styles.button} onPress={recording ? stopRecording : startRecording}>
                    <Text style={styles.buttonText}>{recording ? 'Stop Recording' : 'Start Recording'}</Text>
                  </TouchableOpacity>
                  <TextInput
                    style={styles.input}
                    placeholder="Type your text here"
                    placeholderTextColor="#AAAAAA"
                    value={userInput}
                    onChangeText={setUserInput}
                  />
                  <TouchableOpacity style={styles.button} onPress={handleSubmit}>
                    <Text style={styles.buttonText}>Send Text</Text>
                  </TouchableOpacity>
                </>
              )}
            </>
          )}
        </>
      )}
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
    padding: 20,
    backgroundColor: '#121212',
  },
  title: {
    fontSize: 24,
    color: '#0DB4D7',
    marginBottom: 20,
  },
  input: {
    width: '80%',
    marginTop: 40,
    marginBottom: 20,
    borderWidth: 1,
    borderColor: '#0DB4D7',
    backgroundColor: '#1E1E1E',
    color: '#FFFFFF',
    padding: 10,
    borderRadius: 5,
  },
  button: {
    backgroundColor: '#0DB4D7',
    padding: 10,
    borderRadius: 5,
    width: '50%',
    alignItems: 'center',
    flexDirection: 'row',
    justifyContent: 'center',
  },
  buttonText: {
    color: '#FFFFFF',
    fontSize: 18,
  },
  apiResponse: {
    marginTop: 20,
  },
  infoText: {
    color: '#FFFFFF', // Texte blanc pour les informations de voyage
    fontSize: 16,
    textAlign: 'center',
  }
});
export default Ask;
