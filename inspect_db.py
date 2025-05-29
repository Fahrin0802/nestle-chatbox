from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings

# Load the embedding model (same as you used during saving)
embedding_model = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

# Load the FAISS index from local directory
db = FAISS.load_local("nestle_faiss_index", embedding_model, allow_dangerous_deserialization=True)

# Retrieve all documents stored in the vector DB
docs = db.similarity_search("Show me everything", k=9999)

print(f"✅ Loaded {len(docs)} documents from FAISS vector DB\n")

# Print a preview
for i, doc in enumerate(docs[:10]):  # change 10 to view more
    print(f"--- Document #{i+1} ---")
    print(f"Source: {doc.metadata.get('source', 'N/A')}")
    print(doc.page_content[:500])  # only show the first 500 characters
    print()
