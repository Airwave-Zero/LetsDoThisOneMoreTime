import requests
import pandas as pd

client_id = 'YOUR_CLIENT_ID'
client_secret = 'YOUR_CLIENT_SECRET'

def auth_client():
    '''This function returns a JSON format access token to use
    for authentication in the header'''
    auth_url = 'https://id.twitch.tv/oauth2/token'
    params = {
        'client_id': client_id,
        'client_secret': client_secret,
        'grant_type': 'client_credentials'
    }
    response = requests.post(auth_url, params=params)
    access_token = response.json()['access_token']    return access_token

def get_stream_json():
    '''This function accesses Twitch API and requests the
    top/first 100 streamers and gets their data in a JSON format'''
    url = 'https://api.twitch.tv/helix/streams'
    params = {
        'first': 100  # Max per request
    }

    response = requests.get(url, headers=headers, params=params)
    streams = response.json()['data']
    return streams

def get_games(streams):
    '''This function parses the JSON format stream data and returns the
    games and their respective game ID's'''
    game_ids = list(set([stream['game_id'] for stream in streams if stream['game_id']]))

    # Get up to 100 games per request
    url = 'https://api.twitch.tv/helix/games'
    params = [('id', gid) for gid in game_ids]

    response = requests.get(url, headers=headers, params=params)
    games = {game['id']: game['name'] for game in response.json()['data']}
    return games

def make_dataframe(streams, games):
    '''This function combines the stream and game data and returns a neat
    dataframe for use in PowerBI'''
    enriched_data = []
    for stream in streams:
        enriched_data.append({
            'streamer': stream['user_name'],
            'viewer_count': stream['viewer_count'],
            'started_at': stream['started_at'],
            'game_id': stream['game_id'],
            'game_name': games.get(stream['game_id'], 'Unknown'),
        })

    df = pd.DataFrame(enriched_data)
    return df

access_token = auth_client()
headers = {
        "User-Agent": "Chrome/122.0.0.0",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Connection": "keep-alive",
        'Client-ID': client_id,
        'Authorization': f'Bearer {access_token}'
    }
json_stream_data = get_stream_json()
games_data = get_games(json_stream_data)
df = make_dataframe(json_stream_data, games_data)
