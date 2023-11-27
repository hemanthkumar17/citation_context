
import pandas as pd
import fitz
import glob

base_path = "arxiv_mine/"

def get_reference_vectors(row):
    print(row)
    ref_filename = row["label"]
    filename = row["file_name"]
    print(ref_filename)
    if ref_filename:
        directory = base_path + filename.split(".")[-2].replace("_", " ") + "/references"
        print(directory)
        file = None
        for x in glob.glob(directory + "/*.pdf"):
            if ref_filename.replace(" ", "_").lower() in x.lower():
                file = x
                break
        if not file:
            print("Reference file not found")
            return
        
        doc = fitz.open(file)
        blocks = []
        for page in doc:
            blocks += page.get_text("blocks")
        processed_blocks = [b[4].replace("\n", " ") for b in blocks if len(b[4].replace("\n", " ").split(" ")) > 20 and not (b[4][0] == "[" and (b[4][2] == "]" or b[4][3] == "]" or b[4][4] == "]"))]
        print("processed")

def format_data(data):
    citation_data = pd.read_parquet(data).explode("label", ignore_index=True).fillna("")
    # for data in citation_data:
    #     print(data)
    #     break
    print(citation_data["label"])
    citation_data.apply(get_reference_vectors, axis=1)

if __name__ == "__main__":
    format_data("citation_context.parquet")