import tmdbsimple as tmdb

tmdb.API_KEY = '47403e3942da0c88526896aa3195bb62'

search = tmdb.Search()

# look for movie by string search and get id
response = search.movie(query='shawshank')
movie_id = search.results[0]['id']

# get movie metadata from movie id
movie = tmdb.Movies(movie_id)
response = movie.info()
cast = movie.credits()['cast']
for c in cast:
    if c['known_for_department'] == 'Acting':
        print(c['name'], c['id'])

# get list of movies starring actor from actor id
# actor = tmdb.People(504)
# response = actor.movie_credits()['cast']
# for r in response:
#     print(r['original_title'])