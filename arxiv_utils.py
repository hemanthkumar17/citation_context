import arxiv
import os
import re
from tqdm import tqdm
import shutil
import json
from sklearn.metrics import jaccard_score

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
def jaccard_similarity(list1, list2):
    intersection = len(list(set(list1).intersection(list2)))
    union = (len(set(list1)) + len(set(list2))) - intersection
    return float(intersection) / union
class ArxivHandler():
    def __init__(self) -> None:
        self.client = arxiv.Client()

    def download_arxiv_from_id(self, id_string, directory):
        reg = r"([0-9]{4}[.][0-9]{5})"
        id = re.findall(reg, id_string.lower().replace(" ", ""))
        if not id:
            return None
        id = id[0]
        search = arxiv.Search(
        id_list=[id],
        # max_results = 10,    # Expand search if needed to more than 5 results, but practically, 5 is a good threshold
        )
        for res in self.client.results(search):
            if not os.path.exists(directory + "/" + res.title):
                os.mkdir(directory + "/" + res.title)
            res.download_pdf(directory + "/" + res.title)
            return directory + "/" + res.title
        return None
        
    def download_arxiv_from_title(self, title, directory):
        search = arxiv.Search(
        query = f"ti:{title}",
        max_results = 10,    # Expand search if needed to more than 5 results, but practically, 5 is a good threshold
        )
        for res in self.client.results(search):
            if jaccard_similarity(res.title.lower().split(), title.lower().split()) > 0.8:
                if not os.path.exists(directory + "/" + res.title):
                    os.mkdir(directory + "/" + res.title)
                res.download_pdf(directory + "/" + res.title)
                return directory + "/" + res.title
        return None

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
            pass
        else:
            with open(directory + "/mapping.json", "r") as f:
                # os.remove(directory + "/mapping.json")
                return None, None, json.load(f)
# 
    client = arxiv.Client()
    # query = "".join([f"ti:{x} OR " for x in references[:-1]]) + "ti:" + references[-1]
    ref_mapping = {}

    for file in tqdm(references):
        print("Searching: ", file)
        reg = r"([0-9]{4}[.][0-9]{5})"
        id = re.findall(reg, file.lower().replace(" ", ""))
        if id:
            id = id[0]
            search = arxiv.Search(
            id_list=[id],
            # max_results = 10,    # Expand search if needed to more than 5 results, but practically, 5 is a good threshold
            )
            for res in client.results(search):
                if not os.path.exists(directory + "/" + res.title):
                    os.mkdir(directory + "/" + res.title)
                res.download_pdf(directory + "/" + res.title)
                ref_mapping[file] = directory + "/" + res.title
        else:
            search = arxiv.Search(
            query = f"ti:{file}",
            max_results = 10,    # Expand search if needed to more than 5 results, but practically, 5 is a good threshold
            )
            for res in client.results(search):
                if jaccard_score(res.title.lower().split(), file.lower().split()) > 0.8:
                    if not os.path.exists(directory + "/" + res.title):
                        os.mkdir(directory + "/" + res.title)
                    res.download_pdf(directory + "/" + res.title)
                    ref_mapping[file] = directory + "/" + res.title
    print(f"Fraction found: {len(os.listdir(directory))} / {len(references)}")
    with open(directory + "/mapping.json", "w") as f:
        json.dump(ref_mapping, f)
    return (len(os.listdir(directory)),  len(references), ref_mapping)