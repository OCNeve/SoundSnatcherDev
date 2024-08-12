import sys
import validators
import os
from Back.main import SoundSnatcherBackend

print(r"""   _____                       _                                      
  / ____|                     | |                                     
 | (___   ___  _   _ _ __   __| |                                     
  \___ \ / _ \| | | | '_ \ / _` |                                     
  ____) | (_) | |_| | | | | (_| |                                     
 |_____/ \___/ \__,_|_| |_|\__,_|                                     
                            _____             _       _               
                           / ____|           | |     | |              
                          | (___  _ __   __ _| |_ ___| |__   ___ _ __ 
                           \___ \| '_ \ / _` | __/ __| '_ \ / _ \ '__|
                           ____) | | | | (_| | || (__| | | |  __/ |   
                          |_____/|_| |_|\__,_|\__\___|_| |_|\___|_|   """)

print(2*"\n")

def print_usage():
	print('usage:')
	print('\tssnatcher help\t: list usages')
	print('\tssnatcher [download type] [url] [path]\t: download a playlist a song or an album from [url] and save it to [path]')


if len(sys.argv) < 3:
	print_usage()
	sys.exit()

if sys.argv[1] == "help":
	print_usage()
	sys.exit()

if sys.argv[1] not in ['playlist', 'album', 'song']:
	print("ERROR: first argument must be the download type.")
	print("It must be one of the following:")
	print("\tplaylist\n\talbum\n\tsong")
	print_usage()
	sys.exit()

if not validators.url(sys.argv[2]): # check arg 2 is a valid url
	print('ERROR: second agrument is not a valid url')
	print_usage()
	sys.exit()
if not os.path.exists(sys.argv[3]): # check if arg 2 is a valid path
	print('ERROR: third argument is not a valid path')
	print_usage()
	sys.exit()

SoundSnatcherBackend(sys.argv[1], sys.argv[2], sys.argv[3], auto_run=True)