import argparse
import asyncio
import atexit
import json
import os
import random
import time
from concurrent.futures import ThreadPoolExecutor
from functools import wraps
from io import BytesIO
from tempfile import TemporaryFile
import multiprocessing
import nltk
import requests as r
import speech_recognition as sr
from dotenv import load_dotenv
from fuzzywuzzy import fuzz
from gtts import gTTS
from icecream.icecream import IceCreamDebugger
from nltk.tag import pos_tag
from nltk.tokenize import sent_tokenize, word_tokenize
from pydub import AudioSegment
from pydub.playback import play
from typing import List
from utils.cues import wake_word_cues, audio_received_cues, awaiting_response_cues
from voice_test import TextToSpeechPlayer
from mem_test import measure_memory_usage
from oled.lib import DisplayController
from utils.writer import read_config

ic = IceCreamDebugger()

os.environ['ALSA_WARNINGS'] = '0'

IDENTIFIER = read_config()['user']['id']

tts = TextToSpeechPlayer()

def timing(f):

    def timed(*args, **kw):

        ts = time.time()
        result = f(*args, **kw)
        te = time.time()

        ic(f'func:{f.__name__} args:{args} took: {te-ts:.8f} sec')
        return result

    return timed


load_dotenv()

API_URL = os.getenv('URL')

WAKE_WORD = os.getenv('WAKE_WORD').lower()

# Number of conversations that are kept track of
MEMORY_CONTEXT = 5

# play_keywords = {'play', 'song', 'rhyme'}
play_keywords = {
    "play",
    "start",
    "begin",
    "playback",
    "play song",
    "play video",
    "start music",
    "begin song",
    "play the",
    "start the"
}
# stop_keywords = {'stop', 'quit', 'exit', 'end'}
stop_keywords = {
    "stop",
    "pause",
    "halt",
    "end",
    "stop song",
    "pause video",
    "halt music",
    "end song",
    "stop the",
    "pause the"
}


# Example Usage:
display_controller = DisplayController()

@timing
def check_similar_song(user_input: str, directory_path: str):
    ic("Using V1 Search Algorithm")
    best_match_ratio = 0
    best_match_path = None

    # Iterate over files in the directory directly
    for filename in os.listdir(directory_path):
        # Check if the file is an audio file (based on extension, for example)
        # You can adjust this condition based on your requirements
        if filename.endswith('.mp3') or filename.endswith('.wav'):  # Add other audio extensions if needed
            ratio = fuzz.partial_ratio(user_input.lower(), filename.lower())
            if ratio > best_match_ratio:
                best_match_ratio = ratio
                best_match_path = os.path.join(directory_path, filename)

    if best_match_path and best_match_ratio >= 70:  # Adjust the threshold as needed
        return True, best_match_path
    else:
        return False, None


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
        ic(f"Output Voice Exception : {e}")

    return expect_return


@timing
async def output_voice(text: str, expect_return=False):
    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(None, _output_voice_sync2, text, expect_return)
    return result

def _output_voice_sync(text: str, expect_return=False):
    # Use multiprocessing.Pool to generate the audio in parallel
    pool = multiprocessing.Pool(processes=4)  # Adjust the number of processes as needed

    # Apply gTTS function to generate the audio in parallel
    results = [pool.apply_async(generate_audio, (text,)) for _ in range(4)]  # Adjust the number of processes as needed

    # Get the generated audios from the multiprocessing pool
    audios = [result.get() for result in results]

    # Close the multiprocessing.Pool
    pool.close()
    pool.join()

    # Combine the generated audios into a single audio segment
    song = combine_audios(audios)

    # Play the combined audio
    play_audio(song)

    return expect_return

def _output_voice_sync2(text: str, expect_return=False):
    tts = gTTS(text, lang='en')
    fp = TemporaryFile()
    tts.write_to_fp(fp)
    fp.seek(0)
    song = AudioSegment.from_file(fp, format="mp3")
    play(song)
    return expect_return

def generate_audio(text: str) -> AudioSegment:
    tts = gTTS(text, lang='en')
    fp = BytesIO()
    tts.save(fp)
    fp.seek(0)
    song = AudioSegment.from_file(fp, format="mp3")
    return song

def combine_audios(audios: List[AudioSegment]) -> AudioSegment:
    combined = audios[0]
    for audio in audios[1:]:
        combined += audio
    return combined

def play_audio(audio_path: str):
    audio = AudioSegment.from_file(audio_path)
    play(audio)
    ic(f"Playing: {audio_path}")


mp3_fp = BytesIO()


# for memory
conversation = []


recognizer = sr.Recognizer()
microphone = sr.Microphone()


@timing
def update_conversation(input, output):
    # Single Operation Conversation
    conversation.extend([
        {'role': 'user', 'content': input},
        {'role': 'assistant', 'content': output}
    ])
    ic("Conversation Updated")


