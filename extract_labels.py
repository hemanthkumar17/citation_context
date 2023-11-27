
import glob
import os


import fitz
from langchain.embeddings import HuggingFaceBgeEmbeddings, CacheBackedEmbeddings
from langchain.storage import LocalFileStore
import re
from unidecode import unidecode
import pandas as pd

from arxiv_utils import extract_refs_from_list

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
    return re.findall(r"\[([0-9_]+)\]", text)

def main():
    print(next(os.walk(base_path))[1])
    data = []

    for folder in next(os.walk(base_path))[1]:
        base_directory = base_path + folder
        file = glob.glob(base_directory + "/*.pdf")[0]
        bibfile = glob.glob(base_directory + "/*.bibtex")[0]
        print(base_directory)
        doc = fitz.open(file)
        blocks = []
        for page in doc:
            blocks += page.get_text("blocks")

        # print(blocks)
        # break
        # blocks = [b[4].replace("\n", " ") for b in blocks if len(b[4].replace("\n", " ").split(" ")) > 20 and not (b[4][0] == "[" and (b[4][2] == "]" or b[4][3] == "]" or b[4][4] == "]"))]
        processed_blocks = [b[4].replace("\n", " ") for b in blocks if len(b[4].replace("\n", " ").split(" ")) > 20 and not (b[4][0] == "[" and (b[4][2] == "]" or b[4][3] == "]" or b[4][4] == "]"))]
        reference_blocks = [unidecode(b[4].replace("\n", " ")).replace("- ", "") for b in blocks if (b[4][0] == "[" and (b[4][2] == "]" or b[4][3] == "]" or b[4][4] == "]"))]
        
        
        reference_dict = {}
        # for x in reference_blocks:
        #     if "." in x and x.count("[") <= 1:
        #         title = [p for p in x.split(", ") if len(p.split(" ")) > 3 and p]
        #         reference_dict[int(x.split("]")[0][1:])] = title[0]
        #         print(title)

        # To-do: need fix for reference_dict
        reference_dict = {int(x.split("]")[0][1:]): x for x in reference_blocks if x.count("]") < 4}
        print(len(processed_blocks))
        print(reference_blocks)
        print(reference_dict)

        with open(bibfile, "r") as f:
            string = f.read()
            # print(string)
            start = [m.start() for m in re.finditer('@', string)]
            end = [m.start() for m in re.finditer(',\n}\n', string)]

            references = []
            for s, e in zip(start, end):
                try:
                    references.append(string[s:e].split("title = {")[1].split("},")[0].split(',')[0])
                except:
                    print("Error for ", string[s:e])
        title_dict = {}
        for key in reference_dict:
            for r in references:
                if r in reference_dict[key]:
                    title_dict[key] = r
                    continue

        # Code to zip blocks with references using the reference_dict
        for block in processed_blocks:
            labels = get_labels(block)
            if not labels:
                continue

            new_labels = []
            ref_directory = []
            for label in labels:
                if int(label) not in title_dict:
                    continue
                directory = base_directory + "/references/" + title_dict[int(label)]
                if os.path.isdir(directory):
                    new_labels.append(label)
                    ref_directory.append(directory)
            labels = new_labels

            if not labels:
                continue

            text = block
            for label in labels:
                text = text.replace(label, "")
            text = text.replace("[", "").replace("],", "").replace("]", "").replace("  ", "")
            original_text = block
            for label in labels:
                if int(label) not in title_dict:
                    continue
                original_text = original_text.replace("[" + label + "]", "[" + title_dict[int(label)] + "]")
            
            for label, dir in zip(labels, ref_directory):
                data.append({"text": text, "label": title_dict[int(label)], "original_text": original_text, "file_name": file, "ref_file_name": dir})
        print(data)

        # embeddings = embed_text(blocks, folder)
        # print(len(embeddings))
    pandas_data = pd.DataFrame(data)
    print(pandas_data)
    print(pandas_data["ref_file_name"])
    pandas_data.to_parquet("citation_context.parquet")
    pass


if __name__ == "__main__":
    main()