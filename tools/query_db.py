import os
from dotenv import load_dotenv

_PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
load_dotenv("../.env")

DB_PATH = os.path.join(_PROJECT_ROOT, os.getenv("CHROMA_DB_PATH"))

from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings


def query_db(query: str, k: int=3, db_path: str=DB_PATH, collection_name: str=os.getenv("CHROMA_DB_COLLECTION_NAME")) -> str:
    """get the best matching 'k' documents for the query
    
    Args:
        query (str): query
        k (int, optional): number of top matching documents to retrieve (use more than 1 for enhanced correct retrievals). Defaults to 3
        db_path (str, optional): path to the vector db. Defaults to "CHROMA_DB_PATH".
        collection_name (str, optional): name of the db collection. Defaults to "CHROMA_DB_COLLECTION_NAME".

    Returns:
        str: db schema info of relavant tables
    """
    embeddings = OpenAIEmbeddings()
    db = Chroma(
        persist_directory=db_path,
        embedding_function=embeddings,
        collection_name=collection_name,
    )
    
    docs = db.similarity_search(
        query=query,
        k=k,
    )
    
    return "\n\n".join([doc.page_content for doc in docs])


if __name__ == "__main__":
    test_queries = [
        "Which country has the most customers?",
        "What is the total freight cost per customer?",
        "Top 5 best selling products",
        "Total revenue by product category",
    ]
    
    for query in test_queries:
        res = query_db(
            query, 
            k=3,
        )
        print(f"Query: '{query}'")
        print(res)
        print("---")
