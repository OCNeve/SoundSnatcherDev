from tkinter import Tk, StringVar, IntVar, filedialog, W, E, END, PhotoImage
from tkinter.ttk import Frame, Label, Entry, Radiobutton, Button, Progressbar, Style
import sv_ttk
from Back.main import SoundcloudSnatcher
from os import getcwd
from threading import Thread
from Front.Desktop.locales.localesHander import getString


class GUI:
    def __init__(self):
        self.back_has_been_initialized = False
        self.downloading = False
        self.root = Tk()
        self.snatch_type = StringVar()
        self.Back = SoundcloudSnatcher
        self.error = Label(self.root)
        self.snatcher = Thread(target=self.getSnatchFunc())
        self.root.geometry("480x380")
        self.mainWindow()
        self.pb = Progressbar(
            self.loading_frame,
            orient='horizontal',
            mode='determinate',
            length=280
        )
        photo = PhotoImage(file = "logo.png")
        self.root.iconphoto(False, photo)
        self.root.title('Sound Snatcher')
        self.value_label = Label(self.loading_frame, text="0%")
        sv_ttk.set_theme("dark")
        self.root.mainloop()



    def mainWindow(self):
        self.main_frame = Frame(self.root)
        self.main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        l_url = Label(self.main_frame, text=getString('Labels','url'))
        l_url.config(font=('Helvetica bold', 14))
        l_url.pack(anchor='w', padx=10, pady=10)
        entry_frame = Frame(self.main_frame)
        entry_frame.pack(anchor='w')
        # snatch_type, url, specific_dir = None, no_dir = False
        self.url = Entry(entry_frame, width=40)
        self.url.pack()
        l_file_type = Label(self.main_frame, text=getString('Labels','file_type'))
        l_file_type.config(font=('Helvetica bold', 14))
        l_file_type.pack(anchor='w', padx=10, pady=10)
        file_type_frame = Frame(self.main_frame)
        file_type_frame.pack(anchor='w')

        self.snatch_type.set("playlist")
        r1 = Radiobutton(file_type_frame, text=getString('Radiobuttons','playlist'), variable=self.snatch_type, value="playlist")
        r1.pack(anchor = W)
        r2 = Radiobutton(file_type_frame, text=getString('Radiobuttons','song'), variable=self.snatch_type, value="song")
        r2.pack(anchor = W)
        l_path = Label(self.main_frame, text=getString('Labels','path'))
        l_path.config(font=('Helvetica bold', 14))
        l_path.pack(anchor='w', padx=10, pady=10)
        path_frame = Frame(self.main_frame)
        path_frame.pack(anchor='w')
        self.path = Entry(path_frame, width=40)
        self.path.insert(0, getcwd())
        self.path.grid(row=0, column=0)
        select_dir = Button(
            path_frame,
            text=getString('Buttons','browse'),
            command=self.selectDir
        )
        select_dir.grid(row=0, column=1, padx=5, pady=5)
        snatch_button = Button(
            self.main_frame,
            text=getString('Buttons','snatch'),
            command=self.snatchSongs
        )
        snatch_button.pack(padx=10, pady=10)
        self.loading_frame = Frame(self.main_frame)
        self.loading_frame.pack()

    def getSnatchFunc(self):
        if self.snatch_type.get() == 'playlist':
            return self.Back.snatchPlaylist
        else:
            return self.Back.snatchSong

    def snatchSongs(self):
        self.Back = SoundcloudSnatcher(self.snatch_type.get(),self.url.get(), self.path.get(), auto_run = False)
        def update_progress():
            try:
                self.error.pack_forget()
            except AttributeError:
                pass
            if self.snatcher.is_alive():
                index = self.Back.getCurrentIndex()
                total_songs = self.Back.getTotalPlaylistLength()
                percent = int(index / total_songs * 100)
            else:
                self.downloading = False
                percent = 100
                self.error = self.Back.getErrorMessage()
                if self.error is not None:
                    self.error = Label(self.main_frame, text=self.error)
                    self.error.pack()
                    self.back_has_been_initialized = False
            self.pb['value'] = percent
            self.value_label.config(text=f"{percent}%")
            if percent < 100:
                self.main_frame.after(100, update_progress)

        if not self.downloading:
            self.downloading = True
            self.pb.grid(row='0', column='0', padx=5)
            self.value_label.grid(row='0', column='1', padx=5)
            self.snatcher = Thread(target=self.getSnatchFunc())
            self.snatcher.start()
            self.main_frame.after(100, update_progress)



    def selectDir(self):
        dir = filedialog.askdirectory()
        self.path.delete(0, END)
        self.path.insert(0, dir)





