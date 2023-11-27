import os
import glob
import re
import arxiv
from tqdm import tqdm
import shutil
import argparse

base_path = "./arxiv_mine/"

def clean_refs():
    for file in glob.glob(base_path + "**/*.bibtex", recursive=True):
        print(file)
        directory = "/".join(file.split("/")[:-1]) + "/references"
        if os.path.exists(directory):
            shutil.rmtree(directory)

def extract_refs():
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
                    if not os.path.exists(directory + "/" + res.title):
                        os.mkdir(directory + "/" + res.title)
                    res.download_pdf(directory + "/" + res.title)
        print(f"Fraction found: {len(os.listdir(directory))} / {len(references)}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument("-c", "--clean", dest="clean", help="Clean references and extract", default = 0)
    args = parser.parse_args()
    print(args.clean)
    if args.clean == 1:
        clean_refs()
    extract_refs()
