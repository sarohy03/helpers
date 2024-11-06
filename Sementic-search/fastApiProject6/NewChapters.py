import os
import ebooklib
from ebooklib import epub
from bs4 import BeautifulSoup
import json
import requests
from dotenv import load_dotenv
from pymongo import MongoClient
from transformers import AutoTokenizer, AutoModel
import torch
from ElasticSearch import index_epub_data
load_dotenv()

# Environment variables
MONGO_LINK = os.getenv("MONGO_LINK")
EMBEDDING_MODEL_NAME = os.getenv('EMBEDDING_MODEL_NAME')

# MongoDB setup
client = MongoClient(MONGO_LINK)
db = client["Rag-epub"]
collection = db["667d766625f79ece946a03d0"]

# Load the tokenizer and model from Hugging Face
tokenizer = AutoTokenizer.from_pretrained(EMBEDDING_MODEL_NAME)
model = AutoModel.from_pretrained(EMBEDDING_MODEL_NAME)


def generate_embedding(text: str) -> list[float]:
    inputs = tokenizer(text, return_tensors='pt', truncation=True, padding=True)
    with torch.no_grad():
        outputs = model(**inputs)
        embedding = outputs.last_hidden_state.mean(dim=1).squeeze().tolist()
    return embedding


def chunk_text(text, max_length=512):
    chunks = []
    words = text.split()
    current_chunk = []

    for word in words:
        current_chunk.append(word)
        if len(' '.join(current_chunk)) > max_length:
            joined_chunk = ' '.join(current_chunk)
            last_period_index = joined_chunk.rfind('.')

            if last_period_index == -1:
                chunks.append(' '.join(current_chunk[:-1]))
                current_chunk = [word]
            else:
                chunks.append(joined_chunk[:last_period_index + 1])
                remaining_words = joined_chunk[last_period_index + 1:].strip().split()
                current_chunk = remaining_words

    if current_chunk:
        chunks.append(' '.join(current_chunk))

    return chunks


def embed_chunks(chunks, chapter_name,chap_no):
    all_doc =[]
    for entry in chunks:
        embedding = generate_embedding(entry)

        data_to_store = {
            "chapter": chapter_name,
            "chapter_number":chap_no,
                        "chunk": entry.lower(),
            "embedding": embedding
        }
        all_doc.append(data_to_store)
        #collection.insert_one(data_to_store)
    return all_doc


def extract_chapters_from_epub(epub_file):
    book = epub.read_epub(epub_file)
    chapters = []
    chap_no = 0

    for doc in book.get_items_of_type(ebooklib.ITEM_DOCUMENT):
        try:
            doc_name = doc.get_name()
            base_name = os.path.splitext(os.path.basename(doc_name))[0]

            body_content = doc.get_body_content()
            if body_content:
                chap_no += 1
                soup = BeautifulSoup(body_content, 'html.parser')
                data = soup.get_text()
                chapter_headings = soup.find_all('h2', class_='EP_chapter_head chapterhead')

                if chapter_headings:
                    for heading in chapter_headings:
                        chapter_title = heading.get_text(strip=True)
                        chapters.append({
                            "chapter": chapter_title,
                            "chapter_number": chap_no,
                            "data": data
                        })
                else:
                    chapters.append({
                        "chapter": base_name,
                        "chapter_number": chap_no,
                        "data": data
                    })

        except KeyError as e:
            print(f"Skipping document due to missing resource: {e}")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")

    return chapters

def insert_doc(embedding):
    for data_to_store in embedding:
        collection.insert_one(data_to_store)

def process_epub_file(epub_file):
    chapters = extract_chapters_from_epub(epub_file)
    print(chapters[0])
    for chapter in chapters:
        chapter_name = chapter["chapter"]
        chapter_text = chapter["data"]
        chapter_no = chapter["chapter_number"]
        chunks = chunk_text(chapter_text)
        embedded = embed_chunks(chunks, chapter_name,chapter_no)
        # print(embedded[0])
        # insert_doc(embedded)
        index_epub_data(embedded,"667d766625f79ece946a03d0")

def process_files_in_directory(directory_path="data/"):
    filename = "9780853304050-Education in the New Age-Alice A Bailey.epub"
    file_path = os.path.join(directory_path, filename)
    process_epub_file(file_path)


# Run the process for all EPUB files in the "data" directory
# process_files_in_directory()
