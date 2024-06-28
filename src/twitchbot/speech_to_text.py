import os
import sys
import torch
import platform
import customtkinter as ctk
from queue import Queue, Empty
from tkinter import messagebox
from faster_whisper import WhisperModel
from transformers import AutoTokenizer, AutoModelForCausalLM
from threading import Thread
from pathlib import Path

# Global variable to store the progress and download_window
download_info = {}

queue = Queue()

current_path = Path(__file__).resolve().parent
ICON = current_path/"interface_assets"/"R.ico"
THEME = current_path/"interface_assets"/"purple.json"

class TextboxStdout:
    def __init__(self, textbox):
        self.textbox = textbox
        self.text = ""

    def write(self, s):
        self.text += s
        self.textbox.configure(state=ctk.NORMAL)
        self.textbox.insert(ctk.END, s)
        self.textbox.see(ctk.END)
        self.textbox.configure(state=ctk.DISABLED)
        self.text = ""

    def flush(self):
        pass  # In this case, we don't need to do anything to flush.

def update_textbox(text):
    text.insert(ctk.END, sys.stdout.text)
    text.see(ctk.END)

    # Schedule the function to run again after 500ms
    text.after(500, update_textbox, text)

def instantiate_model(download_window, progress, text):
    model_size = "small"
    sys.stdout = TextboxStdout(text)
    device = "cuda" if torch.cuda.is_available() else "cpu"  # Check if GPU is available


    # Instantiate the WhisperModel
    print("Starting to download the audiomodel...")
    WhisperModel(model_size, device=device, compute_type="int8")
    print("WhisperModel downloaded.")

    print("Starting to download the tokenizer...")
    AutoTokenizer.from_pretrained("google/gemma-2b")
    print("Tokenizer downloaded.")

    print("Starting to download the model...")
    AutoModelForCausalLM.from_pretrained("google/gemma-2b")
    print("Model downloaded.")

    # Put a message in the queue
    queue.put("Download finished")

def download_model():
    model_size = "small"
    model_path = f"~/.cache/huggingface/transformers/{model_size}"
    model_path2 = f"~/.cache/huggingface/transformers/hub/models--google--gemma-2b"
    if not (os.path.exists(os.path.expanduser(model_path)) and os.path.exists(os.path.expanduser(model_path2))):
        messagebox.showinfo("Download", "The application need to download the model for the first time.\n Please wait for a while.\n The model size is 1.5GB.")
        
        # Create a new window
        download_window = ctk.CTk()
        download_window.title("Downloading Model")
        download_window.geometry("500x200")

        ctk.set_appearance_mode("System")
        ctk.set_default_color_theme(THEME)
        # Set the window icon
        if platform.system() == 'Windows':
            download_window.iconbitmap(ICON)

        # Create a progress bar in indeterminate mode
        progress = ctk.CTkProgressBar(download_window, mode='indeterminate')
        progress.pack(pady=10, padx=10)

        # Create a text box in the download_window
        text = ctk.CTkTextbox(download_window)
        text.pack(side="top", fill="both", expand=True)


        text.after(100, update_textbox, text)

        progress.start()

        def check_queue():
            try:
                msg = queue.get_nowait()
                if msg == "Download finished":
                    progress.stop()
                    download_window.destroy()
            except Empty:  # Catch Empty from queue module
                pass

            # Schedule the function to run again after 100ms
            download_window.after(100, check_queue)

        check_queue()

        # Run instantiate_model in the main thread
        Thread(target=instantiate_model, args=(download_window, progress, text)).start()
        download_window.mainloop()
    else :   
       return
    
def create_sentence(transcription_segments, game_name, number_of_messages):
    # Concatenate transcription segments into a single string
    transcription = " ".join(transcription_segments)
    
    # Simplify the prompt
    input_text = f"Transcription: {transcription} Based on the above, generate a continuation in the same language and in the context of the game {game_name}."
    
    # Load a more appropriate model for generating conversational text
    tokenizer = AutoTokenizer.from_pretrained("jondurbin/airoboros-gpt-3.5-turbo-100k-7b")
    model = AutoModelForCausalLM.from_pretrained("jondurbin/airoboros-gpt-3.5-turbo-100k-7b")
    
    encoded_input = tokenizer(input_text, return_tensors="pt")
    output_tokens = model.generate(
        **encoded_input,
        max_length=500,
        num_return_sequences=1,
        do_sample=True,
        top_p=0.95,
        temperature=0.7
    )
    
    # Decode the output tokens to get the generated text
    generated_text = tokenizer.decode(output_tokens[0], skip_special_tokens=True)
    return generated_text

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
    # download_model()
    text = audiototext("output.mp3")
    response = create_sentence(text, "test", 1)
    print(response)