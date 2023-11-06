import asyncio
import os
import threading
import time
from tempfile import TemporaryFile
from cues import transform_wake_word_cues
import requests as r
from google.cloud import texttospeech
from gtts import gTTS
from pydub import AudioSegment
from pydub.playback import play
import json
import sys
from measure import timing


class TextToSpeechPlayer:
    def __init__(self, url, language, gender):
        self.client = texttospeech.TextToSpeechClient()
        self.url = url
        self.language = language
        self.gender = gender

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

    def save_cues_audio(text):
        # url = "https://lionlabs.co.in/ai/synthesize/"
        url = "http://localhost:8000/ai/synthesize/"
        exp = transform_wake_word_cues()
        for cue_type, values in exp.items():
            for lang, data in exp[cue_type].items():
                for gender in ['male', 'female']:
                    for content, number in data[gender].items():
                        print(f"Cue Type : {cue_type} {lang} {gender}")
                        response = r.post(url, json={
                            "text": content,
                            "language": lang,
                            "voice": gender,
                        }, headers={
                            'X-Device-Serial': '100000006486a9c4'
                        })

                        print(response.status_code)
                        
                        if response.status_code == 200:
                            dir_path = f"{os.getcwd()}/assets/voice_cues/{cue_type}/{lang}/{gender}"

                            # Construct the file path
                            os.makedirs(dir_path, exist_ok=True)

                            # Construct the file path
                            file_path = f"{dir_path}/{number}.mp3"
                            
                            # Open the file in binary write mode and write the contents
                            with open(file_path, 'wb') as audio_file:
                                audio_file.write(response.content)
                        else:
                            print(f"Failed to get audio content for {content}: {response.status_code}")
                        # sys.exit()

    def load_and_play(self, filename, use_thread=False):
        audio = AudioSegment.from_mp3(filename)
        if use_thread:
            playback_thread = threading.Thread(target=play, args=(audio,))
            playback_thread.start()

        # load_audio_time = time.time()
        # print(f"Time to load audio : {load_audio_time - time.time() + load_audio_time:.2f}")
        else:
            # print("Loaded Audio")
            play(audio)
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

    def play(self, text, headers):
        # Make a request to the Django API endpoint to get synthesized audio
        response = r.post(
            self.url,
            json={"text": text, "language": self.language,
                  "voice": self.gender},
            headers=headers,
        )

        # Check if the request was successful
        if response.status_code == 200:
            output_filename = "output.mp3"

            # Write the audio data to a temporary file
            with open(output_filename, "wb") as file:
                file.write(response.content)

            # Load and play the audio
            self.load_and_play(output_filename)

        else:
            print(
                f"Failed to get audio. Status code: {response.status_code}. Message: {response.text}")


@timing
async def output_voicev2(text: str, expect_return=False):
    tts = gTTS(text, lang='en')
    try:

        audio_data = tts.get_audio_data()

        play(AudioSegment(
            audio_data,
            frame_rate=tts.FRAME_RATE,
            sample_width=tts.sample_width,
            channels=1
        ))
    except Exception as e:
        print(f"Output Voice Exception : {e}")

    return expect_return


@timing
async def output_voice(text: str, expect_return=False):
    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(None, _output_voice_sync, text, expect_return)
    return result


def _output_voice_sync(text: str, expect_return=False):
    tts = gTTS(text, lang='en')
    fp = TemporaryFile()
    tts.write_to_fp(fp)
    fp.seek(0)
    song = AudioSegment.from_file(fp, format="mp3")
    play(song)
    return expect_return


def play_audio(audio_path: str):
    audio = AudioSegment.from_file(audio_path)
    play(audio)
    print(f"Playing: {audio_path}")


if __name__ == "__main__":
    player = TextToSpeechPlayer("", "", "")
    player.save_cues_audio()
    # player.cues_to_audio_files(audio_error_dict, "audio_error_cues")
    # player.cues_to_audio_files(wake_word_dict, "wake_word_cues")
    # player.cues_to_audio_files(audio_received_dict, "audio_received_cues")
    # player.cues_to_audio_files(awaiting_response_dict, "awaiting_response_cues")
    # player.cues_to_audio_files(chat_mode_activated_dict, "chat_mode_cues")
