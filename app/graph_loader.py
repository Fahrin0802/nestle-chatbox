# from neo4j import GraphDatabase

# # Connection details
# uri = "bolt://localhost:7687"
# username = "neo4j"
# password = "abcd1234"

# driver = GraphDatabase.driver(uri, auth=(username, password))

# def insert_page_and_chunk(tx, url, text):
#     tx.run("""
#         MERGE (p:Page {url: $url})
#         CREATE (c:Chunk {text: $text})
#         MERGE (p)-[:HAS_CHUNK]->(c)
#     """, url=url, text=text)


# def load_chunks_to_graph(docs):
#     driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "abcd1234"))
#     with driver.session() as session:
#         for doc in docs:
#             url = doc.metadata.get("source", "unknown")
#             text = doc.page_content
#             session.write_transaction(insert_page_and_chunk, url, text)
#     driver.close()
#     print("✅ Chunks and Pages loaded into Neo4j graph with relationships.")


# # Example usage
# if __name__ == "__main__":
#     from langchain_community.vectorstores import FAISS
#     from langchain_community.embeddings import HuggingFaceEmbeddings

#     # Load your FAISS DB
#     embedding_model = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
#     db = FAISS.load_local("nestle_faiss_index", embedding_model, allow_dangerous_deserialization=True)

#     # Get all documents (chunks)
#     docs = db.similarity_search("KitKat")  # You can also get all if you want
#     load_chunks_to_graph(docs)

# from langchain_community.vectorstores import FAISS
# from langchain_community.embeddings import HuggingFaceEmbeddings
# from langchain.text_splitter import RecursiveCharacterTextSplitter
# from neo4j import GraphDatabase
# import os

# # Load embeddings and FAISS DB
# embedding_model = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
# db = FAISS.load_local("nestle_faiss_index", embedding_model, allow_dangerous_deserialization=True)

# # Get the chunked documents
# all_docs = db.docstore._dict.values()

# # all_docs = db.similarity_search("dummy query", k=1671)  # Return all chunks in DB

# # Set up Neo4j driver
# driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "abcd1234"))

# def insert_chunk(tx, url, text):
#     tx.run("""
#         MERGE (p:Page {url: $url})
#         CREATE (c:Chunk {text: $text})
#         MERGE (p)-[:HAS_CHUNK]->(c)
#     """, url=url, text=text)

# def load_chunks_to_graph(docs):
#     with driver.session() as session:
#         for doc in docs:
#             url = doc.metadata.get("source", "unknown")
#             text = doc.page_content.strip()
#             if text:
#                 session.execute_write(insert_chunk, url, text)

# if __name__ == "__main__":
#     print(f"📦 Loading {len(all_docs)} chunks into Neo4j...")
#     load_chunks_to_graph(all_docs)
#     print("✅ Chunks loaded into Neo4j graph.")
#     driver.close()

from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from neo4j import GraphDatabase
from dotenv import load_dotenv
import os
import re

# Load env variables
load_dotenv()
NEO4J_URI = os.getenv("NEO4J_URI")
NEO4J_USERNAME = os.getenv("NEO4J_USERNAME")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")


# Connect to Neo4j
driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))

# Load FAISS vector DB
embedding_model = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
db = FAISS.load_local("nestle_faiss_index", embedding_model, allow_dangerous_deserialization=True)
docs = db.similarity_search("", k=10000)  # Retrieves all documents from the index


def is_informative(text):
    text = text.strip()
    if len(text) < 40:
        return False

    # Ratio of alphabetic characters
    alpha_ratio = sum(c.isalpha() for c in text) / max(len(text), 1)
    if alpha_ratio < 0.4:
        return False

    # Common noisy patterns (case insensitive)
    noisy_patterns = [
        r"up next", r"playing", r"see all products", r"recent videos",
        r"watch now", r"click here", r"\bshop\b", r"find your fave",
        r"prepared in canada", r"holiday favourites", r"l'atelier video"
    ]
    for pattern in noisy_patterns:
        if re.search(pattern, text, re.IGNORECASE):
            return False

    # Remove if too repetitive (same word many times)
    words = text.lower().split()
    word_freq = {w: words.count(w) for w in set(words)}
    if any(count > len(words) * 0.4 for count in word_freq.values()):
        return False

    return True


# Helper: Extract concepts (naive example, improve later with spaCy)
def extract_concepts(text):
    # You can replace this with spaCy NER or regex for real concepts
    keywords = re.findall(r"\b(?:milk|sugar|peanuts|hazelnuts|soy|wheat|gluten)\b", text.lower())
    return list(set(keywords))

# Insertion logic
def insert_graph(tx, url, chunk_text):
    section_title = "default"
    concepts = extract_concepts(chunk_text)
    tx.run('''
        MERGE (p:Page {url: $url})
        MERGE (s:Section {title: $section_title})
        MERGE (p)-[:HAS_SECTION]->(s)
        CREATE (c:Chunk {text: $chunk_text, url: $url})
        MERGE (s)-[:HAS_CHUNK]->(c)
    ''', url=url, section_title=section_title, chunk_text=chunk_text)

    for concept in concepts:
        tx.run('''
            MERGE (term:Concept {name: $concept})
            MERGE (term)-[:TYPE]->(:Type {name: $type})
            MERGE (c:Chunk {text: $chunk_text})
            MERGE (c)-[:MENTIONS]->(term)
        ''', concept=concept, type="ingredient", chunk_text=chunk_text)

# Main logic
def load_to_graph():
    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=100)

    with driver.session() as session:
        for doc in docs:
            url = doc.metadata.get("source")
            chunks = splitter.create_documents([doc.page_content])
            for chunk in chunks:
                if not is_informative(chunk.page_content):
                    continue
                session.execute_write(insert_graph, url, chunk.page_content)
                
    print("✅ All chunks and concept relationships loaded into graph!")
                

if __name__ == "__main__":
    load_to_graph()

