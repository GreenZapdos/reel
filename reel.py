#!/usr/bin/env python

from flask import Flask, request, send_file, Response, render_template, url_for
import os, mimetypes, re, StringIO, datetime, user_agents, yaml
from itertools import izip_longest
from bs4 import BeautifulSoup
from PIL import Image, ImageDraw, ImageFont
app = Flask(__name__)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 31557600

#Config Path
cpath = os.path.join(os.path.split(__file__)[0], 'config.yml')

#initialize old_movie_list(for caching)
old_movie_list = dict()
old_movie_list['list'] = list()
old_movie_list['modified'] = str()

#Check for config file
if not os.path.isfile(cpath):
       print('copy config.yml.default to config.yml, then modify the settings')
       quit()

#Load Config
with open(cpath) as f:
       config = yaml.safe_load(f)
try:
	config['movie_path']
	config['port']
	config['debug']
	config['tbn_formats']
	config['movie_formats']
except:
	print('\nConfig missing options, check config.yml.default!\n')
	raise

#Return settings (Called by server.py)
def settings(s):
	if s == 'movie_path':
		return config['movie_path']
	if s == 'port':
		return config['port']

#Crawl directory tree and find movies
def find_movies(path):
	list = []
	for (dirpath, dirnames, filenames) in os.walk(path):
		for d in dirnames:#Recursive
			find_movies(d)
		for f in filenames:#Detect movies or thumbnails
			split = os.path.splitext(f)
			if split[1].replace('.', '') in config['movie_formats']:
				movie = dict()
				movie['path'] = os.path.join(dirpath, f).replace(config['movie_path'], '/movie-directory/')
				movie['name'] = f
				split = os.path.splitext(f)
				for format in config['tbn_formats']:
					if os.path.isfile(os.path.join(dirpath, split[0] + '.' + format)):
						movie['tbn'] = os.path.join(dirpath, split[0] + '.' + format).replace(config['movie_path'], '/posters/')
				if not 'tbn' in movie:
						movie['tbn'] = '/missing/' + movie['name']
				if os.path.isfile(os.path.join(dirpath, split[0] + '.nfo')): #Read nfo file to sort movies in proper order
					try:
						soup = BeautifulSoup(open(os.path.join(dirpath, split[0] + '.nfo')), 'xml')
						movie['name'] = soup.movie.sorttitle.get_text()
					except:
						pass
				list.append(movie)
	return list

## Begin App Routes ##

@app.route('/')
def movies():
	global old_movie_list
	modified = old_movie_list['modified']
	movie_list = find_movies(config['movie_path'])
	if 'If-Modified-Since' in request.headers and old_movie_list['list'] == movie_list:
		return Response(response='', status=304, headers={'Cache-Control': 'max-age=31557600, public', 'Last-Modified': modified}, direct_passthrough=False)
	else:
		old_movie_list['list'] = movie_list
		movie_list = sorted(movie_list, key=lambda k: k['name'])
		movie_list = list(izip_longest(movie_list[0::3], movie_list[1::3], movie_list[2::3]))
		old_movie_list['modified'] = datetime.datetime.now().strftime('%a, %d %b %Y %H:%M:%S')
		modified = old_movie_list['modified']
		return Response(response=render_template('index.html', movie_list=movie_list), status=200, headers={'Cache-Control': 'max-age=31557600, public', 'Last-Modified': modified}, direct_passthrough=False)


@app.route('/posters/<path:filename>')
def img(filename):
	lmod = datetime.datetime(2014, 5, 15, 16, 15, 44) # The last time this function was modified.
	if lmod >= datetime.datetime.fromtimestamp(os.path.getmtime(config['movie_path'] + filename)):
		modified = datetime.datetime.fromtimestamp(os.path.getmtime(config['movie_path'] + filename)).strftime('%a, %d %b %Y %H:%M:%S')
	else:
		modified = lmod.strftime('%a, %d %b %Y %H:%M:%S')
	if 'If-Modified-Since' in request.headers and request.headers['If-Modified-Since'] == modified:
		return  Response(response='', status=304, headers={'Cache-Control': 'max-age=31557600, public', 'Last-Modified': modified}, mimetype='image/jpeg', content_type=None, direct_passthrough=False)
	else:
		tbn = Image.open(config['movie_path'] + filename)
		if user_agents.parse(request.headers.get('User-Agent')).is_mobile: #Deliver higher quality images on non-mobile
			multiplier = 1
		else:
			multiplier = 2
		#Crop and resize to exact specifications
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
	lmod = datetime.datetime(2014, 5, 15, 16, 15, 44) # The lest time this function was modified.
	modified = lmod.strftime('%a, %d %b %Y %H:%M:%S')
	if 'If-Modified-Since' in request.headers and request.headers['If-Modified-Since'] == modified:
		return  Response(response='', status=304, headers={'Cache-Control': 'max-age=31557600, public', 'Last-Modified': modified}, mimetype='image/jpeg', content_type=None, direct_passthrough=False)
	else:
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
		return Response(response=[output.getvalue()], status=200, headers={'Cache-Control': 'max-age=31557600, public', 'Last-Modified': modified}, mimetype='image/jpeg', content_type=None, direct_passthrough=False)

if __name__ == '__main__':
	if not config['debug']:
		print('run server.py not reel.py')
	else:
		print('running in debug mode, videos may not be served')
		app.run(port=config['port'], host='0.0.0.0', debug=True)
