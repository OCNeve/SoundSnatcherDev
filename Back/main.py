from sclib import SoundcloudAPI, Playlist, Track
from os import mkdir, path, getcwd, rename, listdir, unlink, remove
from os.path import exists, isfile, isdir, islink, getmtime
from os.path import join as osjoin
from unicodedata import normalize
import subprocess
from re import sub
from json import loads
from shutil import rmtree
from pytube import Playlist, YouTube
from time import time
from spotdl import utils




class SoundSnatcherBackend:
    @staticmethod
    def slugify(value, allow_unicode=False):
        """
        Taken from https://github.com/django/django/blob/master/django/utils/text.py
        Convert to ASCII if 'allow_unicode' is False. Convert spaces or repeated
        dashes to single dashes. Remove characters that aren't alphanumerics,
        underscores, or hyphens. Convert to lowercase. Also strip leading and
        trailing whitespace, dashes, and underscores.
        """
        value = str(value)
        if allow_unicode:
            value = normalize('NFKC', value)
        else:
            value = normalize('NFKD', value).encode('ascii', 'ignore').decode('ascii')
        value = sub(r'[^\w\s-]', '', value.lower())
        return sub(r'[-\s]+', '-', value).strip('-_')

    def __init__(self, snatch_type, url, specific_dir=None, no_dir=False, auto_run=True):
        self.__current_index = 0
        self.__total_playlist_length = 100
        self.api = SoundcloudAPI()
        self.snatch_type = snatch_type
        self.url = url
        self.no_dir = no_dir
        self.specific_dir = specific_dir
        self.__error_message = None
        if not self.no_dir:
            self.dir = self.specific_dir if self.specific_dir is not None \
                else SoundSnatcherBackend.slugify(self.url.split("/")[-1])
        else:
            self.dir = ""
        if auto_run:
            self.downloadSourceManager()

    def setUrl(self, url):
        self.url = url

    def getErrorMessage(self):
        return self.__error_message

    def getCurrentIndex(self):
        return self.__current_index

    def getTotalPlaylistLength(self):
        return self.__total_playlist_length

    def emptyTemporaryDir(self):
        folder = osjoin(getcwd(), "tmp")
        if not isdir(folder):
            mkdir(folder)
        for filename in listdir(folder):
            file_path = osjoin(folder, filename)
            try:
                if isfile(file_path) or islink(file_path):
                    unlink(file_path)
                elif isdir(file_path):
                    rmtree(file_path)
            except Exception as e:
                print('Failed to delete %s. Reason: %s' % (file_path, e))

    def downloadFromSpotify(self):
        self.emptyTemporaryDir()
        if not utils.ffmpeg.is_ffmpeg_installed(ffmpeg='ffmpeg'):
            print('installing ffmpeg')
            utils.ffmpeg.download_ffmpeg()
        if "playlist" in self.url or "album" in self.url:
            metadata_file = f'{time()}meta.spotdl'
            first_cmd = fr"spotdl save {self.url} --save-file {osjoin('tmp', metadata_file)}"
            print("fetching playlist/album metadata")
            o = subprocess.check_output(first_cmd.split())
            if not exists(osjoin('tmp', metadata_file)):
                rename(osjoin("tmp", metadata_file), osjoin('tmp', metadata_file))
            metadata = loads(open(osjoin('tmp', metadata_file), "r").read())
            print("got metadata\n")
            print("Downloading in wav format, will revert to mp3 if it fails")
            self.__total_playlist_length = len(metadata)
            for index, song in enumerate(metadata):
                print(f"{index + 1}/{self.__total_playlist_length}: {song["name"]}\n\tby: {", ".join(song["artists"])}\n")
                self.__current_index = index
                self.url = song["url"]
                try:
                    cmd = f"spotdl {self.url} --output {self.specific_dir} --format wav"
                    o = subprocess.check_output(cmd.split())
                except Exception as e:
                    print(f"Download faild for mp3 format with the following message:\n{e}")
                    print("Will try to download in default (mp3) format instead.")

                    try:
                        cmd = f"spotdl {self.url} --output {self.specific_dir}"
                        o = subprocess.check_output(cmd.split())
                    except Exception as e:
                        print('retry failed with message:\n{e}')
                        print('going to skip this one entirely')
        else:
            cmd = f"spotdl {self.url} --output {self.specific_dir}"
            o = subprocess.check_output(cmd.split())


    def downlaodFromYoutube(self):
        start_time = time()
        if "playlist" in self.url:
            playlist = Playlist(self.url)  # , use_oauth=True, allow_oauth_cache=True
            self.__total_playlist_length = len(playlist.videos)
            for index, video in enumerate(playlist.videos):
                self.__current_index = index
                video = video.streams.filter(only_audio=True)
                video.first().download(output_path=self.dir)
        else:
            youtube = YouTube(self.url)  # , use_oauth=True, allow_oauth_cache=True
            youtube = youtube.streams.filter(only_audio=True).all()
            youtube[0].download(output_path=self.dir)

        for file in listdir(self.dir):
            if getmtime(osjoin(self.dir, file)) > start_time:
                try:
                    rename(osjoin(self.dir, file), osjoin(self.dir, f'{file[:-1]}3'))
                except FileExistsError:
                    remove(osjoin(self.dir, file))

    def downloadSourceManager(self):
        if "spotify" in self.url:
            self.downloadFromSpotify()
        elif "yout" in self.url:
            self.downlaodFromYoutube()
        else:
            if self.snatch_type == "playlist":
                self.snatchPlaylist()
            else:
                self.snatchSong()


    def snatchPlaylist(self):
        playlist = self.api.resolve(self.url)
        self.mkdirIfNotExists()
        self.__total_playlist_length = len(playlist.tracks)
        for index, track in enumerate(playlist.tracks):
            filename = self.constructFileName(track)
            self.__current_index = index
            with open(filename, 'wb+') as file:
                track.write_mp3_to(file)

    def snatchSong(self):
        track = self.api.resolve(self.url)
        assert type(track) is Track
        filename = self.constructFileName(track)
        self.mkdirIfNotExists()
        with open(filename, 'wb+') as file:
            track.write_mp3_to(file)
        return filename

    def constructFileName(self, track):
        filename = f'{SoundSnatcherBackend.slugify(track.artist)} - {SoundSnatcherBackend.slugify(track.title)}.mp3'
        if not self.no_dir:
            filename = osjoin(self.dir, filename)
        if self.specific_dir is not None:
            return filename
        return osjoin('.', filename)

    def mkdirIfNotExists(self):
        if not path.exists(self.dir) and not self.no_dir:
            mkdir(self.dir)
