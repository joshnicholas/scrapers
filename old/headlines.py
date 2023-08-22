# %%
# import requests
import pandas as pd 

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.neighbors import NearestNeighbors
from tfidf_matcher.ngrams import ngrams
import pathlib
import os 
pathos = pathlib.Path(__file__).parent
os.chdir(pathos)

# %%


urls = ["https://raw.githubusercontent.com/joshnicholas/Archives/main/Archive/abc_top/latest.json",
"https://raw.githubusercontent.com/joshnicholas/Archives/main/Archive/graun_top/latest.json",
"https://raw.githubusercontent.com/joshnicholas/Archives/main/Archive/sbs_top/latest.json"]


listo = []

for urlo in urls:
    inter = pd.read_json(urlo)
    listo.append(inter)
    # print(inter)
    # print(inter.columns.tolist())
    # 'publication', 'scraped_datetime', 'Headline', 'Url', 'Rank'

# %%

cat = pd.concat(listo)
cat = cat[['publication', 'scraped_datetime', 'Headline', 'Url', 'Rank']]
print(cat)
# %%


def matcher(frame, col, outname='Original', ngram_length=3, cutoff=0.8):

    copier = frame.copy()
    original= frame[col].unique().tolist()
    k_matches=len(original)

    lookup = original

    original_lower = [x.lower() for x in original]
    lookup_lower = [x.lower() for x in lookup]

    # Set ngram length for TfidfVectorizer callable
    def ngrams_user(string, n=ngram_length):
        return ngrams(string, n)

    # Generate Sparse TFIDF matrix from Lookup corpus
    vectorizer = TfidfVectorizer(min_df=1, analyzer=ngrams_user)

    # # Generate Sparse TFIDF matrix from Lookup corpus
    # vectorizer = TfidfVectorizer(min_df=1, analyzer='word')
    tf_idf_lookup = vectorizer.fit_transform(lookup_lower)

    # Fit KNN model to sparse TFIDF matrix generated from Lookup
    nbrs = NearestNeighbors(n_neighbors=k_matches, n_jobs=-3, metric="cosine").fit(tf_idf_lookup)

    # Use nbrs model to obtain nearest matches in lookup dataset. Vectorize first.
    tf_idf_original = vectorizer.transform(original_lower)
    distances, lookup_indices = nbrs.kneighbors(tf_idf_original)
    records = []

    for i, lookup_index in enumerate(lookup_indices):

        keep = []
        for b in range(0, len(distances[i])):
            if (1 - distances[i][b]) > 0.3:
                keep.append(b)

        # print("Keep: ", keep)
        ### Work out howmany are similar
        sims = [1 - round(dist, 2) for dist in distances[i] if ((1 - round(dist, 2)) > 0.15)]

        if len(sims) > 1:

            group = (list(lookup_index[:len(sims)]))
            group.sort(reverse=True)
            group = [str(x) for x in group]
            group = ",".join(group)
        
        else:
            group = "0"

        record = {col: original[i], "Matches": group, "Num matches": len(sims)}

        records.append(record)

    cat = pd.DataFrame.from_records(records)
    cat.sort_values(by=[ 'Matches', 'Num matches'], ascending=False, inplace=True)

    return cat

test = matcher(cat,'Headline')
# %%


tog = pd.merge(cat, test, on='Headline', how='left')
tog.sort_values(by=[ 'Matches', 'Num matches'], ascending=False, inplace=True)
print(tog)
# %%


from sentence_transformers import SentenceTransformer, util
model = SentenceTransformer('all-MiniLM-L6-v2')

# sentences = ['A man is eating food.',
#           'A man is eating a piece of bread.',
#           'The girl is carrying a baby.',
#           'A man is riding a horse.',
#           'A woman is playing violin.',
#           'Two men pushed carts through the woods.',
#           'A man is riding a white horse on an enclosed ground.',
#           'A monkey is playing drums.',
#           'Someone in a gorilla costume is playing a set of drums.'
#           ]

