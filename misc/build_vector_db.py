import os
from dotenv import load_dotenv
load_dotenv("../.env")

from typing import List

import pandas as pd
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain.docstore.document import Document


SCHEMA_INFO_CSV = "../data/test_db_vector_schema_info.csv"
CHROMA_DB_PATH = "../vector_db"
CHROMA_DB_COLLECTION_NAME = "test_db_schema_info"


def load_csv(file_path: str) -> pd.DataFrame:
    df = pd.read_csv(file_path)
    
    # fill nan with empty strings
    df = df.fillna("")
    print(f"Loaded {len(df)} rows from {file_path}")
    
    return df


def row_to_document(row: pd.Series) -> Document:
    """"
    Build a text blob from each CSV row using the
    schema CSV fields: id, type, name, description, columns.
    Metadata fields allow filtering later
    """
    parts = []
    
    # type info
    entry_type = str(row.get("type", "")).strip()
    name = str(row.get("name", "")).strip()
    parts.append(f"Type: {entry_type}")
    parts.append(f"Name: {name}")
    
    # dexcription
    desc = str(row.get("description", "")).strip()
    if desc:
        parts.append(f"Description: {desc}")
        
    # columns
    cols = str(row.get("columns", "")).strip()
    if cols:
        parts.append(f"Columns: {cols}")
        
    page_content = "\n".join(parts)
    print(f"{page_content=}")
    print("==" * 20)
    
    # metadata
    metadata = {
        "id": str(row.get("id", "")),
        "type": entry_type,
        "name": name,
    }
    
    return Document(page_content=page_content, metadata=metadata)


def build_documents(df: pd.DataFrame) -> List[Document]:
    docs = [row_to_document(row) for _, row in df.iterrows()]
    print(f"Built {len(docs)} documents")
    
    return docs


def build_vectorstore(data_path: str) -> Chroma:
    print(f"Embedding documents and saving to {CHROMA_DB_PATH}")

    df = load_csv(data_path)
    docs = build_documents(df)
    
    embeddings = OpenAIEmbeddings()
    
    vectorstore = Chroma.from_documents(
        documents=docs,
        embedding=embeddings,
        collection_name=CHROMA_DB_COLLECTION_NAME,
        persist_directory=CHROMA_DB_PATH,
    )
    
    print(f"ChromaDB built and saved to {CHROMA_DB_PATH}")
    
    return vectorstore
    

if __name__ == "__main__":
    # build_vectorstore(SCHEMA_INFO_CSV)
    
    print("[INFO] Checking similarity")
    embeddings = OpenAIEmbeddings()
    db = Chroma(
        persist_directory=CHROMA_DB_PATH, 
        embedding_function=embeddings, 
        collection_name=CHROMA_DB_COLLECTION_NAME,
    )
    
    test_queries = [
        "Which country has the most customers?",
        "What is the total freight cost per customer?",
        "Top 5 best selling products",
        "Total revenue by product category",
    ]
    
    for query in test_queries:
        res = db.similarity_search(
            query, 
            k=3,
        )
        print("==" * 20)
        print(f"Query: '{query}'")
        # names = [doc.metadata["name"] for doc in res]
        for doc in res:
            print(f"name: {doc.metadata['name']}")
            print(doc.page_content)
            print("---")
    