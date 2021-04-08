from flask import render_template
from app import app

@app.route('/')
def index():
    return render_template('index.html')

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