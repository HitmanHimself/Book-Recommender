import numpy as numpy;
import pandas as pandas;

books_csv = pandas.read_csv("./dataset/Books.csv");
users_csv = pandas.read_csv("./dataset/Users.csv");
ratings_csv = pandas.read_csv("./dataset/Ratings.csv");


ratings_with_name = ratings_csv.merge(books_csv,on='ISBN');

books_csv = books_csv.drop_duplicates('Book-Title');

books_csv.reset_index()
books_csv['index'] = range(0, len(books_csv))
import pickle
pickle.dump(books_csv,open('books.pkl','wb'))
print(books_csv)

num_rating_df = ratings_with_name.groupby('Book-Title')['Book-Rating'].count().reset_index()
num_rating_df.rename(columns={'Book-Rating':'num_ratings'},inplace=True)

avg_rating_df = ratings_with_name.groupby('Book-Title')['Book-Rating'].mean().reset_index()
avg_rating_df.rename(columns={'Book-Rating':'avg_rating'},inplace=True)

popular_df = num_rating_df.merge(avg_rating_df,on='Book-Title')


popular_df = popular_df[popular_df['num_ratings']>=100].sort_values('avg_rating',ascending=False).head(100)


popular_df = popular_df.merge(books_csv,on='Book-Title')[['Book-Title','Book-Author','Image-URL-L','num_ratings','avg_rating','index']]
print(popular_df)

import pickle;

pickle.dump(popular_df,open('popular.pkl','wb'));



# x = ratings_with_name.groupby('User-ID').count()['Book-Rating'] > 200
# padhe_likhe_users = x[x].index

# filtered_rating = ratings_with_name[ratings_with_name['User-ID'].isin(padhe_likhe_users)]


# y = filtered_rating.groupby('Book-Title').count()['Book-Rating']>=50
# famous_books = y[y].index


# final_ratings = filtered_rating[filtered_rating['Book-Title'].isin(famous_books)]


# pt = final_ratings.pivot_table(index='Book-Title',columns='User-ID',values='Book-Rating')


# pt.fillna(0,inplace=True)


# from sklearn.metrics.pairwise import cosine_similarity


# similarity_scores = cosine_similarity(pt)


# similarity_scores.shape

# pickle.dump(pt,open('pt.pkl','wb'))
# pickle.dump(books_csv,open('books.pkl','wb'))
# pickle.dump(similarity_scores,open('similarity_scores.pkl','wb'))

# def recommend(book_name):
#     # index fetch
#     index = numpy.where(pt.index==book_name)[0][0]
#     similar_items = sorted(list(enumerate(similarity_scores[index])),key=lambda x:x[1],reverse=True)[1:5]
    
#     data = []
#     for i in similar_items:
#         item = []
#         temp_df = books_csv[books_csv['Book-Title'] == pt.index[i[0]]]
#         item.extend(list(temp_df.drop_duplicates('Book-Title')['Book-Title'].values))
#         item.extend(list(temp_df.drop_duplicates('Book-Title')['Book-Author'].values))
#         item.extend(list(temp_df.drop_duplicates('Book-Title')['Image-URL-M'].values))
        
#         data.append(item)
    
#     return data