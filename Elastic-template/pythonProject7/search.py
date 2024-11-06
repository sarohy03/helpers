from elasticsearch import Elasticsearch

# Elastic configuration.
ELASTIC_ADDRESS = "http://localhost:9200"
INDEX_NAME = "interactions_index-6"

def search_documents(es_client, index_name, query_body, size=10):
    response = es_client.search(index=index_name, body=query_body, size=size)
    hits = response['hits']['hits']

    print(f"Found {response['hits']['total']['value']} documents")
    for i, hit in enumerate(hits, start=1):
        print(f"Result {i}: {hit['_source']}")
        #break

def split_string_to_list(input_string):
    result_list = input_string.split()
    return result_list

def search_by_field(es_client, index_name, field, values, size=10000):
    values = split_string_to_list(values)
    for value in values:
        print(f"Searching {value}")
    query_body = {
        "query": {
            "bool": {
                "must": [
                    {"match": {field: value}}
                    for value in values
                ]
            }
        }
    }
    search_documents(es_client, index_name, query_body, size)

def main():
    es_client = Elasticsearch(hosts=[ELASTIC_ADDRESS])

    search_by_field(es_client, INDEX_NAME, "cve.descriptions.value", "VLC Media Player 2.1.6")

if __name__ == "__main__":
    main()
