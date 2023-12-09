
import glob
import os


import fitz
from langchain.embeddings import HuggingFaceBgeEmbeddings, CacheBackedEmbeddings
from langchain.storage import LocalFileStore
import re
from unidecode import unidecode
import pandas as pd
import shutil
import lxml.etree as et
from bs4 import BeautifulSoup
import json

from arxiv_utils import extract_refs_from_list, ArxivHandler

base_path = "arxiv_data"

def get_labels(text):
    return re.findall(r"\[([0-9_]+)\]", text)

def allTextNodes(root):
    if root.text is not None:
        yield root.text
    for child in root:
        yield child.attrib["rid"]
        if child.tail is not None:
            yield child.tail

class JatsParser():
    # Roadmap
    # ~Done~ 1. Parse blocks into content and references
    # ~Done~ 2. Get reference title list and their respective tagging information
    # 3. Download reference list
    # 4. Identify reference tags in each block and add them to the dataset
    # 5. Continue this for a list of all references downloaded in a BFS fashion
    
    def __init__(self, base_directory):
        self.directory = base_directory
        self.ref_graph = {}
        self.ah = ArxivHandler()

    def get_referencelist(self, blocks, ref_mapper, download_dir = None):
        # Given blocks in a single file, a reference mapper to source/title, 
        #  ++ Download the respective references and return a mapper for reference to directory
        # (OR) create a mapping to arxiv id, and maintain a separate mapper for ID to directory
        if not download_dir:
            download_dir = self.directory
        re_ex = r"(ref[0-9]+)"
        block_to_ref = {}
        ref_to_dir = {}
        for block in blocks:
            res = re.findall(re_ex, block)
            if res:
                for ref in res:
                    if ref in ref_mapper and ref not in ref_to_dir:
                        if ref_mapper[ref][1]:
                            dir = self.ah.download_arxiv_from_id(ref_mapper[ref][1], download_dir)
                            if not dir and ref_mapper[ref][0]:
                                dir = self.ah.download_arxiv_from_title(ref_mapper[ref][0], download_dir)
                        else:
                            dir = self.ah.download_arxiv_from_title(ref_mapper[ref][0], download_dir)
                        ref_to_dir[ref] = dir

        return ref_to_dir

    def get_ref_mapper(self, file):
        # Given a file, get all the blocks in reference section
        # This includes the source (Arxiv: ID) and/or Title
        # Returns "refid": (title, source)
        tree = et.parse(file)
        root = tree.getroot()
        ref_map = {}
        for x in root.iter("ref-list"):
            for ref in x.xpath("//ref"):
                try:
                    title = next(ref.iter("article-title")).text
                except:
                    title = None
                try: 
                    source = next(ref.iter("source")).text
                except: 
                    source = None
                if not title and not source:
                    pass
                else:
                    ref_map[ref.attrib.values()[0]] = (title, source)
        return ref_map
    
    def get_data(self, blocks, ref_to_dir):
        re_ex = r"(ref[0-9]+)"
        result = []
        for block in blocks:
            res = re.findall(re_ex, block)
            if res:
                for ref in res:
                    if ref in ref_to_dir and ref_to_dir[ref]:
                        result.append((block, ref_to_dir[ref]))
        return result

    def get_blocks(self, file):
        # Given file, get the text blocks relevant to the intended training data
        tree = et.parse(file)
        root = tree.getroot()
        blocks = []
        for x in root.iter("sec"):
            # print(list(x))
            for block in x.xpath("//p"):
                blocks.append("".join(allTextNodes(block)))
        return blocks

def extract_block_reference():

    data = []
    with open(f"metadata_{base_path}.json", "w") as f:
        try:
            ref_map_json = json.load(f)
        except IOError:
            ref_map_json = {}    
        for folder in next(os.walk(base_path))[1]:
            file_dir = base_path + "/" + folder
            file = glob.glob(file_dir + "/*.cermxml")
            if file:
                file = file[0]
            else:
                continue

            jp = JatsParser(base_path)
            

            if file in ref_map_json:
                print("Skipped " + file)
                continue
                
            print(ref_map_json)
            blocks = jp.get_blocks(file)
            ref_map = jp.get_ref_mapper(file=file)
            print(ref_map)
            ref_to_dir = jp.get_referencelist(blocks, ref_map)
            ref_map_json[file] = ref_to_dir
            print(ref_map_json)
            # print(blocks)

            data = data + [(file) + x for x in jp.get_data(blocks, ref_to_dir)]
            print(data)
        json.dump(ref_map_json, f)
        # break
    pd.DataFrame(data, columns=['origin_dir', 'block', "reference_dir"]).to_csv("citation_data.csv")
    
def main():
    extract_block_reference()

if __name__ == "__main__":
    main()