import os
from dotenv import load_dotenv
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from some_scraper import scrape_all_pages

load_dotenv()


def store_scraped_content():
    scraped_entries = scrape_all_pages()
    if not scraped_entries:
        print("🚫 No pages were scraped. Check the scraper.")
        return

    print(f"🧽 Total scraped entries: {len(scraped_entries)}")

    all_docs = []
    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=100)

    for entry in scraped_entries:
        url = entry["url"]
        text = entry["text"]

        if not text.strip():
            print(f"⚠️ Skipping empty content from {url}")
            continue

        chunks = splitter.create_documents([text])
        for doc in chunks:
            doc.metadata = {"source": url}
        all_docs.extend(chunks)

    if not all_docs:
        print("🚫 No document chunks generated. Nothing to embed.")
        return

    print(f"📦 Total document chunks to embed: {len(all_docs)}")
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    db = FAISS.from_documents(all_docs, embeddings)
    db.save_local("nestle_faiss_index")
    print("✅ FAISS vector DB stored with", len(all_docs), "documents.")


if __name__ == "__main__":
    store_scraped_content()
