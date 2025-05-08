import requests
import pandas as pd

# 1. Load Base IMDB Dataset
df = pd.read_csv("movies.csv")  # Must include at least 'title' and 'year'

# 2. Setup API Keys (Replace with your real keys)
OMDB_API_KEY = "your_omdb_key"
TMDB_API_KEY = "your_tmdb_key"

# 3. Define Fetch Functions
def fetch_omdb_data(title, year):
    url = f"http://www.omdbapi.com/?t={title}&y={year}&apikey={OMDB_API_KEY}"
    response = requests.get(url)
    if response.ok:
        return response.json()
    return {}

def fetch_tmdb_movie_id(title):
    url = f"https://api.themoviedb.org/3/search/movie?api_key={TMDB_API_KEY}&query={title}"
    response = requests.get(url)
    if response.ok and response.json()['results']:
        return response.json()['results'][0]['id']
    return None

def fetch_tmdb_box_office(tmdb_id):
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
    awards = omdb_data.get("Awards", "")
    return {
        "won_oscar": "Oscar" in awards and "Won" in awards,
        "nominated_oscar": "Oscar" in awards and "Nominated" in awards,
        "won_globe": "Golden Globe" in awards and "Won" in awards,
        "nominated_globe": "Golden Globe" in awards and "Nominated" in awards
    }

def extract_rotten_tomatoes_score(omdb_data):
    ratings = omdb_data.get("Ratings", [])
    for rating in ratings:
        if rating["Source"] == "Rotten Tomatoes":
            return rating["Value"]
    return None

def extract_user_engagement(omdb_data):
    return {
        "imdb_rating": omdb_data.get("imdbRating"),
        "imdb_votes": omdb_data.get("imdbVotes")
    }

# 4. Enrich Dataset
def enrich_movie(row):
    title = row['title']
    year = row['year']

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

# 5. Apply Enrichment
enriched_data = df.apply(enrich_movie, axis=1)
df = pd.concat([df, enriched_data], axis=1)

# 6. Save
df.to_csv("enriched_imdb_movies.csv", index=False)
