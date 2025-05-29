# from fastapi import FastAPI
# from pydantic import BaseModel
# from langchain_community.vectorstores import FAISS
# from langchain_community.embeddings import HuggingFaceEmbeddings
# from langchain.chains.question_answering import load_qa_chain
# from langchain.llms import HuggingFacePipeline
# from transformers import pipeline
# import os

# # Load local sentence transformer model
# embedding_model = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

# # Load your FAISS vector store
# db = FAISS.load_local("nestle_faiss_index", embedding_model, allow_dangerous_deserialization=True)

# # Load local LLM (using transformers pipeline)
# qa_pipeline = pipeline("text2text-generation", model="google/flan-t5-base")
# llm = HuggingFacePipeline(pipeline=qa_pipeline)

# # Build QA Chain
# chain = load_qa_chain(llm, chain_type="stuff")

# # FastAPI app
# app = FastAPI()

# class Question(BaseModel):
#     question: str

# @app.post("/chat")
# def chat(q: Question):
#     docs = db.similarity_search(q.question)
#     result = chain.run(input_documents=docs, question=q.question)
#     return {"answer": result}  


from fastapi import FastAPI
from pydantic import BaseModel
# from langchain_pinecone import Pinecone as LangchainPinecone
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.chains.question_answering import load_qa_chain
from langchain.schema import Document  
from langchain.chat_models import ChatOpenAI
from dotenv import load_dotenv
from neo4j import GraphDatabase
from fastapi.middleware.cors import CORSMiddleware
# from pinecone import Pinecone

import os
import re

from dotenv import load_dotenv

# Load env variables
load_dotenv()
NEO4J_URI = os.getenv("NEO4J_URI")
NEO4J_USERNAME = os.getenv("NEO4J_USERNAME")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
INDEX_NAME = "nestle-index"

def extract_concepts(text):
    # Regex keywords (can later replace with spaCy NER)
    return list(set(re.findall(r"\b(?:milk|sugar|peanuts|hazelnuts|soy|wheat|gluten)\b", text.lower())))


# Connect to Neo4j
neo4j_driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))

# # Create Pinecone v3 client
# pc = Pinecone(api_key=PINECONE_API_KEY)

# # Get index object
# index = pc.Index(INDEX_NAME)



# ✅ Load environment variables
load_dotenv()
openai_key = os.getenv("OPENAI_API_KEY")


# def query_neo4j(concepts):
#     chunks = []
#     with neo4j_driver.session() as session:
#         for concept in concepts:
#             result = session.run("""
#                 MATCH (c:Chunk)-[:MENTIONS]->(term:Concept {name: $concept})
#                 RETURN c.text AS chunk, c.url AS url
#                 LIMIT 3
#             """, concept=concept)

#             for record in result:
#                 if record["chunk"]:  # Safety check
#                     chunks.append(Document(
#                         page_content=record["chunk"],
#                         metadata={"source": record["url"] or "unknown"}
#                     ))
#     return chunks

def query_neo4j(concepts):
    chunks = []
    with neo4j_driver.session() as session:
        for concept in concepts:
            result = session.run("""
                MATCH (c:Chunk)-[:MENTIONS]->(term:Concept {name: $concept})
                OPTIONAL MATCH (p:Page)-[:HAS_SECTION]->(:Section)-[:HAS_CHUNK]->(c)
                RETURN c.text AS chunk, coalesce(c.url, p.url, "unknown") AS url
                LIMIT 3
            """, concept=concept)
            for record in result:
                print(f"[Neo4j Result] Concept: {concept} | Chunk: {record['chunk'][:100]}... | URL: {record['url']}")
                if record["chunk"]:
                    chunks.append(Document(
                        page_content=record["chunk"],
                        metadata={"source": record["url"]}
                    ))
    return chunks


# ✅ Load the FAISS vector store
embedding_model = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

# db = LangchainPinecone(index, embedding_model, text_key="text")

db = FAISS.load_local("nestle_faiss_index", embedding_model, allow_dangerous_deserialization=True)

# ✅ Set up OpenAI LLM
llm = ChatOpenAI(openai_api_key=openai_key, model_name="gpt-4", temperature=0)

# ✅ Load QA chain
chain = load_qa_chain(llm, chain_type="stuff")

app = FastAPI()

#connecting frontend



# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Or restrict to ["http://localhost:3000"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



class Question(BaseModel):
    question: str

@app.post("/chat")
def chat(q: Question):
    # 🔍 1. FAISS semantic search
    faiss_docs = db.similarity_search(q.question, k=3)
    print(faiss_docs)

    # 🧠 2. Extract concepts from top FAISS results
    all_concepts = set()
    for doc in faiss_docs:
        all_concepts.update(extract_concepts(doc.page_content))

    # 🌐 3. Use concepts to query Neo4j
    neo4j_docs = query_neo4j(list(all_concepts))

    # 📚 4. Combine all chunks
    all_docs = faiss_docs + neo4j_docs
    # 🔍 DEBUG PRINT EACH DOCUMENT'S METADATA
    print("\n🔎 Document Metadata Debug:")
    for i, doc in enumerate(all_docs):
        print(f"Doc #{i+1}:")
        print(f"  Content: {doc.page_content[:]}...")  # Print first 100 chars only
        print(f"  Metadata: {doc.metadata}")

    all_sources = list({doc.metadata.get("source", "unknown") for doc in all_docs})

    # 💬 5. Send to GPT-4 via LangChain
    answer = chain.run(input_documents=all_docs, question=q.question + "If needed go to the source URLS yourself and check")

    return {
        "answer": answer,
        "sources": all_sources
    }
