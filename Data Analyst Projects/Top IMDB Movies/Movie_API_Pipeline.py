import requests
import pandas as pd

# 2. Setup API Keys (Replace with your real keys)
OMDB_API_KEY = "your_omdb_key"
TMDB_API_KEY = "your_tmdb_key"

# extracted from kaggle dataset https://www.kaggle.com/datasets/georgescutelnicu/top-100-popular-movies-from-2003-to-2022-imdb
df = pd.read_csv("movies_raw_data.csv")

def fetch_omdb_data(title, year):
    '''Function to make API call to Open Movies DB and return the movie'''
    url = f"http://www.omdbapi.com/?t={title}&y={year}&apikey={OMDB_API_KEY}"
    response = requests.get(url)
    if response.ok:
        return response.json()
    return {}

def fetch_tmdb_movie_id(title):
    '''Function to make API call to The Movie DB and return the movie'''
    url = f"https://api.themoviedb.org/3/search/movie?api_key={TMDB_API_KEY}&query={title}"
    response = requests.get(url)
    if response.ok and response.json()['results']:
        return response.json()['results'][0]['id']
    return None

def fetch_tmdb_box_office(tmdb_id):
    '''Function to make API call to The Movie DB and return the movie and look up the
    box office performance stats'''
    url = f"https://api.themoviedb.org/3/movie/{tmdb_id}?api_key={TMDB_API_KEY}"
    response = requests.get(url)
    if response.ok:
        data = response.json()
        return {
            "revenue": data.get("revenue"),
            "budget": data.get("budget"),
            "popularity": data.get("popularity")
        }
    return {}

def check_awards(omdb_data):
    '''Function to make API call to Open Movies DB and check if it was nominated for an
    Oscar or Golden Globe, and if it actually won it or not'''
    awards = omdb_data.get("Awards", "")
    return {
        "won_oscar": "Oscar" in awards and "Won" in awards,
        "nominated_oscar": "Oscar" in awards and "Nominated" in awards,
        "won_globe": "Golden Globe" in awards and "Won" in awards,
        "nominated_globe": "Golden Globe" in awards and "Nominated" in awards
    }

def extract_rotten_tomatoes_score(omdb_data):
    '''Function to get Rotten Tomatoes score from Open Movies DB, a popular user
    site for reviewing movies'''
    ratings = omdb_data.get("Ratings", [])
    for rating in ratings:
        if rating["Source"] == "Rotten Tomatoes":
            return rating["Value"]
    return None

def extract_user_engagement(omdb_data):
    '''Returns an object for the IMDB rating and number of votes that contributed to that score'''
    return {
        "imdb_rating": omdb_data.get("imdbRating"),
        "imdb_votes": omdb_data.get("imdbVotes")
    }

def enrich_movie(row):
    title = row['Title']
    year = row['Year']
    print("Currently looking at: " + title)
    
    omdb_data = fetch_omdb_data(title, year)
    tmdb_id = fetch_tmdb_movie_id(title)
    box_office_data = fetch_tmdb_box_office(tmdb_id) if tmdb_id else {}

    awards = check_awards(omdb_data)
    rt_score = extract_rotten_tomatoes_score(omdb_data)
    engagement = extract_user_engagement(omdb_data)

    return pd.Series({
        **box_office_data,
        **awards,
        "rt_score": rt_score,
        **engagement
    })

enriched_data = df.apply(enrich_movie, axis=1)
df = pd.concat([df, enriched_data], axis=1)

df.to_csv("enriched_imdb_movies.csv", index=False)
