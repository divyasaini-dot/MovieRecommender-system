import streamlit as st
import pickle
import pandas as pd
import ast
import joblib

OMDB_API_KEY = st.secrets["16336354"]
import requests

def fetch_movie_details(movie_title):
    url = f"http://www.omdbapi.com/?t={movie_title}&apikey={OMDB_API_KEY}"
    data = requests.get(url).json()

    if data.get("Response") == "True":
        return {
            "poster": data.get("Poster")
        }
    else:
        return {
            "poster": "https://via.placeholder.com/300x450?text=No+Poster"
        }

def get_selected_movie_details(movie_title):
    movie = movies[movies['title'] == movie_title].iloc[0]

    details = fetch_movie_details(movie_title)

    return {
        "poster": details["poster"],
        "rating": movie.vote_average,
        "genre": movie.genres,
        "year": movie.release_date[:4]
    }

def recommend(movie):
    movie_index = movies[movies['title'] == movie].index[0]
    distances = similarity[movie_index]

    movies_list = sorted(
        list(enumerate(distances)),
        reverse=True,
        key=lambda x: x[1]
    )[1:11]

    recommended_movies = []
    posters = []
    ratings = []
    genres = []
    years = []
    scores = []

    max_similarity = movies_list[0][1] if movies_list[0][1] != 0 else 1

    for i in movies_list:
        movie = movies.iloc[i[0]]

        details = fetch_movie_details(movie.title)
        match = round((i[1] / max_similarity) * 100, 1)
        recommended_movies.append(movie.title)
        posters.append(details["poster"])

        # Use your dataset
        ratings.append(movie.vote_average)
        genres.append(movie.genres)
        years.append(movie.release_date[:4])
        scores.append(match)

    return recommended_movies, posters, ratings, genres, years, scores
movies_dict = pickle.load(open('movies_dict.pkl', 'rb'))
movies = pd.DataFrame(movies_dict)
def clean_genres(x):
    if isinstance(x, str):
        x = ast.literal_eval(x)
    return " • ".join(x)

movies["genres"] = movies["genres"].apply(clean_genres)
similarity = joblib.load('similarity.joblib')
# Store search history
if "history" not in st.session_state:
    st.session_state.history = []

st.set_page_config(
    page_title="Movie Recommender",
    page_icon="🍿",
    layout="wide"
)
st.sidebar.title("📚 About Project")

with st.sidebar.expander("📊 Dataset"):
    st.write("""
    TMDB 5000 Movie Dataset
    - 5000 Movies
    - Genres
    - Cast
    - Crew
    - Keywords
    """)

with st.sidebar.expander("🤖 Content-Based Filtering"):
    st.write("""
    Movies are recommended based on
    similarity of movie features instead
    of user ratings.
    """)

with st.sidebar.expander("🔤 CountVectorizer"):
    st.write("""
    Converts movie tags into numerical vectors
    using the Bag of Words approach.
    """)

with st.sidebar.expander("📐 Cosine Similarity"):
    st.write("""
    Calculates the similarity between
    movie vectors.

    Higher value = More similar movies.
    """)

with st.sidebar.expander("🎯 Workflow"):
    st.markdown("""
    **Recommendation Process**

    1. 🎬 Select a Movie
    2. 🏷️ Generate Tags
    3. 🔤 Apply CountVectorizer
    4. 📐 Compute Cosine Similarity
    5. 🎯 Display Top 10 Recommendations
    """)
st.sidebar.markdown("---")
st.sidebar.subheader("🕒 Recently Searched")

if st.session_state.history:
    for i, movie in enumerate(st.session_state.history, start=1):
        st.sidebar.markdown(f"**{i}.** 🎬 {movie}")
else:
    st.sidebar.info("No searches yet.")

st.title("Movie Recommender System")

selected_movie_name  = st.selectbox("🎬 Select a Movie", movies['title'].values)

if st.button("🔍 Find Similar Movies"):
    if selected_movie_name not in st.session_state.history:
        st.session_state.history.insert(0, selected_movie_name)

    st.session_state.history = st.session_state.history[:5]
    selected = get_selected_movie_details(selected_movie_name)

    with st.container(border=True):
        st.subheader("🎞️ Selected Movie")

        col1, col2 = st.columns([1, 3])

        with col1:
            st.image(selected["poster"], width=220)

        with col2:
            st.markdown(f"## {selected_movie_name}")
            st.write(f"⭐ **{selected['rating']}/10**")
            st.write(f"🎭 {selected['genre']}")
            st.write(f"📅 {selected['year']}")
        st.markdown("---")
        st.subheader("🍿 Recommended Movies")
    with st.spinner("Finding similar movies... 🍿"):
        names, posters, ratings, genres, years, scores = recommend(selected_movie_name)

    cols = st.columns(5)

    for i in range(5):
        with cols[i]:
            st.image(posters[i])
            st.markdown(f"**{names[i]}**")
            st.caption(f"🔥 {scores[i]}% Match")
            st.caption(f"⭐ {ratings[i]}/10")
            st.caption(f"🎭 {genres[i]}")
            st.caption(f"📅 {years[i]}")

    cols = st.columns(5)

    for i in range(5,10):
        with cols[i-5]:
            st.image(posters[i])
            st.markdown(f"**{names[i]}**")
            st.caption(f"🔥 {scores[i]}% Match")
            st.caption(f"⭐ {ratings[i]}/10")
            st.caption(f"🎭 {genres[i]}")
            st.caption(f"📅 {years[i]}")


st.markdown("---")
st.caption(
    "✨ Movie Recommendation System | Built with Streamlit & Scikit-Learn"
)