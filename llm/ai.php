<?php

// Vérifier si le formulaire a été soumis
if ($_SERVER["REQUEST_METHOD"] == "POST") {
  // Récupérer la phrase de l'utilisateur
  $userInput = $_POST['userInput'];

  // Préparer le prompt pour l'API LLM
  $prompt = "Create a simple JSON with only two fields, 'depart' and 'arrivee', for the following request: " . $userInput . " Do not add any additional comments or information.";

  // Envoyer la requête à l'API LLM

  $responseJson = callYourLLMAPI($prompt);

    // Afficher la réponse brute pour le débogage
    echo "<h3>Réponse brute de l'API :</h3>";
    echo "<pre>" . htmlspecialchars($responseJson) . "</pre>";

    // Extraire le JSON de la réponse
    $jsonStart = strpos($responseJson, "{");
    $jsonEnd = strrpos($responseJson, "}") + 1;
    $jsonLength = $jsonEnd - $jsonStart;
    $jsonString = substr($responseJson, $jsonStart, $jsonLength);

    $responseData = json_decode($jsonString, true);

    if (json_last_error() !== JSON_ERROR_NONE) {
        echo "<h3>Erreur lors du décodage du JSON : " . json_last_error_msg() . "</h3>";
    } elseif (isset($responseData['depart']) && isset($responseData['arrivee'])) {
        $depart = $responseData['depart'];
        $arrivee = $responseData['arrivee'];

        echo "<h3>Informations d'Itinéraire :</h3>";
        echo "Départ : " . htmlspecialchars($depart) . "<br>";
        echo "Arrivée : " . htmlspecialchars($arrivee);
    } else {
        echo "<h3>La réponse de l'IA n'est pas disponible ou est mal formée.</h3>";
    }
}

// Fonction simulée pour appeler votre API LLM
function callYourLLMAPI($prompt) {
  // URL de votre serveur LLM local
  $url = 'http://localhost:1234/v1/chat/completions';

  // Données à envoyer sous forme de tableau PHP
  $data = [
      'model' => 'local-model',  // Modèle utilisé, si nécessaire
      'messages' => [
          ['role' => 'system', 'content' => $prompt]
      ],
      'temperature' => 0.7,  // Paramètre optionnel pour contrôler la créativité de la réponse
  ];

  // Initialisation de cURL
  $ch = curl_init($url);

  // Configuration des options de cURL
  curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
  curl_setopt($ch, CURLOPT_HTTPHEADER, ['Content-Type: application/json']);
  curl_setopt($ch, CURLOPT_POST, true);
  curl_setopt($ch, CURLOPT_POSTFIELDS, json_encode($data));

  // Envoi de la requête et réception de la réponse
  $response = curl_exec($ch);

  // Fermeture de la session cURL
  curl_close($ch);

  // Gestion des erreurs
  if (!$response) {
      return json_encode(["error" => "Aucune réponse de l'API"]);
  }

  // Décoder la réponse JSON
  $responseData = json_decode($response, true);

  // Extraire uniquement la réponse de l'IA
  if (isset($responseData['choices'][0]['message']['content'])) {
      return $responseData['choices'][0]['message']['content'];
  } else {
      return "La réponse de l'IA n'est pas disponible.";
  }
}



?>
<!DOCTYPE html>
<html>
<head>
    <title>Requête de Voyage</title>
</head>
<body>

<h1>Demandez votre itinéraire</h1>

<!-- Formulaire pour entrer la phrase -->
<form method="post" action="">
    <label for="userInput">Entrez votre destination (ex: "Je veux aller de Paris à Nice"):</label><br>
    <input type="text" id="userInput" name="userInput"><br>
    <input type="submit" value="Envoyer">
</form>

</body>
</html>