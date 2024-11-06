import json
import os
from typing import Dict

from fastapi import FastAPI
from pydantic import BaseModel
from torch.nn.functional import embedding

from NewChapters import generate_embedding, db
from groq import Groq
from dotenv import load_dotenv
from Syninom import process_query,clean_data
from ElasticSearch import search_epub_chunk,get_data
from Ranking import get_ranked_answers
load_dotenv()

app = FastAPI()

client = Groq(
    api_key=os.getenv("GROQ_API_KEY"),
)


class QueryRequest(BaseModel):
    id:str
    query: str
    synonym:bool
    ranking:bool



def query_mongo(query: str, id:str) :
    query_vector = generate_embedding(query)

    results = db[id].aggregate([
        {
            "$vectorSearch": {
                "queryVector": query_vector,
                "path": "embedding",
                "numCandidates": 2100,
                "limit": 50,
                "index": "HUI"
            }
        }
    ])
    all_data=[]
    for document in results:
        chunk = document["chunk"]
        chapter = document["chapter"]
        number = document["chapter_number"]
        embedding = document["embedding"]
        doc ={
            "content":chunk,
            "chapter":chapter,
            "number":number,
            "embedding":embedding
        }
        all_data.append(doc)

    return all_data


def generate_completion(content: str) -> dict[str, str]:
    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": content,
                }
            ],
            model="llama3-groq-70b-8192-tool-use-preview",
        )
        hi = chat_completion.choices[0].message.content
        return {"response": hi}
    except Exception as error:
        return {"Error": str(error)}

@app.get("/")
async def root():
    return {"Hello": "World"}
@app.post("/get-response")
async def get_response(request: QueryRequest):
    query = request.query
    id = request.id
    all_ans =[]
    value = query_mongo(query, id)
    all_ans += value
    if request.synonym:
        extracted_words=process_query(query)
        for word in extracted_words:
            res = search_epub_chunk(id,word)
            all_ans+=res

    if request.ranking:
        print("hi")
        extracted =  get_data(id,query)
        all_ans += extracted
        clean= await clean_data(all_ans)

        ranked = get_ranked_answers(generate_embedding(query),clean)
        return ranked
    if all_ans:
        for answer in all_ans:
            if 'embedding' in answer:
                del answer['embedding']

        clean = await clean_data(all_ans)
        sorted_data = sorted(clean, key=lambda x: x['number'])
        return sorted_data

    return {"Error": "No such data"}
