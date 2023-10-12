from google.cloud import texttospeech

import os

from pydub import AudioSegment, playback

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

        load_audio_time = time.time()
        print(f"Time to load audio : {load_audio_time - time.time() + load_audio_time:.2f}")

        print("Loaded Audio")
        playback.play(audio)
        print(f"To play : {time.time() - load_audio_time:.2f}")

    def text_to_speech(self, text, output_filename):
        self.synthesize_speech(text, output_filename)
        self.load_and_play(output_filename)


if __name__=="__main__":
    player = TextToSpeechPlayer()
    text = "Hello, this is a test for Google Text to Speech."
    output_filename = "output.mp3"
    player.text_to_speech(text, output_filename)


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
