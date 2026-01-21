import pickle
import pandas as pd
import streamlit as st
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# --- 1. SETUP RETRY LOGIC ---
session = requests.Session()
retries = Retry(
    total=5,
    backoff_factor=1,
    status_forcelist=[500, 502, 503, 504]
)
session.mount('https://', HTTPAdapter(max_retries=retries))

def fetch_poster(movie_id):
    try:
        url = "https://api.themoviedb.org/3/movie/{}?api_key=68dc896b125af39c30c3f528c26ea323&language=en-US".format(movie_id)
        response = session.get(url, timeout=10)
        data = response.json()
        poster_path = data.get('poster_path')

        if poster_path:
            return "https://image.tmdb.org/t/p/w500/" + poster_path
        else:
            return "https://via.placeholder.com/500x750?text=No+Poster+Found"
    except Exception:
        return "https://via.placeholder.com/500x750?text=Connection+Error"

def recommend(movie):
    movie_index = movies[movies['title'] == movie].index[0]
    distances = similarity[movie_index]
    # Fetching 10 movies
    movies_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:11]

    recommended_movies_names = []
    recommended_movies_posters = []

    for i in movies_list:
        movie_id = movies.iloc[i[0]].movie_id
        recommended_movies_posters.append(fetch_poster(movie_id))
        recommended_movies_names.append(movies.iloc[i[0]].title)

    return recommended_movies_names, recommended_movies_posters

# --- 2. DATA LOADING ---
movies_dct = pickle.load(open('movie_dct.pkl', 'rb'))
movies = pd.DataFrame(movies_dct)
similarity = pickle.load(open('similarity.pkl', 'rb'))

# --- 3. STREAMLIT UI SETUP ---
st.set_page_config(page_title="Movie Recommender", layout="wide")

# Sidebar Help Section
st.sidebar.title("Help & Info")
st.sidebar.info("""
This system uses **Content-Based Filtering** to recommend movies.
1. Select a movie you like.
2. Click 'Show Recommendation'.
3. Our AI finds the top 10 most similar movies for you.
""")

st.title(" Movie Recommender System")

# Custom Styling for the text labels
st.markdown("""
    <style>
    .movie-font {
        font-size:18px !important;
        font-weight: bold;
        color: #E50914;
    }
    </style>
    """, unsafe_allow_html=True)

selected_movie_name = st.selectbox(
    "Select a movie to get recommendations:",
    movies['title'].values
)

if st.button('Show Recommendation'):
    names, posters = recommend(selected_movie_name)

    # Row 1
    col_row1 = st.columns(5)
    for i in range(0, 5):
        with col_row1[i]:
            st.markdown(f'<p class="movie-font">{names[i]}</p>', unsafe_allow_html=True)
            st.image(posters[i])

    st.markdown("---")

    # Row 2
    col_row2 = st.columns(5)
    for i in range(5, 10):
        with col_row2[i - 5]:
            st.markdown(f'<p class="movie-font">{names[i]}</p>', unsafe_allow_html=True)
            st.image(posters[i])

# --- 4. FOOTER & RIGHTS RESERVED ---
st.markdown("<br><br><br>", unsafe_allow_html=True) # Add some space
st.markdown("---")
footer = """
    <div style="text-align: center;">
        <p>© 2026 Movie Recommender AI. All Rights Reserved.</p>
        <p style='font-size: 0.8em;'>For technical support, contact us at help@recommender.com</p>
    </div>
"""
st.markdown(footer, unsafe_allow_html=True)
