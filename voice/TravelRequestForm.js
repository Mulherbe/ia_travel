import React, { useState } from 'react';
import { View, Text, TextInput, TouchableOpacity, StyleSheet, ActivityIndicator } from 'react-native';
import Ask from './Ask';

const TravelRequestForm = () => {
  const [userInput, setUserInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [travelInfo, setTravelInfo] = useState(null);

  const handleSubmit = async () => {
    setIsLoading(true);

    const prompt = `Create a simple JSON with only two fields, 'depart' and 'arrivee', for the following request: ${userInput} Do not add any additional comments or information.`;

    try {
      const response = await fetch('http://192.168.1.105:1234/v1/chat/completions', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          model: 'local-model',
          messages: [{ role: 'system', content: prompt }],
          temperature: 0.7,
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
        
        setTravelInfo(result);
      }
    } catch (error) {
      console.error(error);
      setTravelInfo({ error: "Erreur lors de la connexion à l'API ou dans le parsing du JSON." });
    } finally {
      setIsLoading(false);
    }
  };

  if (isLoading) {
    return (
      <View style={styles.container}>
        <ActivityIndicator size="large" color="#0DB4D7" />
      </View>
    );
  }

  return (
    <View style={styles.container}>
      {!travelInfo ? (
        <>
          <Text style={styles.title}>Demandez votre itinéraire</Text>
          <TextInput
            style={styles.input}
            placeholder="Entrez votre destination (ex: 'De Paris à Nice')"
            placeholderTextColor="#AAAAAA"
            value={userInput}
            onChangeText={setUserInput}
          />
          <TouchableOpacity style={styles.button} onPress={handleSubmit}>
            <Text style={styles.buttonText}>Envoyer</Text>
          </TouchableOpacity>
        </>
      ) : (
        <View style={styles.travelInfo}>
          {travelInfo.error ? (
            <Text style={styles.errorText}>{travelInfo.error}</Text>
          ) : (
            <>
              <Text style={styles.infoText}>Départ : {travelInfo.depart}</Text>
              <Text style={styles.infoText}>Arrivée : {travelInfo.arrivee}</Text>
              <TouchableOpacity style={styles.button} onPress={() => setTravelInfo(null)}>
                <Text style={styles.buttonText}>Nouvelle recherche</Text>
              </TouchableOpacity>
            </>
          )}
        </View>
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
    width: '100%',
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
    width: '100%',
    alignItems: 'center',
    flexDirection: 'row',
    justifyContent: 'center',
  },
  buttonText: {
    color: '#FFFFFF',
    fontSize: 18,
  },
  travelInfo: {
    marginTop: 20,
  },
  infoText: {
    color: '#FFFFFF', // Texte blanc pour les informations de voyage
    fontSize: 16,
    textAlign: 'center',
  }
});

export default TravelRequestForm;
