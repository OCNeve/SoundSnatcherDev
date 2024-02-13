import os

from pydub import AudioSegment
import os

class WavConverter:
    def __init__(self, dir):
        self.dir = dir

    def convertToWav(self, download_method):
        download_method()
        for filename in os.listdir(self.dir):
            if filename.split(".")[0].lower() == "mp3":
                sound = AudioSegment.from_mp3(filename)
                sound.export(f"{filename.split('.')[0]}.wav", format="wav")

