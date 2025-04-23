
from reproach import Retriever

retriever = Retriever.from_folder("reproach_index/docs")

def query(text, top_k=3):
    return retriever.retrieve(text, k=top_k)

if __name__ == "__main__":
    results = query("enemy on platform")
    for r in results:
        print(r["text"])
