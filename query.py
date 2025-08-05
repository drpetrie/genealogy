import chromadb
from chromadb.utils import embedding_functions
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction


# === CONFIGURATION ===
chroma_dir = "/Users/dpetrie/chroma_store"  # Chroma persistent storage
collection_name = "gedcom_family"

# === Set Up ChromaDB Client ===
chroma_client = chromadb.Client(chromadb.config.Settings(
    persist_directory=chroma_dir, is_persistent=True
))

embedding_fn = SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")

# Create or load collection
collection = chroma_client.get_or_create_collection(
    name=collection_name,
    embedding_function=embedding_fn
)

# === Query Loop ===
print("📜 Ask about your ancestors! (Type 'exit' to quit)")
while True:
    query = input("\n❓ Ask: ")
    if query.lower() in ["exit", "quit"]:
        break

    results = collection.query(
        query_texts=[query],
        n_results=5  # adjust how many top matches to return
    )
 #   print(results)

    matches = results['documents'][0]
    metadata = results['metadatas'][0]
    ids = results['ids'][0]
    scores = results['distances'][0]

    for i, (doc, score) in enumerate(zip(matches, scores)):
        print(f"\n{i+1}. ID: {ids[i]}")
        print(f"Score: {score:.4f}")
        print(f"Name: {metadata[i].get('name', 'Unknown')}")
#        print("Text Chunk:\n", doc)