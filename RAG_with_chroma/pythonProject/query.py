import chromadb
from langchain_chroma import Chroma
from sympy.polys.polyconfig import query

from embeddings import get_embedding_function

# Set up the client to connect to the existing Chroma database
persistent_client = chromadb.PersistentClient(path="chromao")  # Path to the Chroma database folder

def query_database(query_text: str, top_k: int = 5):
    # Initialize vector store with the existing collection
    vector_store = Chroma(
        client=persistent_client,
        collection_name="wow",
        embedding_function=get_embedding_function()
    )

    # Generate an embedding for the query text
    query_embedding = get_embedding_function()
    embedding = query_embedding.embed_query(query_text)

    # Retrieve the top-k most similar documents based on the query embedding
    results = vector_store.similarity_search(
        k=top_k,
        query=query_text,
    )

    # Display results
    print(f"Top {top_k} results for your query '{query_text}':")
    print(results)
    for i, result in enumerate(results):
        text = result.page_content  # Access page content (text)
        metadata = result.id # Access metadata (ID, page, source)

        print(f"\nResult {i + 1}")  # Display the result number
        print("Text:", text)  # Print the text (page content)
        print("Metadata:", metadata)  # Print the metadata dictionary
    return results


if __name__ == "__main__":
    # Replace with your query text
    query_text = "Nepoliean financial crisis"
    query_database(query_text, top_k=5)
