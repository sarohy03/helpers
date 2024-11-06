import os
import time
import json
from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk

ELASTIC_ADDRESS = "http://localhost:9200"
INDEX_NAME = "interactions_index-6"

def index_documents(documents_filename, index_name, es_client):
    # Open the file containing the JSON data to index.
    with open(documents_filename, "r") as json_file:
        json_data = json.load(json_file)

        # Extract the vulnerabilities list from the JSON data.
        vulnerabilities = json_data.get("vulnerabilities", [])

        # Prepare documents for Elasticsearch indexing.
        documents = []
        for index, item in enumerate(vulnerabilities):
            # Each `item` is expected to be a dict

            if isinstance(item, dict):
                document = {
                    "_id": item.get("cve", {}).get("id", str(index)),  # Use CVE ID as document ID or fallback to index
                    "_source": item  # The vulnerability data goes into the document's _source field
                }
                if(item['cve']['id']== 'CVE-2023-46814'):
                    print("CVE-2023-46814")

                documents.append(document)

        # Use the bulk helper to index data in chunks
        indexing = bulk(es_client, documents, index=index_name, chunk_size=100)
        print(f"Indexed {documents_filename} - Success: {indexing[0]}, Failed: {len(indexing[1])}")

def main():
    directory_path = '/home/sarohy/PycharmProjects/pythonProject6/NewData/'

    # Declare a client instance of the Python Elasticsearch library.
    es_client = Elasticsearch(hosts=[ELASTIC_ADDRESS])

    # Loop through all JSON files in the specified directory
    for filename in os.listdir(directory_path):
        if filename.endswith(".json"):
            print(filename)

            document_filename = os.path.join(directory_path, filename)
            print(f"Indexing file: {document_filename}")

            initial_time = time.time()
            index_documents(document_filename, INDEX_NAME, es_client)
            finish_time = time.time()

            print(f'Documents indexed from {filename} in {finish_time - initial_time:.2f} seconds\n')

if __name__ == "__main__":
    main()
