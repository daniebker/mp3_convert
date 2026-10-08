# mp3_convert
Python Script to convert wav and flac files to mp3. Skips failed files and logs them to a csv so you can easily figure out what's missing. If the mp3 already exists at the target path it also skips the conversion. 

## Run

`python3 mp3convert.py /path/to/input /path/to/output`

Provide a bitrate using the `--bitrate` argument:

`python3 mp3convert.py /path/to/input /path/to/output --bitrate=192kbps`
