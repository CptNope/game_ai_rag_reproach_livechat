
from sentence_transformers import SentenceTransformer
import numpy as np

model = SentenceTransformer('all-MiniLM-L6-v2')

def embed_text(text):
    return model.encode(text)

if __name__ == "__main__":
    vec = embed_text("jump over the lava pit")
    print(vec)
