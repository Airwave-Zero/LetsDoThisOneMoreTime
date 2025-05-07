import requests

client_id = 'YOUR_CLIENT_ID'
client_secret = 'YOUR_CLIENT_SECRET'

def auth_client():
    auth_url = 'https://id.twitch.tv/oauth2/token'
    params = {
        'client_id': client_id,
        'client_secret': client_secret,
        'grant_type': 'client_credentials'
    }

    response = requests.post(auth_url, params=params)
    access_token = response.json()['access_token']
    return access_token

######

def get_livestreams():
    headers = {
        '''
        "User-Agent": "Chrome/122.0.0.0",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Connection": "keep-alive",
        '''
        'Client-ID': client_id,
        'Authorization': f'Bearer {access_token}'
    }

    # Example: Get live streams from Twitch
    url = 'https://api.twitch.tv/helix/streams'
    params = {
        'first': 100  # Max per request
    }

    response = requests.get(url, headers=headers, params=params)
    streams = response.json()['data']
    return streams
######

def get_games():
    game_ids = list(set([stream['game_id'] for stream in streams if stream['game_id']]))

    # Get up to 100 games per request
    url = 'https://api.twitch.tv/helix/games'
    params = [('id', gid) for gid in game_ids]

    response = requests.get(url, headers=headers, params=params)
    games = {game['id']: game['name'] for game in response.json()['data']}
    return games

#######
def get_dataframe():
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
