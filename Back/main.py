from sclib import SoundcloudAPI, Playlist, Track
from os import mkdir, path
from unicodedata import normalize
from re import sub
from Front.Desktop.locales.localesHander import getString
from yt_dlp import YoutubeDL

class SoundcloudSnatcher:
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

    def __init__(self, snatch_type, url, specific_dir = None, no_dir = False, auto_run=True):
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
                else SoundcloudSnatcher.slugify(self.url.split("/")[-1])
        else:
            self.dir = ""
        if auto_run:
            if snatch_type == 'playlist':
                self.snatchPlaylist()
            else:
                self.snatchSong()

    def setUrl(self, url):
        self.url = url

    def getErrorMessage(self):
        return self.__error_message

    def getCurrentIndex(self):
        return self.__current_index

    def getTotalPlaylistLength(self):
        return self.__total_playlist_length

    def downlaodFromYoutube(self):
        video_info = YoutubeDL().extract_info(
            url = self.url, download=False
        )
        filename = f"{self.dir}\\{video_info['title']}.mp3"
        options={
            'format':'bestaudio/best',
            'keepvideo':False,
            'outtmpl':filename,
        }

        with YoutubeDL(options) as ydl:
            ydl.download([video_info['webpage_url']])

    def snatchPlaylist(self):
        print('in')
        try:
            playlist = self.api.resolve(self.url)
        except TypeError:
            try:
                self.downlaodFromYoutube()
            except Exception as e:
                print(e)
                self.__error_message = getString("Errors", "url_error")
            else:
                return 0
        else:
            assert type(playlist) is Playlist
            self.mkdirIfNotExists()
            self.__total_playlist_length = len(playlist.tracks)
            for index, track in enumerate(playlist.tracks):
                filename = self.constructFileName(track)
                self.__current_index = index
                with open(filename, 'wb+') as file:
                    track.write_mp3_to(file)

    def snatchSong(self):
        try:
            track = self.api.resolve(self.url)
        except TypeError:
            try:
                self.downlaodFromYoutube()
            except Exception as e:
                print(e)
                self.__error_message = getString("Errors", "url_error")
            else:
                return 0
        else:
            assert type(track) is Track
            filename = self.constructFileName(track)
            self.mkdirIfNotExists()
            with open(filename, 'wb+') as file:
                track.write_mp3_to(file)

    def constructFileName(self, track):
        filename = f'{SoundcloudSnatcher.slugify(track.artist)} - {SoundcloudSnatcher.slugify(track.title)}.mp3'
        if not self.no_dir:
            filename = f'{self.dir}\\{filename}'
        if self.specific_dir is not None:
            return filename
        return f'.\\{filename}'

    def mkdirIfNotExists(self):
        if not path.exists(self.dir) and not self.no_dir:
            mkdir(f'.\\{self.dir}')

#SoundcloudSnatcher('playlist',"https://soundcloud.com/user-802191077/sets/goodfuckingcore")
#SoundcloudSnatcher('song',"https://soundcloud.com/argotek/acid-marry-me?in=user-802191077/sets/goodfuckingcore", specific_dir="C:\\Projects-data")
