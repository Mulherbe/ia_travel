import qdrant_client
from llama_index.llms import Ollama
from llama_index import (
    VectorStoreIndex,
    ServiceContext,
)
from llama_index.vector_stores.qdrant import QdrantVectorStore
from flask import Flask, request, jsonify
from httpx import Client, Timeout  # Utiliser httpx directement
from flask_restful import Api
from flask_api import status
from flask_cors import CORS, cross_origin

# Configuration du client HTTPX avec un timeout global
httpx_client = Client(timeout=60)  # Délai d'attente de 60 secondes

client = qdrant_client.QdrantClient(
    path="./qdrant_data",
    timeout=60  # Ajustez le timeout pour Qdrant si nécessaire
)
vector_store = QdrantVectorStore(client=client, collection_name="epiech")

# Get the LLM
llm = Ollama(model="mistral")
service_context = ServiceContext.from_defaults(llm=llm, embed_model="local")
# Load the index from the vector store
index = VectorStoreIndex.from_vector_store(vector_store=vector_store, service_context=service_context)

app = Flask(__name__)
api = Api(app)

cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'


@api.errorhandler(TimeoutException)  # Gérer l'exception Timeout générale
def handle_timeout(error):
    return jsonify({"error": "La requête a pris trop de temps. Veuillez réessayer plus tard."}), 503


@app.route('/process_form', methods=['POST'])
@cross_origin()
def process_form():
    query = request.form.get('query')
    if query is not None:
        try:
            response = httpx_client.get(
                "http://localhost:8080/process_query",  # Adaptez l'URL et la méthode
                params={"query": query}
            )
            response.raise_for_status()  # Renvoie une exception pour les codes de statut d'échec
            return jsonify({"response": response.json()})
        except TimeoutException as e:
            return handle_timeout(e)
        except Exception as e:  # Gérer les autres exceptions
            return jsonify({"error": str(e)}), status.HTTP_400_BAD_REQUEST
    else:
        return jsonify({"error": "query field is missing"}), status.HTTP_400_BAD_REQUEST


@app.route('/test', methods=['GET'])
@cross_origin()
def test_route():
    return jsonify({"message": "This is a test route!"})


if __name__ == "__main__":
    app.run(host='0.0.0.0')