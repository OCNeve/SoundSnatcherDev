from tkinter import StringVar, filedialog, W, END
from customtkinter import CTk, CTkFrame, CTkLabel, CTkEntry, CTkRadioButton, CTkButton, CTkProgressBar
from threading import Thread
from Front.Desktop.locales.localesHander import getString
from Back.knownpaths import get_path
from Back.main import SoundSnatcherBackend
from Back.wavConverter import WavConverter
from os import path
import sys

def check_os():
    import os
    if os.name == 'nt':
        return 'Windows'
    elif os.name == 'posix':
        return 'MacOS'

    return 'Not sure'

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = path.abspath(".")
    return path.join(base_path, relative_path)


class PrettyLabel(CTkLabel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, font=("Ubuntu", 12, 'bold'), **kwargs)


class CustomButton(CTkButton):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._hover_color = "black"

class CustomRadioButton(CTkRadioButton):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._hover_color = "black"

class GUI:
    def __init__(self):
        self.back_has_been_initialized = False
        self.downloading = False
        self.root = CTk()
        self.snatch_type = StringVar()
        self.Back = SoundSnatcherBackend
        self.snatcher = Thread(target=self.getSnatchFunc)
        self.root.geometry("480x380")
        if check_os() == 'Windows':
            self.root.iconbitmap(resource_path("logo.ico"))
        self.root.title('Sound Snatcher')
        self.current_color = self.root["bg"]
        self.error = CTkLabel(self.root, fg_color=self.current_color)
        self.mainWindow()
        self.pb = CTkProgressBar(
            master=self.loading_frame,
            orientation='horizontal',
            mode='determinate',
            fg_color="grey",
            progress_color="#eb7c38"
        )
        self.value_label = CTkLabel(self.loading_frame, text="1%", fg_color=self.current_color)
        self.root.mainloop()

    def mainWindow(self):
        self.main_frame = CTkFrame(self.root, fg_color=self.current_color)
        self.main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        l_url = PrettyLabel(self.main_frame, text=getString('Labels', 'url'), fg_color=self.current_color)
        l_url.configure(font=('Helvetica bold', 14))
        l_url.pack(anchor='w', padx=10, pady=10)
        entry_frame = CTkFrame(self.main_frame)
        entry_frame.pack(anchor='w')
        # snatch_type, url, specific_dir = None, no_dir = False
        self.url = CTkEntry(entry_frame, width=370)
        self.url.pack()
        l_file_type = CTkLabel(self.main_frame, text=getString('Labels', 'file_type'), fg_color=self.current_color)
        l_file_type.configure(font=('Helvetica bold', 14))
        l_file_type.pack(anchor='w', padx=10, pady=10)
        file_type_frame = CTkFrame(self.main_frame, fg_color=self.current_color)
        file_type_frame.pack(anchor='w')

        self.snatch_type.set("playlist")
        r1 = CustomRadioButton(file_type_frame, text=getString('Radiobuttons', 'playlist'), variable=self.snatch_type,
                         value="playlist", fg_color="#eb7c38")
        r1.pack(anchor=W)
        r2 = CustomRadioButton(file_type_frame, text=getString('Radiobuttons', 'song'), variable=self.snatch_type,
                         value="song", fg_color="#eb7c38")
        r2.pack(anchor=W)
        l_path = CTkLabel(self.main_frame, text=getString('Labels', 'path'), fg_color=self.current_color)
        l_path.configure(font=('Helvetica bold', 14))
        l_path.pack(anchor='w', padx=10, pady=10)
        path_frame = CTkFrame(self.main_frame, fg_color=self.current_color)
        path_frame.pack(anchor='w')
        self.path = CTkEntry(path_frame, width=370)
        self.path.insert(0, get_path('Downloads'))
        self.path.grid(row=0, column=0)
        select_dir = CustomButton(
            path_frame,
            width=30,
            text=getString('Buttons', 'browse'),
            command=self.selectDir,
            fg_color="#eb7c38"
        )
        select_dir.grid(row=0, column=1, padx=5, pady=5)
        snatch_button = CustomButton(
            self.main_frame,
            text=getString('Buttons', 'snatch'),
            command=self.snatchSongs,
            width=30,
            fg_color="#eb7c38"
        )
        snatch_button.pack(padx=10, pady=10)
        self.loading_frame = CTkFrame(self.main_frame, fg_color=self.current_color)
        self.loading_frame.pack()

    def getSnatchFunc(self):
        wc = WavConverter(self.path.get())
        return wc.convertToWav(self.Back.downloadSourceManager)

    def snatchSongs(self):
        self.Back = SoundSnatcherBackend(self.snatch_type.get(), self.url.get(), self.path.get(), auto_run=False)

        def update_progress():
            try:
                self.error.pack_forget()
            except AttributeError:
                pass
            if self.snatcher.is_alive():
                index = self.Back.getCurrentIndex()
                total_songs = self.Back.getTotalPlaylistLength()
                percent = int(index / total_songs * 100) if int(index / total_songs * 100) != 0 else 1
            else:
                self.downloading = False
                percent = 100
                self.error = self.Back.getErrorMessage()
                if self.error is not None:
                    self.error = CTkLabel(self.main_frame, text=self.error, fg_color=self.current_color)
                    self.error.pack()
                    self.back_has_been_initialized = False
            self.pb.set(percent / 100) # because value is in range 0 1
            self.value_label.configure(text=f"{percent}%")
            if percent < 100:
                self.main_frame.after(100, update_progress)

        if not self.downloading:
            self.downloading = True
            self.pb.grid(row='0', column='0', padx=5)
            self.pb.set(0)
            self.value_label.grid(row='0', column='1', padx=5)
            self.snatcher = Thread(target=self.getSnatchFunc())
            self.snatcher.start()
            self.main_frame.after(100, update_progress)

    def selectDir(self):
        dir = filedialog.askdirectory()
        self.path.delete(0, END)
        self.path.insert(0, dir)
