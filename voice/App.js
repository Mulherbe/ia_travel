import { StatusBar } from 'expo-status-bar';
import { StyleSheet, Text, View } from 'react-native';
import Ask from './Ask';
import TravelRequestForm from './TravelRequestForm';
export default function App() {
  return (
    <View style={styles.container}>
      <Ask/>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
});
