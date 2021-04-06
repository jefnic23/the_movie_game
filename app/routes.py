from flask import render_template, request, redirect, url_for, jsonify
import tmdbsimple as tmdb
from app import app

tmdb.API_KEY = '47403e3942da0c88526896aa3195bb62'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/round_start')
def round_start():
    search = tmdb.Search()
    q = request.args.get('search', 0, type=str)
    response = search.movie(query=q)
    genres = [16, 99, 10402, 10770]
    return jsonify(result=[t['original_title'] for t in response['results'] if not any(x in t['genre_ids'] for x in genres) if t['genre_ids']])

# look for movie by string search and get id
# response = search.movie(query='shawshank')
# movie_id = search.results[0]['id']

# look for actor by string search and get id
# response = search.person(query='dustin hoffman')
# movie_id = search.results[0]['id']

# get movie metadata from movie id
# movie = tmdb.Movies(movie_id)
# response = movie.info()
# cast = movie.credits()['cast']
# for c in cast:
#     if c['known_for_department'] == 'Acting':
#         print(c['name'], c['id'])

# get list of movies starring actor from actor id
# actor = tmdb.People(504)
# response = actor.movie_credits()['cast']
# for r in response:
#     print(r['original_title'])