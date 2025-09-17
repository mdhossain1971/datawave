from typing import List
import numpy as np
from sentence_transformers import SentenceTransformer

# cache model once (384 dims for all-MiniLM-L6-v2)
_model = SentenceTransformer("all-MiniLM-L6-v2")

def embed(texts: List[str]) -> np.ndarray:
    # returns float32 numpy array shape: (N, 384)
    X = _model.encode(texts, convert_to_numpy=True, normalize_embeddings=False)
    return X.astype("float32")

def embed_one(text: str) -> np.ndarray:
    return embed([text])


#This function contains a simple test where it:
def main():
    # Test the embed and embed_one functions
    texts = ["Hello, world!", "Sentence embeddings are cool.", "This is a test sentence."]

    # Testing embed function
    embeddings = embed(texts)
    print("Embeddings for multiple texts:")
    print(embeddings)

    # Testing embed_one function
    single_text = "This is a single test sentence."
    single_embedding = embed_one(single_text)
    print("\nEmbedding for a single text:")
    print(single_embedding)

#This ensures that the main() function is only called when the script is executed directly
#(not when it is imported as a module)
if __name__ == "__main__":
    main()