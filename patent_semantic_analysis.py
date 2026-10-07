import os
import json
from genericpath import isfile
from keybert import KeyBERT
from sentence_transformers import SentenceTransformer, util
from pypdf import PdfReader
import read_pdf

patent_path = ""
onlyfiles = [os.path.join(patent_path, f) for f in os.listdir(patent_path) if isfile(os.path.join(patent_path, f))]
kw_model = KeyBERT()

patent_codes=dict()

model = SentenceTransformer("all-MiniLM-L6-v2")
patent_classification_data=[]

reader = PdfReader("./cpc-scheme-H.pdf")


# Get the total number of pages
print(f"Total pages: {len(reader.pages)}")

def write_patent_data(patent_name, class_code, class_description, key_word, all_key_words):
    global patent_classification_data
    json_patent_data={"patent_name":patent_name, "classification_code":class_code, "classification_description":class_description, "most_significant_key_word":key_word, "all_key_words":all_key_words}
    patent_classification_data.append(json.dumps(json_patent_data, indent=4))

def save_patent_classification_data():
    global patent_classification_data
    with open('patent_classification.json', 'w') as f:
        for data in patent_classification_data:
            json.dump(json.loads(data), f, ensure_ascii=False, indent=4)


def get_similarity(text):
    global cpc_classification
    patent_similarities=[]
    for cpc in cpc_classification:
        embedding1 = model.encode(text, convert_to_tensor=True)
        embedding2 = model.encode(cpc[1], convert_to_tensor=True)
        similarity = util.cos_sim(embedding1, embedding2)
        patent_similarities.append([similarity, text, cpc[0], cpc[1]])
    return sorted(patent_similarities, key=lambda x: x[0])

def getKeyWords(phrase, patent_name):
    # Extract keywords and key phrases (using n-grams of size 1 to 2)
    patent_similarities=[]
    keywords = kw_model.extract_keywords(phrase, keyphrase_ngram_range=(1, 2), stop_words='english', top_n=10)
    for keyword, score in keywords:
        patent_similarities.extend(get_similarity(keyword))
    patent_similarities_sorted = sorted(patent_similarities, key=lambda x: x[0])
    patent_similarities_sorted.reverse()
    write_patent_data(patent_name, patent_similarities_sorted[0][2], patent_similarities_sorted[0][3],  patent_similarities_sorted[0][1], keywords)
    #read_pdf.write_data_to_worksheet(patent_name, patent_similarities_sorted[0][2], patent_similarities_sorted[0][1], patent_similarities_sorted[0][3], phrase)


def get_patent_keywords():
    with open(onlyfiles[0]) as f:
        phrase = f.read()
        getKeyWords(phrase, f.name)
    save_patent_classification_data()
    #read_pdf.close_workbook()


cpc_classification = read_pdf.extract_patent_codes()
get_patent_keywords()
