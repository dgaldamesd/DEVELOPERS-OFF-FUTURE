from flask import Flask, request, redirect, session, render_template, jsonify
import requests

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Spotify API credentials
CLIENT_ID = 'e16d3a403cb64a46a670e2f7dcabe870'
CLIENT_SECRET = 'f6b4df7bbf64476b8b67b34ff4a5cdfa'
REDIRECT_URI = 'http://18.190.136.78:8080/callback'  # Reemplaza tu_direccion_ip y puerto
SCOPE = 'user-top-read user-read-recently-played'  # Cambiar el alcance para obtener los artistas más populares y las canciones más escuchadas

@app.route('/logout')
def logout():
    # Elimina el token de acceso de la sesión
    session.pop('access_token', None)
    # Redirige al usuario de vuelta a index.html
    return redirect('/')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login')
def login():
    # Redirige al usuario a la página de autorización de Spotify
    authorization_url = f'https://accounts.spotify.com/authorize?client_id={CLIENT_ID}&response_type=code&redirect_uri={REDIRECT_URI}&scope={SCOPE}'
    return redirect(authorization_url)


@app.route('/callback')
def callback():
    # Obtiene el código de autorización de la URL de redireccionamiento
    code = request.args.get('code')

    # Intercambia el código de autorización por un token de acceso
    token_url = 'https://accounts.spotify.com/api/token'
    payload = {
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': REDIRECT_URI,
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET
    }
    response = requests.post(token_url, data=payload)
    access_token = response.json()['access_token']

    # Almacena el token de acceso en la sesión
    session['access_token'] = access_token

    # Redirige al usuario a la página de inicio
    return redirect('/home')

@app.route('/home')
def get_featured_playlists():
    # Token de acceso de la sesión
    access_token = session.get('access_token')
    
    if access_token:
        # URL de la API de Spotify
        url = 'https://api.spotify.com/v1/browse/featured-playlists'
        
        # Headers de la solicitud
        headers = {
            'Authorization': 'Bearer ' + access_token
        }
        
        try:
            # Realizar la solicitud GET a la API de Spotify
            response = requests.get(url, headers=headers)
            response.raise_for_status()  # Lanza una excepción si la solicitud no fue exitosa
            
            # Obtener los datos de las playlists
            playlists_data = response.json()['playlists']['items']
            
            # Agregar índices a las playlists
            playlists_data_with_index = [(index, playlist) for index, playlist in enumerate(playlists_data)]
            
            # Renderizar el template home.html y pasar los datos de las playlists como contexto
            return render_template('home.html', playlists=playlists_data_with_index)
        except requests.exceptions.RequestException as e:
            print("Error al realizar la solicitud a la API de Spotify:", e)
            return render_template('error.html', message='Error al obtener las listas de reproducción destacadas.'), 500
    else:
        return render_template('error.html', message='No hay token de acceso. Debes autorizar la aplicación primero.'), 401


@app.route('/top_tracks')
def top_tracks():
    # Obtiene el token de acceso de la sesión
    access_token = session.get('access_token')

    if access_token:
        headers = {
            'Authorization': 'Bearer ' + access_token
        }
        endpoint = 'https://api.spotify.com/v1/me/top/tracks'
        try:
            response = requests.get(endpoint, headers=headers)
            response.raise_for_status()  # Lanza una excepción si la solicitud no fue exitosa
            top_tracks_data = response.json()['items']
            
            # Obtener más información sobre cada canción
            detailed_tracks = []
            for track_data in top_tracks_data:
                track_id = track_data['id']
                track_endpoint = f'https://api.spotify.com/v1/tracks/{track_id}'
                track_response = requests.get(track_endpoint, headers=headers)
                track_response.raise_for_status()
                detailed_track_data = track_response.json()
                detailed_tracks.append(detailed_track_data)
                
            return render_template('top_tracks.html', tracks=detailed_tracks)
        except requests.exceptions.RequestException as e:
            print("Error al realizar la solicitud a la API de Spotify:", e)
            return render_template('error.html', message='Error al obtener las canciones más escuchadas.')
    else:
        return render_template('error.html', message='No hay token de acceso. Debes autorizar la aplicación primero.')

@app.route('/top_artists')
def top_artists():
    # Obtiene el token de acceso de la sesión
    access_token = session.get('access_token')

    if access_token:
        headers = {
            'Authorization': 'Bearer ' + access_token
        }
        endpoint = 'https://api.spotify.com/v1/me/top/artists'
        try:
            response = requests.get(endpoint, headers=headers)
            response.raise_for_status()  # Lanza una excepción si la solicitud no fue exitosa
            top_artists_data = response.json()['items']
            
            # Obtener más información sobre cada artista
            detailed_artists = []
            for artist_data in top_artists_data:
                artist_id = artist_data['id']
                artist_endpoint = f'https://api.spotify.com/v1/artists/{artist_id}'
                artist_response = requests.get(artist_endpoint, headers=headers)
                artist_response.raise_for_status()
                detailed_artist_data = artist_response.json()
                detailed_artists.append(detailed_artist_data)
                
            return render_template('top_artists.html', artists=detailed_artists)
        except requests.exceptions.RequestException as e:
            print("Error al realizar la solicitud a la API de Spotify:", e)
            return render_template('error.html', message='Error al obtener los artistas más populares.')
    else:
        return render_template('error.html', message='No hay token de acceso. Debes autorizar la aplicación primero.')

@app.route('/perfil')
def perfil():
    access_token = session.get('access_token')

    if access_token:
        headers = {
            'Authorization': 'Bearer ' + access_token
        }
        endpoint = 'https://api.spotify.com/v1/me'
        try:
            response = requests.get(endpoint, headers=headers)
            response.raise_for_status()  
            perfil_data = response.json()
            return render_template('perfil.html', perfil_data=perfil_data)
        except requests.exceptions.RequestException as e:
            print("Error al realizar la solicitud a la API de Spotify:", e)
            return jsonify({'error': 'Error al obtener el perfil de Spotify.'})
    else:
        return jsonify({'error': 'No hay token de acceso. Debes autorizar la aplicación primero.'})



@app.route('/recently_played')
def recently_played():
    # Obtener el token de acceso de la sesión
    access_token = session.get('access_token')

    if access_token:
        headers = {
            'Authorization': 'Bearer ' + access_token
        }
        limit = request.args.get('limit', default=6, type=int)  # Obtener el parámetro de límite, predeterminado a 5 si no se proporciona
        endpoint = f'https://api.spotify.com/v1/me/player/recently-played?limit={limit}'
        try:
            response = requests.get(endpoint, headers=headers)
            response.raise_for_status()  # Lanza una excepción si la solicitud no fue exitosa
            recently_played_data = response.json()['items']
            
            return render_template('recently_played.html', tracks=recently_played_data)
        except requests.exceptions.RequestException as e:
            print("Error al realizar la solicitud a la API de Spotify:", e)
            return render_template('error.html', message='Error al obtener los tracks reproducidos recientemente.')
    else:
        return render_template('error.html', message='No hay token de acceso. Debes autorizar la aplicación primero.')



if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080, debug=True)  # Cambia el puert
