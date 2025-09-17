from typing import List
import re
import spacy
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

# load lightweight English model once
_nlp = spacy.load("en_core_web_sm")
_stop = set(stopwords.words("english"))
_word = re.compile(r"[a-z]+")

def normalize(text: str) -> str:
    text = text.lower()
    tokens = [w for w in word_tokenize(text) if _word.fullmatch(w)]
    tokens = [t for t in tokens if t not in _stop]
    # lemmatize with spaCy
    doc = _nlp(" ".join(tokens))
    lemmas = [tok.lemma_ for tok in doc if tok.lemma_ not in _stop and len(tok.lemma_) > 1]
    return " ".join(lemmas)

def batch_normalize(texts: List[str]) -> List[str]:
    return [normalize(t) for t in texts]

#This function contains a simple test where it:
def main():
    # Test the normalize function
    test_text = "Running runs better than walked!"
    print("Original Text:", test_text)
    print("Normalized Text:", normalize(test_text))

    # Test the batch_normalize function
    texts = [
        "I love coding!",
        "Running is fun!",
        "Natural Language Processing is great."
    ]
    print("\nBatch Normalized Texts:")
    print(batch_normalize(texts))

#This ensures that the main() function is only called when the script is executed directly
#(not when it is imported as a module)
if __name__ == "__main__":
    main()