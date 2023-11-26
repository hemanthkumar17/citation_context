
import glob
import os

base_path = "arxiv_mine/"
ref_sum = 0
frac_list = []
for folder in next(os.walk(base_path))[1]:
    base_directory = base_path + folder
    file = len(glob.glob(base_directory + "/references/*.pdf"))
    ref_sum += file
    with open(glob.glob(base_directory + "/*.bibtex")[0], "r") as f:
        x = f.read()

        print(f"{file} / {x.count('author')} = {file / x.count('author')}")
        frac_list.append(file / x.count('author'))
print(f"Total references = {ref_sum}")
print(f"Average fraction of references extracted = {sum(frac_list) / len(frac_list)}")
    # break