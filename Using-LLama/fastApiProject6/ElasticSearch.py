import chunk
from numbers import Number

from elasticsearch import Elasticsearch, helpers

# Initialize Elasticsearch client
es = Elasticsearch("http://localhost:9200")


def index_epub_data(data_list, index_name):
    """
  Function to index a list of EPUB data into Elasticsearch using the bulk API.

  Parameters:
  - data_list: List of dictionaries containing 'chapter', 'chapter_number', 'chunk', and 'embedding'.
  - index_name: The name of the Elasticsearch index to store the data.

  Returns:
  - None
  """

    def bulk_index_data(data_list):
        for entry in data_list:
            yield {
                "_index": index_name,
                "_source": entry
            }

    # Bulk indexing the data
    helpers.bulk(es, bulk_index_data(data_list))
    print(f"Data indexed successfully into '{index_name}'")


def search_epub_chunk(index_name, query):
    """
  Function to perform a full-text search on chunks in the indexed EPUB data.

  Parameters:
  - index_name: The name of the Elasticsearch index to search.
  - query: The search term (string) to search in the chunk content.

  Returns:
  - List of search results with chapter and chunk.
  """
    response = es.search(
        index=index_name,
        body={
            "query": {
                "match": {
                    "chunk": query
                }
            }
        }
    )

    # Extract and return search results
    results = []
    for hit in response['hits']['hits']:
        #print(hit['_source'])
        results.append({
            "content": hit['_source']['chunk'],
            "chapter": hit['_source']['chapter'],
            "number": hit['_source']['chapter_number'],
            "embedding": hit['_source']['embedding']
        })

    return results


def search_by_embedding(index_name, query_vector):
    """
  Function to perform an embedding-based search (semantic search) in the indexed EPUB data.

  Parameters:
  - index_name: The name of the Elasticsearch index to search.
  - query_vector: The query embedding vector for similarity search.

  Returns:
  - List of search results with chapter, chunk, and similarity score.
  """
    response = es.search(
        index=index_name,
        body={
            "query": {
                "script_score": {
                    "query": {
                        "match_all": {}
                    },
                    "script": {
                        "source": "cosineSimilarity(params.query_vector, 'embedding') + 1.0",
                        "params": {
                            "query_vector": query_vector
                        }
                    }
                }
            }
        }
    )

    # Extract and return search results
    results = []
    for hit in response['hits']['hits']:
        results.append({
            "chapter": hit['_source']['chapter'],
            "chunk": hit['_source']['chunk'],
            "score": hit['_score']
        })

    return results



def get_data(index_name,query):
    """
    Function to retrieve all documents from an Elasticsearch index.

    Parameters:
    - index_name: The name of the Elasticsearch index to retrieve data from.

    Returns:
    - List of all documents in the index.
    """
    # Define search query to fetch all documents with the given query
    # Generate match_phrase clauses for slop values from 0 to 30
    slop_queries = [
        {
            "match_phrase": {
                "chunk": {
                    "query": query,
                    "slop": slop_value
                }
            }
        }
        for slop_value in range(0, 31)  # Generate slop values from 0 to 30
    ]

    # Define search query to fetch all documents with the given query and slop range
    response = es.search(
        index=index_name,
        query={
            "bool": {
                "should": slop_queries
            }
        },
        size=1000  # Adjust size to fetch more documents (max default is 10)
    )

    # Extract and return all the documents
    documents = []
    total_docs = response['hits']['total']['value']
    print(f"Found {total_docs} documents")

    for hit in response['hits']['hits']:
        print(hit['_source'])
        res = {
            "content": hit['_source']['chunk'],
            "chapter": hit['_source']['chapter'],
            "number": hit['_source']['chapter_number'],
            "embedding": hit['_source']['embedding']
        }
        documents.append(res)

    return documents

# Example usage



def delete_index(index_name):
    """
    Function to delete an Elasticsearch index.

    Parameters:
    - index_name: The name of the Elasticsearch index to delete.

    Returns:
    - A response from Elasticsearch indicating success or failure.
    """
    # Check if the index exists before trying to delete it
    if es.indices.exists(index=index_name):
        # Delete the index
        response = es.indices.delete(index=index_name)
        return response
    else:
        return f"Index '{index_name}' does not exist."


# Example usage:
# index_name = "667d766625f79ece946a03d0"
# delete_response = delete_index(index_name)
# print(delete_response)
#
# get_data(index_name,"ways in education")
# search_epub_chunk("aab-es","education")