##Configuration##
movie_path = '/path/to/movies/' #Full path of movie folder goes here
port = 9000
debug = True

if movie_path == '/path/to/movies/':
	print '!!Change movie_path in reel.py !!'
	exit()

from flask import Flask, request, send_file, Response, render_template, url_for
import os, mimetypes, re, StringIO, datetime, user_agents
from itertools import izip_longest
from bs4 import BeautifulSoup
from PIL import Image, ImageDraw, ImageFont
app = Flask(__name__)

def settings(s):
	if s == 'movie_path':
		return movie_path
	if s == 'port':
		return port

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
							if split[0] + '.m4v' == movie['name']:
								movie['tbn'] = os.path.join(dirpath, f).replace(movie_path, '/posters/')
						if split[1] == '.nfo':
							try:
								soup = BeautifulSoup(open(os.path.join(dirpath, f)))
								movie['name'] = soup.movie.sorttitle.get_text()
							except:
								pass
				try:
					movie['tbn']
				except:
					movie['tbn'] = '/missing/' + movie['name']
				list.append(movie)
	return list

@app.route('/')
def movies():
	movie_list = find_movies(movie_path)
	movie_list = sorted(movie_list, key=lambda k: k['name'])
	movie_list = list(izip_longest(movie_list[0::3], movie_list[1::3], movie_list[2::3]))
	return render_template('index.html', movie_list=movie_list)

@app.route('/posters/<path:filename>')
def img(filename):
	modified = datetime.datetime.fromtimestamp(os.path.getmtime(movie_path + filename)).strftime('%a, %d %b %Y %H:%M:%S')
	if 'If-Modified-Since' in request.headers and request.headers['If-Modified-Since'] == modified:
		return  Response(response='', status=304, headers={'Cache-Control': 'max-age=31557600, public', 'Last-Modified': modified}, mimetype='image/jpeg', content_type=None, direct_passthrough=False)
	else:
		tbn = Image.open(movie_path + filename)
		if user_agents.parse(request.headers.get('User-Agent')).is_mobile:
			multiplier = 1
		else:
			multiplier = 2
		if tbn.size[0] / tbn.size[1] > 2/3:
			baseheight = 400*multiplier
			hpercent = (baseheight / float(tbn.size[1]))
			wsize = int((float(tbn.size[0]) * float(hpercent)))
			tbn = tbn.resize((wsize, baseheight), Image.ANTIALIAS)
			tbn = tbn.crop((0, 0, 266*multiplier, 400*multiplier)) 
			output = StringIO.StringIO()
			tbn.save(output, format='JPEG')
		else:
			basewidth = 266*multiplier
			wpercent = (basewidth / float(tbn.size[0]))
			hsize = int((float(tbn.size[1]) * float(wpercent)))
			tbn = tbn.resize((basewidth, hsize), Image.ANTIALIAS)
			tbn = tbn.crop((0, 0, 266*multiplier, 400*multiplier)) 
			output = StringIO.StringIO()
			tbn.save(output, format='JPEG')
		return Response(response=[output.getvalue()], status=200, headers={'Cache-Control': 'max-age=31557600, public', 'Last-Modified': modified}, mimetype='image/jpeg', content_type=None, direct_passthrough=False)

@app.route('/missing/<filename>')
def missing(filename):
	width = 266
	height = 400
	tbn = Image.new('RGB', (width, height))
	draw = ImageDraw.Draw(tbn)
	text_x, text_y = draw.textsize(filename)
	x = (width - text_x)/2
	y = (height - text_y)/2
	draw.text((x,y), filename)
	output = StringIO.StringIO()
	tbn.save(output, format='JPEG')
	return Response(response=[output.getvalue()], status=200, mimetype='image/jpeg', content_type=None, direct_passthrough=False)

if __name__ == '__main__':
	print 'run server.py not reel.py'
	#app.run(port=port, host='0.0.0.0', debug=debug)
