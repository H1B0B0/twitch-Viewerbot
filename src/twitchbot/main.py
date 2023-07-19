import os
import customtkinter
from threading import Thread
from tkinter import filedialog
from viewer_bot import ViewerBot

SLIDER_MIN = 1000
SLIDER_MAX = 10000

class ViewerBotGUI(customtkinter.CTk):
    def __init__(self):
        super().__init__()
        customtkinter.set_appearance_mode("System")
        self.title("Viewerbot")
        from pathlib import Path
        self.current_dir = Path(__file__).resolve().parent.parent
        # try catch if we are on linux distribution
        try:
            self.wm_iconbitmap(os.path.join(self.current_dir, "..", "images", "R.ico"))
        except:
            pass
        customtkinter.set_default_color_theme(os.path.join(self.current_dir, "..", "interface_theme", "purple.json"))
        self.nb_requests = 0
        self.slider = 0
        
        # Label for number of threads
        nb_threads_label = customtkinter.CTkLabel(self, text="Number of threads:")
        nb_threads_label.grid(column=0, row=0, padx=10, pady=10)
        
        # Entry for number of threads
        self.nb_threads_entry = customtkinter.CTkEntry(self)
        self.nb_threads_entry.grid(column=1, row=0, padx=10, pady=10)
        
        # Label for Twitch channel name
        channel_name_label = customtkinter.CTkLabel(self, text="Twitch channel name:")
        channel_name_label.grid(column=0, row=1, padx=10, pady=10)
        
        # Entry for Twitch channel name
        self.channel_name_entry = customtkinter.CTkEntry(self)
        self.channel_name_entry.grid(column=1, row=1, padx=10, pady=10)

        # Label for proxy type
        proxy_type = customtkinter.CTkLabel(self, text="Proxy type")
        proxy_type.grid(column=0, row=2, columnspan=2, padx=10, pady=0)

        # select proxy type
        self.segemented_button_var = customtkinter.StringVar(value="http")
        self.segemented_button = customtkinter.CTkSegmentedButton(self, values=["http", "socks4", "socks5", "all"], variable=self.segemented_button_var)
        self.segemented_button.grid(column=0, row=3, columnspan=2, padx=10, pady=5)

        self.slider = customtkinter.CTkSlider(self, from_=SLIDER_MIN, to=SLIDER_MAX, command=self.slider_event)
        self.slider.set(SLIDER_MAX)
        self.slider.grid(column=0, row=5, columnspan=2, padx=10, pady=0)

        # Label for timeout
        self.timeout = customtkinter.CTkLabel(self, text=f"timeout: {int(self.slider.get())}")
        self.timeout.grid(column=0, row=4, columnspan=2, padx=10, pady=0)
        
        # Button to start the bot
        start_button = customtkinter.CTkButton(self, text="Start bot")
        start_button.grid(column=0, row=6, padx=10, pady=10)
        start_button.configure(command=self.start_bot)
        
        # Button to stop the bot
        stop_button = customtkinter.CTkButton(self, text="Stop", state="normal")
        stop_button.grid(column=1, row=6, padx=10, pady=10)
        stop_button.configure(command=self.stop_bot)
        
        self.nb_requests_label = customtkinter.CTkLabel(self, text="Number of requests: 0")
        self.nb_requests_label.grid(column=0, row=7, columnspan=2, padx=10, pady=2)
        # Label for status
        self.status_label = customtkinter.CTkLabel(self, text="Status: Stopped")
        self.status_label.grid(column=0, row=8, columnspan=2, padx=10, pady=2)
        
        # Variables for status and threads
        self.status = "Stopped"
        self.threads = []
        self.show_dialog()

    def slider_event(self, value):
        self.timeout.configure(text=f"timeout: {int(self.slider.get())}")
        
    def start_bot(self):
        if self.status == "Stopped":
            nb_of_threads = self.nb_threads_entry.get()
            self.channel_name = self.channel_name_entry.get()
            self.bot = ViewerBot(nb_of_threads, self.channel_name, self.proxylist, self.proxy_imported, self.slider.get(), type_of_proxy=self.segemented_button_var)
            self.thread = Thread(target=self.bot.main)
            self.after(50, self.configure_label)
            self.thread.daemon = True
            self.thread.start()
            # Change status and disable/enable buttons
            self.status = "Running"
            self.nb_threads_entry.configure(state="disabled")
            self.channel_name_entry.configure(state="disabled")
            self.segemented_button.configure(state="disabled")
            self.slider.configure(state="disabled")
            # Update status label and buttons
            self.status_label.configure(text=f"Status: {self.status}")
            # Append thread to list of threads
            self.threads.append(self.thread)         
        
    def stop_bot(self):
        if self.status == "Running":
            # Change status and disable/enable buttons
            self.status = "Stopped"
            self.nb_threads_entry.configure(state="normal")
            self.channel_name_entry.configure(state="normal")
            self.segemented_button.configure(state="normal")
            self.slider.configure(state="normal")
            # Update status label and buttons
            self.status_label.configure(text=f"Status: {self.status}")
            self.bot.stop()

    def configure_label(self):
        self.nb_requests_label.configure(text=f"Number of requests: {self.bot.nb_requests}")
        self.update_idletasks()
        app.after(50, app.configure_label)

    def show_dialog(self):
        self.proxylist = []
        # create new window for the parameters
        self.dialog = customtkinter.CTkToplevel(self)
        self.dialog.title("Parameters")
        # Button for import proxy list
        open_file_button = customtkinter.CTkButton(self.dialog, text="import your proxy list")
        open_file_button.grid(column=1, row=1, padx=10, pady=10)
        open_file_button.configure(command=self.on_open_file) 

        scraped_button = customtkinter.CTkButton(self.dialog, text="scraped automatically proxy")
        scraped_button.grid(column=1, row=2, padx=10, pady=10)
        scraped_button.configure(command=self.scraped_proxy) 

        self.dialog.protocol("WM_DELETE_WINDOW", self.scraped_proxy)
        # center the parameters window about the object
        self.dialog.update_idletasks()
        self.wait_window(self.dialog)
        
    def scraped_proxy(self):
        self.proxylist = None
        self.proxy_imported = False
        self.dialog.destroy()

    # validation button
    def on_open_file(self):
        file_path = filedialog.askopenfilenames(filetypes=[("Text Files", "*.txt")])
        for path in file_path:
            with open(path, 'r') as f:
                for line in f:
                    self.proxylist.append(line.strip())
        self.proxy_imported = True
        # close the parameters window
        self.dialog.destroy()                   

if __name__ == '__main__':
    app = ViewerBotGUI()
    app.mainloop()