from flask import Flask, request, jsonify
from flask_cors import CORS, cross_origin
import qdrant_client
from llama_index.llms import Ollama
from llama_index import (
    VectorStoreIndex,
    ServiceContext,
)
from llama_index.vector_stores.qdrant import QdrantVectorStore

app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

try:
    # Initialize the vector store
    client = qdrant_client.QdrantClient(
        path="./qdrant_data",
        timeout=500
    )
    vector_store = QdrantVectorStore(client=client, collection_name="epiech")

    # Load the LLM
    llm = Ollama(model="mistral")
    service_context = ServiceContext.from_defaults(llm=llm, embed_model="local")
    
    # Load the index from the vector store
    index = VectorStoreIndex.from_vector_store(vector_store=vector_store, service_context=service_context)
except Exception as e:
    app.logger.error(f"Initialization Error: {e}")

# This is just so you can easily tell the app is running
@app.route('/')
def hello_world():
    return 'Hello, World!'

@app.route('/process_form', methods=['POST'])
@cross_origin()
def process_form():
    try:
        query = request.form.get('query')
        if query is not None:
            query_engine = index.as_query_engine(similarity_top_k=20)
            response = query_engine.query(query)
            return jsonify({"response": str(response)})
        else:
            return jsonify({"error": "query field is missing"}), 400
    except Exception as e:
        app.logger.error(f"Error in process_form: {e}")
        return jsonify({f"Error in process_form: {e}"}), 500

@app.route('/test', methods=['GET'])
@cross_origin()
def test_route():
    return jsonify({"message": "This is a test route!"})

@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Internal Server Error"}), 500

@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Not Found"}), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0')
