import qdrant_client
from llama_index import (
    VectorStoreIndex,
    ServiceContext,
)
from llama_index.llms import Ollama
from llama_index.vector_stores.qdrant import QdrantVectorStore

# Configurez le client Qdrant
client = qdrant_client.QdrantClient(
    path="qdrant_data",
    timeout=60
)

# Configurez le stockage de vecteurs
vector_store = QdrantVectorStore(client=client, collection_name="epiech")

# Initialisez le modèle LLM
llm = Ollama(model="mistral")

# Créez un contexte de service en utilisant les paramètres par défaut
service_context = ServiceContext.from_defaults(llm=llm, embed_model="local")

# Créez un index à partir du stockage de vecteurs
index = VectorStoreIndex.from_vector_store(vector_store=vector_store, service_context=service_context)

# Créez un moteur de requête à partir de l'index
query_engine = index.as_query_engine(similarity_top_k=20)

# Tentez d'exécuter la requête et gérez les exceptions liées au timeout
try:
    response = query_engine.query("Raconte moi en francais l'histoire de marco, jad , gael , yoanet fred")
    print(response)
except TimeoutError as e:
    print(f"La requête a dépassé le temps d'attente maximum : {e}")
except Exception as e:
    print(f"Une erreur est survenue lors de la requête : {e}")
