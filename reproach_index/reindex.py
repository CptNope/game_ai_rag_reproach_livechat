
from reproach import Retriever, Document
import os
import json

DOCS_PATH = "reproach_index/docs"

def load_all_documents(path):
    docs = []
    for file in os.listdir(path):
        if file.endswith(".json"):
            with open(os.path.join(path, file), "r") as f:
                data = json.load(f)
                docs.append(Document(id=data["id"], text=data["text"]))
    return docs

def reindex():
    print("Reindexing documents...")
    documents = load_all_documents(DOCS_PATH)
    retriever = Retriever.from_documents(documents)
    retriever.save(DOCS_PATH)
    print(f"Reindexed {len(documents)} documents.")

if __name__ == "__main__":
    reindex()
