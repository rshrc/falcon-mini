import argparse
import asyncio
import json
import os
import random
import time
from functools import wraps
from io import BytesIO
from tempfile import TemporaryFile
from oled.lib import DisplayController
import nltk
import requests as r
import speech_recognition as sr
from dotenv import load_dotenv
from fuzzywuzzy import fuzz
from gtts import gTTS

from nltk.tag import pos_tag
from nltk.tokenize import sent_tokenize, word_tokenize
from pydub import AudioSegment
from pydub.playback import play
from mem_test import measure_memory_usage
import atexit
from concurrent.futures import ThreadPoolExecutor

os.environ['ALSA_WARNINGS'] = '0'

def timing(f):

    def timed(*args, **kw):

        ts = time.time()
        result = f(*args, **kw)
        te = time.time()

        print(f'func:{f.__name__} args:{args} took: {te-ts:.8f} sec')
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
    print("Using V1 Search Algorithm")
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
        print(f"Line 99 : {e}")

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
    print("Conversation Updated")


@timing
async def process_input(recognized_text):
    # doc = nlp(recognized_text)
    display_controller.render_text_threaded_v2("Let me think....")
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

    print(f"Play Intent? {play_intent}")
    print(f"Stop Intent? {stop_intent}")

    if play_intent:
        similar_song_found, song_path = check_similar_song(
            recognized_text, 'audio_files/')
        print(
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
            'input': recognized_text, 'age': 4,
        }

        if len(conversation) > 0:
            data['conversation'] = json.dumps(conversation[:MEMORY_CONTEXT])

        print(f"POST DATA {data}")

        response = r.post(API_URL, json=data)

        print(response.status_code)

        speech = response.json()['response']
        update_conversation(recognized_text, speech)

        # print(f"Response : {conversation}")
        display_controller.render_text_threaded_v2(speech)
        await output_voice(speech)


def voice_filler():
    return random.choice(seq=['yes', 'yes tell me', 'sup', 'whats up', 'yo yo'])

@timing
async def speech_to_text_v2():
    recognizer = sr.Recognizer()
    microphone = sr.Microphone()
    
    recognizer.adjust_for_ambient_noise(microphone, duration=1)
    recognizer.energy_threshold = 7000
    print("Energy threshold:", recognizer.energy_threshold)

    listen = True

    if listen:
        print("Listening for Wake Word")
        display_controller.render_text_threaded_v2("Listening for wake word")
        
        with microphone as source:
            audio = recognizer.listen(source)
            display_controller.render_text_threaded_v2("Hmmmmmm.....")
            print("There was some audio input!")

            try:
                recognized_text = recognizer.recognize_google(audio).lower()
                print(f"Recognized Text : {recognized_text}")

                with ThreadPoolExecutor() as executor:
                    wake_word_future = executor.submit(fuzz.partial_ratio, recognized_text, WAKE_WORD)
                    yes_wake_word_future = executor.submit(fuzz.partial_ratio, recognized_text, "hey panda")



                wake_word = wake_word_future.result()

                print(f"Wake Word Spoken: {wake_word}")

                if wake_word > 70:
                    if recognized_text.lower().startswith(WAKE_WORD) and len(recognized_text) == len(WAKE_WORD):
                        while True:
                            print("Preparing for Audio I/O")

                            print("Listeing for second command!")
                            display_controller.render_text_threaded_v2(voice_filler())
                            audio = recognizer.listen(source)
                            display_controller.render_text_threaded_v2("Ummm...")
                            print("Resuming Conversation")

                            recognized_text = recognizer.recognize_google(
                                audio)

                            print(
                                f"Recognized Instruction : {recognized_text}")

                            await process_input(recognized_text)

                    else:
                        command = recognized_text.lower().replace(WAKE_WORD, "").strip()

                        await process_input(command)
                        
            except Exception as e:
                print(f"Error recognizing speech: {e}")

@timing
async def speech_to_text():

    with sr.Microphone() as source:
        try:
            recognizer.adjust_for_ambient_noise(source, duration=1)
            recognizer.energy_threshold =  7000
            print("Energy threshold:", recognizer.energy_threshold)

            listen = True

            if listen:
                print("Listening for Wake Word")
                display_controller.render_text_threaded_v2("Listening for wake word")
                audio = recognizer.listen(source)
                display_controller.render_text_threaded_v2("Hmmmmmm.....")
                print("There was some audio input!")

                try:
                    recognized_text = recognizer.recognize_google(audio).lower()
                    print(f"Recognized Text : {recognized_text}")

                    wake_word = fuzz.partial_ratio(recognized_text, WAKE_WORD)
                    yes_wake_word = fuzz.partial_ratio(
                        recognized_text, f"hey panda")

                    print(f"Wake Word Spoken: {wake_word}")

                    if wake_word > 70:
                        if recognized_text.lower().startswith(WAKE_WORD) and len(recognized_text) == len(WAKE_WORD):
                            while True:
                                print("Preparing for Audio I/O")

                                print("Listeing for second command!")
                                display_controller.render_text_threaded_v2(voice_filler())
                                audio = recognizer.listen(source)
                                display_controller.render_text_threaded_v2("Ummm...")
                                print("Resuming Conversation")

                                recognized_text = recognizer.recognize_google(
                                    audio)

                                print(
                                    f"Recognized Instruction : {recognized_text}")

                                await process_input(recognized_text)

                        else:
                            command = recognized_text.lower().replace(WAKE_WORD, "").strip()

                            await process_input(command)

                    else:
                        pass
                        print(f"Keep Sleeping")
                except Exception as e:
                    display_controller.render_text_threaded_v2("Something happened?")
                    print(f"Some Error Occoured : {e}")
        except Exception as e:
            display_controller.render_text_threaded_v2("I heard some noise")
            print(f"Something Crashed {e}")


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
        print(f"Output {args.output_text}")
        await output_voice(args.output_text)
    else:
        # load_audio_files()
        print(f"Loaded {len(audio_files)} Songs & Rhymes")
        while True:
            await speech_to_text()

def cleanup():
    display_controller.render_text_threaded_v2("Not Running...")
    print("Cleaning up before exiting...")   

def exit_handler():
    cleanup()

atexit.register(exit_handler)

if __name__ == "__main__":
    asyncio.run(main())
