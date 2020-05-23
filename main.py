import pandas as pd
import spacy
import pickle
from nltk.corpus import stopwords

"""Created this script to create pickle object for further recommendations without vectorizing each time
   Tested different kernel's and TfidfVectorizer as well as CountVectorizer
   I have choosen sigmoid kernel and TfidfVectorizer empirically
"""

russian_stopwords = stopwords.words("russian")

df = pd.read_csv('songs_dataset.csv')

nlp = spacy.load("en_core_web_sm", disable=["tagger", "parser"])

cool_df = df[(df.Singer == 'Noize MC') | (df.Singer == 'Anacondaz')].reset_index()

def clean_lyrics(text):
    text = text.lower()
    text = nlp(text)
    text = [t.text for t in text if t.is_alpha and not t.is_stop]
    text = ' '.join(text)
    return(text)

cool_df["Lyrics"] = cool_df["Lyrics"].apply(clean_lyrics)

from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer

cv = CountVectorizer(min_df=5, stop_words=russian_stopwords, ngram_range=(1,3))

tfv = TfidfVectorizer(min_df=5, ngram_range=(1,3), stop_words=russian_stopwords)

tfv_matrix = tfv.fit_transform(cool_df['Lyrics'])

from sklearn.metrics.pairwise import linear_kernel, sigmoid_kernel, cosine_similarity

sig_kernel = sigmoid_kernel(tfv_matrix, tfv_matrix)

with open('sig_kernel', 'wb') as f:
    pickle.dump(sig_kernel, f)

#Inverse mapping of Song names to indexes
indices = pd.Series(cool_df.index, index=cool_df['Song']).drop_duplicates()

def get_recommendations(title, cosine_sim, indices):
    #Receiving index
    idx = indices[title]
    #List of tuples containg song names and their indexes
    sim_scores = list(enumerate(cosine_sim[idx]))
    #Sorting
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
    #Selecting top 10
    sim_scores = sim_scores[1:11]
    #List of indexes to chose
    movie_indices = [i[0] for i in sim_scores]

    return cool_df['Song'].iloc[movie_indices]

print('Рекомендации к Ты знаешь кто он: \n{}'.format(get_recommendations('Ты знаешь, кто он', sig_kernel, indices)))
print('Рекомендации к Ты не считаешь: \n{}'.format(get_recommendations('Ты не считаешь', sig_kernel, indices)))
print('Рекомендации к Устрой дестрой: \n{}'.format(get_recommendations('Устрой дестрой', sig_kernel, indices)))