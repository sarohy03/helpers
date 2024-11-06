
from fastapi import FastAPI
from elasticsearch import Elasticsearch
from pydantic import BaseModel
# from getting_data import search_documents

class Data(BaseModel):
    app: str
    version: str


async def search_documents(es_client, index_name, query_body, values: Data ,size=10):
    response = es_client.search(index=index_name, body=query_body, size=size)
    hits = response['hits']['hits']

    results = []
    for hit in hits:
        # results.append(hit['_source'])
        val = hit['_source']
        id = val ['cve']['id']
        description = val ['cve']['descriptions']
        doc = {
            "id": id,
            "description": description,
        }
        results.append(doc)

    return {
        "app":values.app,
        "version":values.version,
        "total": response['hits']['total']['value'],
        "results": results
    }




async def search_by_field(es_client, index_name, field, values: Data, size=10000):
    query_body = {
        "query": {
            "bool": {
                "must": [
                    {
                        "match_phrase": {field: values.app}
                    },
                    {
                        "match_phrase": {field: values.version}
                    }
                ]
            }
        }
    }

    return await search_documents(es_client, index_name, query_body,values, size)


app = FastAPI()


@app.post("/search")
async def root(data: Data):
    ELASTIC_ADDRESS = "http://localhost:9200"
    INDEX_NAME = "interactions_index-6"
    es_client = Elasticsearch(hosts=[ELASTIC_ADDRESS])

    result = await search_by_field(es_client, INDEX_NAME, "cve.descriptions.value", data)

    return result
