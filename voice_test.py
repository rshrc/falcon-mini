from google.cloud import texttospeech
from utils.cues import wake_word_dict, awaiting_response_dict, audio_received_dict
import os
import threading

from pydub import audio_segment
from pydub.playback import play

import time
from pydub import AudioSegment
from google.cloud import texttospeech

class TextToSpeechPlayer:
    def __init__(self):
        self.client = texttospeech.TextToSpeechClient()

    def synthesize_speech(self, text, output_filename):
        start_time = time.time()

        # Set the text input to be synthesized
        synthesis_input = texttospeech.SynthesisInput(text=text)

        # Build the voice request
        voice = texttospeech.VoiceSelectionParams(
            language_code="en-US",
            name="en-US-Wavenet-F"
        )

        # Select the type of audio file you want
        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3
        )

        # Perform the text-to-speech request
        response = self.client.synthesize_speech(
            input=synthesis_input, voice=voice, audio_config=audio_config
        )

        response_time = time.time()
        print(f"Time for response to be back {response_time - start_time:.2f}")

        # Write the response to the output file
        with open(output_filename, "wb") as out:
            out.write(response.audio_content)

        write_time = time.time()
        print(f"Time to write response : {write_time - response_time:.2f}")

        print("Audio Stored")

    def load_and_play(self, filename):
        audio = AudioSegment.from_mp3(filename)
        playback_thread = threading.Thread(target=play, args=(audio,))
        playback_thread.start()

        # load_audio_time = time.time()
        # print(f"Time to load audio : {load_audio_time - time.time() + load_audio_time:.2f}")

        # print("Loaded Audio")
        # # play(audio)
        # print(f"To play : {time.time() - load_audio_time:.2f}")

    def text_to_speech(self, text, output_filename):
        self.synthesize_speech(text, output_filename)
        self.load_and_play(output_filename)


    def cues_to_audio_files(self, cue_dict, folder_name):
    # Ensure the folder exists
        if not os.path.exists(folder_name):
            os.makedirs(folder_name)

        for cue, idx in cue_dict.items():
            filename = f"{idx}.mp3"
            filepath = os.path.join(folder_name, filename)

            # Use the existing synthesize_speech method to save the cue as audio
            self.synthesize_speech(cue, filepath)

            print(f"Saved '{cue}' to {filepath}")


if __name__=="__main__":
    player = TextToSpeechPlayer()
    player.cues_to_audio_files(wake_word_dict, "wake_word_cues")
    player.cues_to_audio_files(audio_received_dict, "audio_received_cues")
    player.cues_to_audio_files(awaiting_response_dict, "awaiting_response_cues")


# def text_to_speech(text, output_filename):
#     # Initialize the client
#     client = texttospeech.TextToSpeechClient()

#     # Set the text input to be synthesized
#     synthesis_input = texttospeech.SynthesisInput(text=text)

#     # Build the voice request
#     voice = texttospeech.VoiceSelectionParams(
#         language_code="en-US",
#         name="en-US-Wavenet-F"
#     )

#     # Select the type of audio file you want
#     audio_config = texttospeech.AudioConfig(
#         audio_encoding=texttospeech.AudioEncoding.MP3
#     )

#     # Perform the text-to-speech request
#     response = client.synthesize_speech(
#         input=synthesis_input, voice=voice, audio_config=audio_config
#     )

#     # Write the response to the output file.
#     with open(output_filename, "wb") as out:
#         out.write(response.audio_content)
    
#     print("Audio Stored")

#     audio = AudioSegment.from_mp3("output.mp3")

#     print("Loaded Audio")
#     playback.play(audio)
    


# text = "Ba Ba Black Sheep have you any wool, yes sir yes sir, 3 bags full"
# output_filename = "output.mp3"
# text_to_speech(text, output_filename)
