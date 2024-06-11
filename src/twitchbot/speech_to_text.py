import os
import sys
import platform

import customtkinter as ctk
from tkinter import messagebox
from faster_whisper import WhisperModel
from transformers import AutoTokenizer, AutoModelForCausalLM
from threading import Thread
from pathlib import Path

# Global variable to store the progress and download_window
download_info = {}

current_path = Path(__file__).resolve().parent
ICON = current_path/"interface_assets"/"R.ico"
THEME = current_path/"interface_assets"/"purple.json"

class TextRedirector(object):
    def __init__(self, widget):
        self.widget = widget

    def write(self, str):
        self.widget.insert(ctk.END, str)
        self.widget.see(ctk.END)

    def flush(self):
        pass

def instantiate_model(download_window, progress):
    
    model_size = "medium"

    text = ctk.CTkTextbox(download_window)
    text.pack(side="top", fill="both", expand=True)
    sys.stdout = TextRedirector(text)

    # Instantiate the WhisperModel
    audio = WhisperModel(model_size, device="cpu", compute_type="int8")

    # Redirect stdout to the text box
    old_stdout = sys.stdout
    sys.stdout = TextRedirector(text)

    tokenizer = AutoTokenizer.from_pretrained("google/gemma-2b")
    model = AutoModelForCausalLM.from_pretrained("google/gemma-2b")

    # Restore stdout
    sys.stdout = old_stdout

    # Store the model in the global variable
    download_info['audiomodel'] = audio
    download_info['tokenizer'] = tokenizer
    download_info['model'] = model

    progress.stop()
    download_window.destroy()

    console_window.mainloop()

def download_model():
    model_size = "medium"
    model_path = f"~/.cache/huggingface/transformers/{model_size}"
    model_path2 = f"~/.cache/huggingface/transformers/hub/models--google--gemma-2b"
    if not (os.path.exists(os.path.expanduser(model_path)) and os.path.exists(os.path.expanduser(model_path2))):
        messagebox.showinfo("Download", "The application need to download the model for the first time.\n Please wait for a while.\n The model size is 1.5GB.")
        
        # Create a new window
        download_window = ctk.CTk()
        download_window.title("Downloading Model")

        ctk.set_appearance_mode("System")
        ctk.set_default_color_theme(THEME)
        # Set the window icon
        if platform.system() == 'Windows':
            download_window.iconbitmap(ICON)

        # Create a progress bar in indeterminate mode
        progress = ctk.CTkProgressBar(download_window, mode='indeterminate')
        progress.pack(pady=10, padx=10)

        progress.start()

        # Run instantiate_model in the main thread
        download_window.after(1000, instantiate_model, download_window, progress)  # Change this line
        download_window.mainloop()
    else :   
       return
    
def create_sentence(transcription, game_name, number_of_messages):

    tokenizer = AutoTokenizer.from_pretrained("google/gemma-2b")
    model = AutoModelForCausalLM.from_pretrained("google/gemma-2b")

    # Access the model from the global variable
    response = tokenizer(f"This is a transcription from a {game_name} stream. Please generate at least {number_of_messages} sentences to continue the conversation. Please reply in the language of the stream. And if you aren't inspired, you can generate just emoji reactions. We need some reaction in the chat. Write the sentence at the first person. Here is the Twitch transcription: {transcription}", return_tensors="pt")
    response = model.generate(**response)
    return response

def audiototext(SPEECH_FILE):
    model_size = "medium"
    segmentresult = []


    audio = WhisperModel(model_size, device="cpu", compute_type="int8")

    segments, info = audio.transcribe(SPEECH_FILE, beam_size=5)

    print("Detected language '%s' with probability %f" % (info.language, info.language_probability))

    for segment in segments:
        print((segment.start, segment.end, segment.text))
        segmentresult.append(segment.text)
    return segmentresult


if __name__ == "__main__":
    download_model()
    #audiototext("C:/Users/HP/Downloads/2021-10-16_14-58-00.wav")
    #create_sentence("This is a test", "test", 1)