@timing
async def process_input(recognized_text):
    # doc = nlp(recognized_text)
    display_controller.render_text_threaded_v2(random.choice(awaiting_response_cues))
    try:
        tokens = word_tokenize(recognized_text)

        bigrams = [" ".join(bigram) for bigram in zip(tokens[:-1], tokens[1:])]

        tagged_tokens = pos_tag(tokens)

        token_bigrams = [" ".join(bigram) for bigram in bigrams(tokens)]

        # play_intent = any(word.lower() in play_keywords or pos ==
        #                 "VB" for word, pos in tagged_tokens)
        # stop_intent = any(word.lower() in stop_keywords or pos ==
        #                 "VB" for word, pos in tagged_tokens)

        play_intent = any(word.lower() in play_keywords for word, pos in tagged_tokens) or \
                      any(bigram.lower() in play_keywords for bigram in token_bigrams)
        
        # Check for stop intent
        stop_intent = any(word.lower() in stop_keywords for word, pos in tagged_tokens) or \
                      any(bigram.lower() in stop_keywords for bigram in token_bigrams)
        
        if play_intent and any(pos == "VB" for word, pos in tagged_tokens):
            play_intent = False
            
        if stop_intent and any(pos == "VB" for word, pos in tagged_tokens):
            stop_intent = False


    except Exception as e:
        play_intent = False
        stop_intent = False

    ic(f"Play Intent -> {play_intent}")
    ic(f"Stop Intent -> {stop_intent}")

    if play_intent:
        similar_song_found, song_path = check_similar_song(
            recognized_text, 'audio_files/')
        ic(
            f"Similar Song Found ? {similar_song_found} and Path {song_path}")

        if song_path is not None:
            play_audio(song_path)
            update_conversation(
                recognized_text, f"Played song {song_path}")
        else:
            random_song = random.choice(audio_files)
            update_conversation(random_song, f"Played song {random_song}")
            play_audio(random_song)
    elif stop_intent:
        await output_voice("Sure thing! Stopping")
        return
    else:
        data = {
            'input': recognized_text, 'child_id': IDENTIFIER,
        }

        ic(data)

        if len(conversation) > 0:
            data['conversation'] = json.dumps(conversation[:MEMORY_CONTEXT])

        ic(f"POST DATA {data}")

        response = r.post(API_URL, json=data)

        ic(response.status_code)

        speech = response.json()['response']
        update_conversation(recognized_text, speech)

        # ic(f"Response : {conversation}")
        display_controller.render_text_threaded_v2(speech)
        # await output_voice(speech)
        tts.text_to_speech(speech, "output.mp3")


def voice_filler():
    return random.choice(seq=['yes', 'yes tell me', 'sup', 'whats up', 'yo yo'])

@timing
async def speech_to_text():

    with sr.Microphone() as source:
        try:
            recognizer.adjust_for_ambient_noise(source, duration=1)
            recognizer.energy_threshold =  7000
            ic("Energy threshold:", recognizer.energy_threshold)

            listen = True

            if listen:
                ic("Listening for Wake Word")
                display_controller.render_text_threaded_v2(random.choice(wake_word_cues))
                audio = recognizer.listen(source)
                display_controller.render_text_threaded_v2(random.choice(audio_received_cues))
                ic("There was some audio input!")

                try:
                    recognized_text = recognizer.recognize_google(audio).lower()
                    ic(f"Recognized Text : {recognized_text}")

                    wake_word = fuzz.partial_ratio(recognized_text, WAKE_WORD)
                    yes_wake_word = fuzz.partial_ratio(
                        recognized_text, f"hey panda")

                    ic(f"Wake Word Spoken: {wake_word}")

                    if wake_word > 70:
                        if recognized_text.lower().startswith(WAKE_WORD) and len(recognized_text) == len(WAKE_WORD):
                            while True:
                                ic("Preparing for Audio I/O")

                                ic("Listeing for second command!")
                                display_controller.render_text_threaded_v2(voice_filler())
                                audio = recognizer.listen(source)
                                display_controller.render_text_threaded_v2("Ummm...")
                                ic("Resuming Conversation")

                                recognized_text = recognizer.recognize_google(
                                    audio)

                                ic(
                                    f"Recognized Instruction : {recognized_text}")

                                await process_input(recognized_text)

                        else:
                            command = recognized_text.lower().replace(WAKE_WORD, "").strip()

                            await process_input(command)

                    else:
                        pass
                        ic(f"Keep Sleeping")
                except Exception as e:
                    display_controller.render_text_threaded_v2("Something happened?")
                    ic(f"Some Error Occoured : {e}")
        except Exception as e:
            display_controller.render_text_threaded_v2("I heard some noise")
            ic(f"Something Crashed {e}")


audio_files = []


@timing
def load_audio_files():
    folder_path = "audio_files"

    for filename in os.listdir(folder_path):
        if filename.lower().endswith('.mp3'):
            audio_files.append(os.path.join(folder_path, filename))

@timing
async def main():
    parser = argparse.ArgumentParser(
        description="Process input and optionally generate output audio.")
    parser.add_argument("-O", "--output", dest="output_text",
                        help="Output audio for the given input text")

    args = parser.parse_args()

    if args.output_text:
        ic(f"Output {args.output_text}")
        await output_voice(args.output_text)
    else:
        # load_audio_files()
        # load data.yaml config file
        ic(f"Loaded {len(audio_files)} Songs & Rhymes")
        while True:
            await speech_to_text()

def cleanup():
    display_controller.render_text_threaded_v2("Not Running...")
    ic("Cleaning up before exiting...")   

def exit_handler():
    cleanup()

atexit.register(exit_handler)

if __name__ == "__main__":
    asyncio.run(main())
