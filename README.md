## reel

reel is a HTTP movie share, think XBMC for web browsers

![Alt text](screenshot.png)

## Requirements

Run `pip install twisted flask beautifulsoup4 user_agents Pillow PyYaml` to make sure you have all the requirements.

## Configuration

copy `config.yml.default` to `config.yml` and modify the values.
The movie directory should have movies organized into subfolders, with thumbnails(jpg, png or tbn) and (optionally) XBMC-style .nfo files. Thumbnails may be named either `<moviename>.(jpg, png, tbn)` or `<moviename>-poster.(jpg, png, tbn)`
```
$ ls /movies/back-to-the-future-part-1-1985/
back-to-the-future-part-1-1985.m4v  back-to-the-future-part-1-1985.nfo  back-to-the-future-part-1-1985-poster.jpg
```

You may need to modify your /etc/mime.types to support the m4v extension.
```
video/mp4                                       mp4 m4v
```

.nfo files will be read for the `<sorttile>` tag
```
<movie>
        <sorttitle>harry potter 4</sorttitle>
</movie>
```
## Usage

`python server.py`

Click on the movie thumbnails to watch the movie.

## License

reel is licensed under GPL 3.0, see LICENSE