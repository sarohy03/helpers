from langchain_huggingface import HuggingFaceEmbeddings

def get_embedding_function():
    # Initialize HuggingFaceEmbeddings with the correct model
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-mpnet-base-v2")
    return embeddings  # Return the embed_query method
