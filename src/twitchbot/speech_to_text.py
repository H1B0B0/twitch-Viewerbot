import os
from faster_whisper import WhisperModel
import tkinter as tk
import customtkinter as ctk
# from transformers import AutoProcessor, PaliGemmaForConditionalGeneration
# import torch

def audiototext(SPEECH_FILE):
    model_size = "medium"
    segmentresult = []

    # Run on GPU with FP16
    # model = WhisperModel(model_size, device="cuda", compute_type="float16")
    model_path = f"~/.cache/huggingface/transformers/{model_size}"
    if not os.path.exists(os.path.expanduser(model_path)):
        root = tk.Tk()
        ctk.CTkMessageBox(
            root,
            title="Model Download Required",
            message=f"The model '{model_size}' is not downloaded. Please download the model first.",
            icon="warning",
            button_type="ok",
            default_button="ok"
        )
        root.mainloop()
        return
    # or run on GPU with INT8
    # model = WhisperModel(model_size, device="cuda", compute_type="int8_float16")
    # or run on CPU with INT8
    model = WhisperModel(model_size, device="cpu", compute_type="int8")

    segments, info = model.transcribe(SPEECH_FILE, beam_size=5)

    print("Detected language '%s' with probability %f" % (info.language, info.language_probability))

    for segment in segments:
        print((segment.start, segment.end, segment.text))
        segmentresult.append(segment.text)
    return segmentresult
    

# def generate_chat_response(transcription_text, game_name, number_of_messages=5):
#     model_id = "google/gemma-2b"

#     # Load pre-trained model and processor
#     model = PaliGemmaForConditionalGeneration.from_pretrained(model_id).eval()
#     processor = AutoProcessor.from_pretrained(model_id)

#     # Join the transcriptions into a single string
#     transcription_text = ' '.join(transcription_text)

#     # Generate the chat response
#     model_inputs = processor(text=transcription_text, return_tensors="pt")
#     input_len = model_inputs["input_ids"].shape[-1]

#     with torch.inference_mode():
#         generation = model.generate(**model_inputs, max_new_tokens=100, do_sample=False)
#         generation = generation[0][input_len:]
#         response = processor.decode(generation, skip_special_tokens=True)

#     return response
