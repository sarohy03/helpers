from elasticsearch import Elasticsearch

# Initialize Elasticsearch client
es = Elasticsearch("http://localhost:9200")
index = "667d766625f79ece946a03d0"

# Define index mappings
index_mapping = {
  "mappings": {
    "properties": {
      "chapter": {
        "type": "text"
      },
      "chapter_number": {
        "type": "text"
      },
      "chunk": {
        "type": "text"
      },
      "embedding": {
        "type": "dense_vector",
        "dims": 384
      }
    }
  }
}

# Create the index
es.indices.create(index=index, body=index_mapping)
