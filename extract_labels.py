
import glob
import os


import fitz
import re
from unidecode import unidecode
import pandas as pd
import shutil

from arxiv_utils import extract_refs_from_list

base_path = "arxiv_mine/"

def get_labels(text):
    return re.findall(r"\[([0-9_]+)\]", text)

def main():
    data = []
    # Make a centralized paper repo, with a mapping json
    ref = next(os.walk(base_path))[1]
    depth = 0
    next_ref = []
    for depth in range(10):
        for folder in ref:
            base_directory = base_path + folder
            file = glob.glob(base_directory + "/*.pdf")[0]
            # bibfile = glob.glob(base_directory + "/*.bibtex")[0]
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
            reference_dict = {int(x.split("]")[0][1:]): x for x in reference_blocks if x.count("]") < 4 and x.split("]")[0][1:].isnumeric()}
            print(reference_dict)
            print(len(processed_blocks))

            # with open(bibfile, "r") as f:
            #     string = f.read()
            #     # print(string)
            #     start = [m.start() for m in re.finditer('@', string)]
            #     end = [m.start() for m in re.finditer(',\n}\n', string)]

            #     references = []
            #     for s, e in zip(start, end):
            #         try:
            #             references.append(string[s:e].split("title = {")[1].split("},")[0].split(',')[0])
            #         except:
            #             print("Error for ", string[s:e])
            title_dict = {}
            # for key in reference_dict:
            #     for r in references:
            #         if r in reference_dict[key]:
            #             title_dict[key] = r
            #             continue
            title_dict = reference_dict
            if not title_dict:
                shutil.rmtree(base_directory)
                continue
            _, _, ref_map = extract_refs_from_list(title_dict.values(), base_directory)
            next_ref += ref_map.items()
            # Code to zip blocks with references using the reference_dict
            for block in processed_blocks:
                labels = get_labels(block)
                if not labels:
                    continue


                new_label = []
                ref_directory = []
                for label in labels:
                    if int(label) in title_dict:
                        if title_dict[int(label)] in ref_map:
                            new_label.append(label)
                            ref_directory.append(ref_map[title_dict[int(label)]])
                labels = new_label
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

        # embeddings = embed_text(blocks, folder)
    pandas_data = pd.DataFrame(data)
    print(pandas_data)
    pandas_data.to_parquet("citation_context.parquet")
    pass


if __name__ == "__main__":
    main()