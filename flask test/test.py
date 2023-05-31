from flask import Flask, render_template, request, redirect, session, url_for
from flask import flash
import os

from random import sample

import mysql.connector
import pickle
import numpy as numpy

popular_df = pickle.load(open('popular.pkl','rb'))
pt = pickle.load(open('pt.pkl','rb'))
books = pickle.load(open('books.pkl','rb'))
similarity_scores = pickle.load(open('similarity_scores.pkl','rb'))


conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="snap"
    )

cursor = conn.cursor()


app = Flask(__name__)
app.secret_key = os.urandom(24)


@app.route("/")
def snap():
    popular_check = True
    logged_in = False

    if 'user_id' in session:
        logged_in = True
        cursor.execute("""SELECT * FROM `users_index` WHERE `username`='{}'""".format(session['user_id']))
        user_books=cursor.fetchall()
        print(user_books)
        if len(user_books)>0:
            popular_check = False

    if popular_check:
        return render_template('index.html',
                            popular = popular_check,
                            logged_in = logged_in,
                            book_name = list(popular_df['Book-Title'].values),
                            author = list(popular_df['Book-Author'].values),
                            image = list(popular_df['Image-URL-L'].values),
                            votes = list(popular_df['num_ratings'].values),
                            rating = list(popular_df['avg_rating'].values),
                            index = list(popular_df['index'].values)
                            )
    else:
        search_input = books[books['index']==user_books[0][1]]['Book-Title'].values[0]
        datas = getRecommended(search_input)
        for idx in range(1, len(user_books)):
            search_input = books[books['index']==user_books[idx][1]]['Book-Title'].values[0]
            extendRecommendation(datas,getRecommended(search_input))

        num_random = 8
        if num_random > len(datas):
            num_random = len(datas)
        return render_template('index.html',
                               logged_in = True,
                            popular = popular_check,
                            data = sample(datas, k = num_random)
                            )


@app.route("/popular")
def popular():
    logged_in = False
    if 'user_id' in session:
        logged_in = True
    return render_template('popular.html',
                           logged_in = logged_in,
                           book_name = list(popular_df['Book-Title'].values),
                           author = list(popular_df['Book-Author'].values),
                           image = list(popular_df['Image-URL-L'].values),
                           votes = list(popular_df['num_ratings'].values),
                           rating = list(popular_df['avg_rating'].values),
                           index = list(popular_df['index'].values)
                           )


@app.route("/login_validation", methods=['POST'])
def login_validation():
    email_username=request.form.get('email_username')
    password=request.form.get('password')
    

    cursor.execute("""SELECT * FROM `registered_users` WHERE `email`='{}' OR `username`='{}'""".format(email_username,email_username))

    users=cursor.fetchall()

    if len(users)>0:
        if password == users[0][2]:
            session['user_id']=users[0][0]

    return redirect(request.referrer or url_for('index'))



@app.route("/registration", methods=['POST'])
def registration():
    username=request.form.get('username')
    email=request.form.get('email')
    password=request.form.get('password')

    cursor.execute("""SELECT * FROM `registered_users` WHERE `email`='{}' OR `username`='{}'""".format(email,username))

    existing=cursor.fetchall()

    print(existing)
    if len(existing)>0:
        return redirect('/')
    else:
        cursor.execute("""INSERT INTO `registered_users`(`username`, `email`, `password`) VALUES ('{}','{}','{}')""".format(username,email,password))
        conn.commit()
        return redirect('/')




@app.route("/recommend")
def recommend_ui():
    logged_in = False
    if 'user_id' in session:
        logged_in = True
    return render_template('recommend.html', logged_in=logged_in)

@app.route("/recommend_books", methods=['POST','GET'])
def recommend():
    search_input = request.form.get('search_input')

    if search_input == None:
        return redirect("/recommend")
    
    data = getRecommended(search_input)
    return render_template('recommend.html',data=data)


@app.route("/capture_click/<int:item_id>")
def capture_click(item_id):
    print(item_id)
    if 'user_id' in session:
        print(session['user_id'])
        cursor.execute("""SELECT * FROM `users_index` WHERE `username`='{}' AND `book`='{}'""".format(session['user_id'],item_id))
        existing=cursor.fetchall()
        if len(existing)<1:
            cursor.execute("""INSERT INTO `users_index`(`username`, `book`) VALUES ('{}','{}')""".format(session['user_id'],item_id))
            conn.commit()
    return redirect(request.referrer or "/")


@app.route("/catalogue")
def catalogue():
    logged_in = False
    if 'user_id' in session:
        logged_in = True
    return render_template('catalogue.html',
                           logged_in = logged_in,
                            book_name = list(books['Book-Title'].values[1:1000]),
                            author = list(books['Book-Author'].values[1:1000]),
                            image = list(books['Image-URL-L'].values[1:1000]),
                            index = list(books['index'].values[1:1000])
                            )

@app.route("/logout")
def login():
    session.pop('user_id')
    return redirect(request.referrer or url_for('index'))


def getRecommended(search_input):
    try:
        index = numpy.where(pt.index == search_input)[0][0]
        similar_items = sorted(list(enumerate(similarity_scores[index])), key=lambda x: x[1], reverse=True)[1:11]

        data = []
        for i in similar_items:
            item = []
            temp_df = books[books['Book-Title'] == pt.index[i[0]]]
            item.extend(list(temp_df.drop_duplicates('Book-Title')['Book-Title'].values))
            item.extend(list(temp_df.drop_duplicates('Book-Title')['Book-Author'].values))
            item.extend(list(temp_df.drop_duplicates('Book-Title')['Image-URL-L'].values))
            item.extend(list(temp_df.drop_duplicates('Book-Title')['index'].values))

            data.append(item)
        
        return data
    except:
        return []

def extendRecommendation(data1, data2):
    for val2 in data2:
        append = True
        for val1 in data1:
            if val1[3] == val2[3]:
                append = False
                break
        if(append):
            data1.append(val2)


if __name__ == '__main__':
    app.run(debug=True)