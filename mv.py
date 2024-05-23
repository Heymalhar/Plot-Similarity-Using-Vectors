# This code is using a sample dataset on MongoDB Atlas, the details for which have been shared in the underlying code

import os
from dotenv import load_dotenv
import pymongo
import requests

load_dotenv()

# Use a .env file to store important passwords, keys and tokens
password = os.getenv("MONGODB_PASS")
hf_token = os.getenv("HF_TOKEN")

client = pymongo.MongoClient("<your_connection_url")
db = client.sample_mflix
collection = db.movies

embedding_url = "https://api-inference.huggingface.co/pipeline/feature-extraction/sentence-transformers/all-MiniLM-L6-v2"

def generate_embedding(text: str) -> list[float]:

    response = requests.post(
        embedding_url,
        headers={"Authorization": f"Bearer {hf_token}"},
        json={"inputs": text}
    )

    if response.status_code != 200:
        raise ValueError(f"Request failed with status code {response.status_code}: {response.text}")

    return response.json()

print(" ")
query = input("Enter the keywords: ")
print(" ")

for doc in collection.find({'plot':{"$exists": True}}).limit(50):
	doc['plot_embedding_hf'] = generate_embedding(doc['plot'])
	collection.replace_one({'_id': doc['_id']}, doc)

# Refer 'VectorSearch.txt' for details regarding the Vector Search Index

results = collection.aggregate([
  {"$vectorSearch": {
    "queryVector": generate_embedding(query),
    "path": "plot_embedding_hf",
    "numCandidates": 100,
    "limit": 4,
    "index": "PlotSemanticSearch",
   }}
])

for document in results:
    print(f'Movie Name: {document["title"]},\nMovie Plot: {document["plot"]}\n')