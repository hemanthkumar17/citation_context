
import glob
import os


import fitz
from langchain.embeddings import HuggingFaceBgeEmbeddings, CacheBackedEmbeddings
from langchain.storage import LocalFileStore
import re

base_path = "arxiv_mine/"

def embed_text(text, cache_name):
    model_name = "BAAI/bge-small-en"
    model_kwargs = {"device": "cpu"}
    encode_kwargs = {"normalize_embeddings": True}
    hf = HuggingFaceBgeEmbeddings(
        model_name=model_name, model_kwargs=model_kwargs, encode_kwargs=encode_kwargs)

    fs = LocalFileStore("./cache/" + cache_name)

    cached_embedder = CacheBackedEmbeddings.from_bytes_store(
        hf, fs, namespace=model_name
    )

    return cached_embedder.embed_documents(text)

def get_labels(text):
    m = re.search(r"\[([A-Za-z0-9_]+)\]", s)

def main():
    print(next(os.walk(base_path))[1])
    for folder in next(os.walk(base_path))[1]:
        base_directory = base_path + folder
        file = glob.glob(base_directory + "/*.pdf")[0]

        doc = fitz.open(file)
        blocks = []
        for page in doc:
            blocks += page.get_text("blocks")

        # print(blocks)
        # break
        blocks = [b[4] for b in blocks if len(b[4].replace("\n", " ").split(" ")) > 20 and not (b[4][0] == "[" and (b[4][2] == "]" or b[4][3] == "]" or b[4][4] == "]"))]
        print(len(blocks))
        embeddings = embed_text(blocks, folder)
        print(len(embeddings))

        break

if __name__ == "__main__":
    main()