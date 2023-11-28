import arxiv
import os
import re
from tqdm import tqdm
import shutil
import json

def get_base_dataset(topic = "large language models", dataset_size=40, base_path = "./arxiv_mine"):
    search = arxiv.Search(
    query = topic,
    max_results = dataset_size,
    sort_by = arxiv.SortCriterion.Relevance
    )

    for result in arxiv.Client().results(search):
        print(result.title)
        directory = base_path + result.title
        if not os.path.exists(directory):
            os.mkdir(directory)
        paper = result.download_pdf(directory)
        print(paper)

def extract_refs_from_bibtex(bibfile):
    directory = "/".join(bibfile.split("/")[:-1]) + "/references"
    if not os.path.exists(directory):
        os.mkdir(directory)
    else:
        return
    with open(bibfile, "r") as f:
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
    
    return extract_refs_from_list(references, directory)

def extract_refs_from_list(references, directory):
    directory = directory + "/references"
    if not os.path.exists(directory):
        os.mkdir(directory)
    else:
        # return None, None, None
        if not os.path.isfile(directory + "/mapping.json"):
            shutil.rmtree(directory)
            os.mkdir(directory)
        else:
            with open(directory + "/mapping.json", "r") as f:
                return None, None, json.load(f)

    client = arxiv.Client()
    # query = "".join([f"ti:{x} OR " for x in references[:-1]]) + "ti:" + references[-1]
    ref_mapping = {}

    for file in tqdm(references):
        search = arxiv.Search(
        query = f"ti:{file}",
        max_results = 10,    # Expand search if needed to more than 5 results, but practically, 5 is a good threshold
        )
        for res in client.results(search):
            if all(map(res.title.lower().__contains__, file.lower().split())):
                if not os.path.exists(directory + "/" + res.title):
                    os.mkdir(directory + "/" + res.title)
                res.download_pdf(directory + "/" + res.title)
                ref_mapping[file] = directory + "/" + res.title
    print(f"Fraction found: {len(os.listdir(directory))} / {len(references)}")
    with open(directory + "/mapping.json", "w") as f:
        json.dump(ref_mapping, f)
    return (len(os.listdir(directory)),  len(references), ref_mapping)