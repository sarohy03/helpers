import os
import shutil
from importlib.metadata import metadata

from chromadb.api.models.Collection import Collection
from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.schema.document import Document
from triton.language.extra.hip.libdevice import trunc

from embeddings import get_embedding_function
from langchain_chroma import Chroma
import chromadb

persistent_client = chromadb.PersistentClient(path="chromao")  # Saves to "chromao" folder
DATA_PATH = "data"


def  main(reset=False):
    if reset:
        print("✨ Clearing Database")
        clear_database()

    # Create (or update) the data store.
    documents = load_documents()
    # print(documents)
    chunks = split_documents(documents)
    add_to_chroma(chunks)


def load_documents():
    document_loader = PyPDFDirectoryLoader(DATA_PATH)
    return document_loader.load()


def split_documents(documents: list[Document]):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=20,
        length_function=len,
    is_separator_regex=True,
        separators=[
            "\n\n",
            "\n",
            " ",
            ".",
            ",",
            "\u200b",  # Zero-width space
            "\uff0c",  # Fullwidth comma
            "\u3001",  # Ideographic comma
            "\uff0e",  # Fullwidth full stop
            "\u3002",  # Ideographic full stop
            "",
        ],    )
    return text_splitter.split_documents(documents)


def add_to_chroma(chunks: list[Document]):
    # Initialize vector store
    vector_store = Chroma(
        client=persistent_client,
        collection_name="wow",
        embedding_function=get_embedding_function()
    )

    # Calculate unique chunk IDs
    chunks_with_ids = calculate_chunk_ids(chunks)

    # Get existing document IDs in the collection
    existing_items = vector_store.get(include=[])  # IDs are always included by default
    existing_ids = set(existing_items["ids"])
    print(f"Number of existing documents in DB: {len(existing_ids)}")

    new_chunks = []
    for chunk in chunks_with_ids:
        if chunk.metadata["id"] not in existing_ids:
            new_chunks.append(chunk)

    if len(new_chunks):
        print(f"👉 Adding new documents: {len(new_chunks)}")
        new_chunk_ids = [chunk.metadata["id"] for chunk in new_chunks]

        try:
            vector_store.add_documents(ids=new_chunk_ids, documents=new_chunks)
        except Exception as e:
            print("Error while adding documents:", e)
    else:
        print("✅ No new documents to add")


def calculate_chunk_ids(chunks):
    last_page_id = None
    current_chunk_index = 0

    for chunk in chunks:
        source = chunk.metadata.get("source")
        page = chunk.metadata.get("page")
        current_page_id = f"{source}:{page}"

        if current_page_id == last_page_id:
            current_chunk_index += 1
        else:
            current_chunk_index = 0

        chunk_id = f"{current_page_id}:{current_chunk_index}"
        last_page_id = current_page_id
        chunk.metadata["id"] = chunk_id

    return chunks


def clear_database():
    if os.path.exists("chromao"):
        shutil.rmtree("chromao")


if __name__ == "__main__":
    main(reset=False)  # Pass reset=True to clear the database
