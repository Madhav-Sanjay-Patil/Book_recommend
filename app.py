from flask import Flask,render_template,request
import pickle
import numpy as np

import os
import requests

def download_model_file(url, filename):
    if not os.path.exists(filename):
        print(f"Downloading {filename}...")
        r = requests.get(url)
        with open(filename, "wb") as f:
            f.write(r.content)
        print(f"Saved {filename}")
    else:
        print(f"{filename} already exists.")

# Download all required .pkl files
download_model_file("https://drive.google.com/uc?export=download&id=1AMmcRogrprHg_if30I5rGoNQdLJ6kqP-", "books.pkl")
download_model_file("https://drive.google.com/uc?export=download&id=1CIvEzMDaMdOmyAtsyQ1lYurxvF1XfxMC", "similarity_scores.pkl")
download_model_file("https://drive.google.com/uc?export=download&id=1OBPxhMgY9RcFU8R8Zl8HSwYlPH7OCZiK", "pt.pkl")
download_model_file("https://drive.google.com/uc?export=download&id=1kHcttmZqRD07OTx4IyHV91mIuEO2isQm", "popular.pkl")

# Add more as needed

popular_df = pickle.load(open('popular.pkl','rb'))
pt = pickle.load(open('pt.pkl','rb'))
books = pickle.load(open('books.pkl','rb'))
similarity_scores = pickle.load(open('similarity_scores.pkl','rb'))

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html',
                           book_name = list(popular_df['Book-Title'].values),
                           author=list(popular_df['Book-Author'].values),
                           image=list(popular_df['Image-URL-M'].values),
                           votes=list(popular_df['num_ratings'].values),
                           rating=list(popular_df['avg_rating'].values)
                           )

@app.route('/recommend')
def recommend_ui():
    return render_template('recommend.html', pt=pt)


@app.route('/recommend_books', methods=['POST'])
def recommend():
    user_input = request.form.get('user_input')
    
    try:
        # Get index of user input
        index = np.where(pt.index == user_input)[0][0]
        similar_items = sorted(list(enumerate(similarity_scores[index])), key=lambda x: x[1], reverse=True)[1:9]
        
        data = []
        for i in similar_items:
            item = []
            temp_df = books[books['Book-Title'] == pt.index[i[0]]]
            item.extend(list(temp_df.drop_duplicates('Book-Title')['Book-Title'].values))
            item.extend(list(temp_df.drop_duplicates('Book-Title')['Book-Author'].values))
            item.extend(list(temp_df.drop_duplicates('Book-Title')['Image-URL-M'].values))

            data.append(item)

        return render_template('recommend.html', data=data, pt=pt)

    except IndexError:
        return render_template('recommend.html', error="Book not found. Please select from dropdown.", pt=pt)


if __name__ == '__main__':
    app.run(debug=True)
