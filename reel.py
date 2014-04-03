##Configuration##
movie_path = '/path/to/movies/' #Full path of movie folder goes here
port = 9000
debug = True

if movie_path == '/path/to/movies/':
	print '!!Change movie_path in reel.py !!'
	exit()

from flask import Flask, request, send_file, Response, render_template, url_for
import os, mimetypes, re
from itertools import izip_longest
from bs4 import BeautifulSoup
app = Flask(__name__)

def settings(s):
	if s == 'movie_path':
		return movie_path
	if s == 'port':
		return port


@app.after_request
def after_request(response):
    response.headers.add('Accept-Ranges', 'bytes')
    return response

def find_movies(path):
	list = []
	for (dirpath, dirnames, filenames) in os.walk(path):
		for d in dirnames:
			find_movies(d)
		for f in filenames:
			split = os.path.splitext(f)
			if split[1] == '.m4v':
				movie = dict()
				movie['path'] = os.path.join(dirpath, f).replace(movie_path, '/movie-directory/')
				movie['name'] = f
				for (dirpath, dirnames, filenames) in os.walk(dirpath):
					for f in filenames:
						split = os.path.splitext(f)
						if split[1] == '.tbn' or split[1] == '.jpg' or split[1] == '.png':
							movie['tbn'] = os.path.join(dirpath, f).replace(movie_path, '/movie-directory/')
                                                if split[1] == '.nfo':
							try:
								soup = BeautifulSoup(open(os.path.join(dirpath, f)))
								movie['name'] = soup.movie.sorttitle.get_text()
							except:
								pass
				try:
					movie['tbn']
				except:
					movie['tbn'] = '/static/missing-poster.jpg'
				list.append(movie)
	return list

@app.route('/')
def movies():
	movie_list = find_movies(movie_path)
	movie_list = sorted(movie_list, key=lambda k: k['name'])
	movie_list = list(izip_longest(movie_list[0::3], movie_list[1::3], movie_list[2::3]))
	return render_template('index.html', movie_list=movie_list)


if __name__ == '__main__':
	print 'run server.py not reel.py'
#	app.run(port=port, host='0.0.0.0', debug=debug)
