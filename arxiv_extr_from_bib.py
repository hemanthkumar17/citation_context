import os
import glob
from pybtex.database.input import bibtex
import sys
import re
import arxiv
import time
from tqdm import tqdm
base_path = "./arxiv_mine/"

for file in glob.glob(base_path + "**/*.bibtex", recursive=True):
    print(file)
    directory = "/".join(file.split("/")[:-1]) + "/references"
    if not os.path.exists(directory):
        os.mkdir(directory)
    else:
        continue
    with open(file, "r") as f:
        string = f.read()
        # print(string)
        start = [m.start() for m in re.finditer('@', string)]
        end = [m.start() for m in re.finditer(',\n}\n', string)]

        references = []
        for s, e in zip(start, end):
            try:
                references.append(string[s:e].split("title = {")[1].split("},")[0])
            except:
                print("Error for ", string[s:e])
        print(len(references))
        

    client = arxiv.Client()
    query = "".join([f"ti:{x} OR " for x in references[:-1]]) + "ti:" + references[-1]

    for file in tqdm(references):
        search = arxiv.Search(
        query = f"ti:{file}",
        max_results = 5,
        )
        for res in client.results(search):
            # print()
            if all(map(res.title.lower().__contains__, file.lower().split())):
                res.download_pdf(directory)
    print(f"Fraction found: {len(os.listdir(directory))} / {len(references)}")