sentences = cat['Headline'].unique().tolist()

#Encode all sentences
embeddings = model.encode(sentences)

#Compute cosine similarity between all pairs
cos_sim = util.cos_sim(embeddings, embeddings)

#Add all pairs to a list with their cosine similarity score
all_sentence_combinations = []
for i in range(len(cos_sim)-1):
    for j in range(i+1, len(cos_sim)):
        all_sentence_combinations.append([cos_sim[i][j], i, j])

#Sort list by the highest cosine similarity score
all_sentence_combinations = sorted(all_sentence_combinations, key=lambda x: x[0], reverse=True)

print("Top-5 most similar pairs:")
for score, i, j in all_sentence_combinations[0:5]:
    print("{} \t {} \t {:.4f}".format(sentences[i], sentences[j], cos_sim[i][j]))


# #Sentences are encoded by calling model.encode()
# emb1 = model.encode("This is a red cat with a hat.")
# emb2 = model.encode("Have you seen my red cat?")

# cos_sim = util.cos_sim(emb1, emb2)
# print("Cosine-Similarity:", cos_sim)
# %%

# https://www.sbert.net/examples/applications/semantic-search/README.html
from sentence_transformers import SentenceTransformer, util
# import torch

embedder = SentenceTransformer('all-MiniLM-L6-v2')

corpus = cat['Headline'].unique().tolist()

corpus_embeddings = embedder.encode(corpus, convert_to_tensor=True)

# print(corpus_embeddings)

records = []

# Find the closest sentences of the corpus for each in corpus based on cosine similarity
top_k = min(5, len(corpus))
for query in corpus:

    group = []
    query_embedding = embedder.encode(query, convert_to_tensor=True)

    # Alternatively, we can also use util.semantic_search to perform cosine similarty + topk
    hits = util.semantic_search(query_embedding, corpus_embeddings, top_k=5)
    hits = hits[0]      #Get the hits for the first query
    # print(hits)
    for hit in hits:
        if hit['score'] > 0.5:
            group.append(hit['corpus_id'])
            # print(corpus[hit['corpus_id']], "(Score: {:.4f})".format(hit['score']))

    lenno = len(group)
    group.sort(reverse=True)
    group = [str(x) for x in group]
    group = ",".join(group)

    record = {"Headline": query, "Matches": group, "Num matches": lenno}
    records.append(record)

test = pd.DataFrame.from_records(records)
test.sort_values(by=[ 'Matches', 'Num matches'], ascending=False, inplace=True)


tog = pd.merge(cat, test, on='Headline', how='left')
tog.sort_values(by=['Num matches', 'Matches'], ascending=False, inplace=True)
print(tog)
# %%


def send_to_git(stemmo, repo, what, frame):

    tokeny = os.environ['gitty']

    github = Github(tokeny)

    repository = github.get_user().get_repo(repo)

    jsony = frame.to_dict(orient='records')
    content = json.dumps(jsony)

    filename = f'Archive/{what}/daily_dumps/{stemmo}.json'
    latest = f'Archive/{what}/latest.json'

    def check_do(pathos):
        contents = repository.get_contents(pathos)

        fillos = [x.path.replace(f"{pathos}/", '') for x in contents]

        # print(pathos)
        # print("contents: ", contents)
        # print("fillos: ", fillos)
        return fillos

    def try_file(pathos):
        try:
            repository.get_contents(pathos)
            return True
        except UnknownObjectException as e:
            return False

    # latest_donners = check_do(f'Archive/{what}')
    # donners = check_do(f'Archive/{what}/daily_dumps')
    donners = try_file(filename)

    latters = repository.get_contents(latest)
    repository.update_file(latest, f"updated_scraped_file_{stemmo}", content, latters.sha)

    if donners == False:

        repository.create_file(filename, f"new_scraped_file_{stemmo}", content)