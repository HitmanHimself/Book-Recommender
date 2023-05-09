import pandas as pd
import numpy as np  
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import CountVectorizer

df = pd.read_csv('dataset\Books.csv')

columns = ['Book-Title', 'Book-Title', 'Book-Title']

def combine_features(data):
    features = []
    for i in range(0, data.shape[0]) :
        features.append(str(data['Book-Title'][i]) + ' ' + str(data['Book-Author'][i]) + ' ' + str(data['Publisher'][i]))

    return features

cmb = combine_features(df)

cm = CountVectorizer().fit_transform(cmb)

cs = cosine_similarity(cm[:11110])


Title = df['Book-Title'][2143]

print(Title)


book_id = 2143

scores = list(enumerate(cs[book_id]))

sorted_scores = sorted(scores, key = lambda x : x[1], reverse = True)[1:]

j = 0;
for item in sorted_scores:
    book_title = df['Book-Title'][item[0]]
    print(book_title)
    j = j + 1
    if j > 5:
        break
