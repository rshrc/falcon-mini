import argparse
import asyncio
import json
import os
import random
import time
from functools import wraps
from io import BytesIO
from tempfile import TemporaryFile
from display.utils import display

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

# nltk.download('averaged_perceptron_tagger')
# nltk.download('punkt')

def timing(f):

    def timed(*args, **kw):

        ts = time.time()
        result = f(*args, **kw)
        te = time.time()

        print('func:%r args:[%r, %r] took: %2.8f sec' %
              (f.__name__, args, kw, te-ts))
        return result

    return timed


load_dotenv()

API_URL = os.getenv('URL')

WAKE_WORD = os.getenv('WAKE_WORD').lower()

# Number of conversations that are kept track of
MEMORY_CONTEXT = 5

play_keywords = {'play', 'song', 'rhyme'}
stop_keywords = {'stop', 'quit', 'exit', 'end'}

# nlp = spacy.load("en_core_web_sm")

# nlp = English()

trie = None


@timing  # taking 0.0019 sec
@measure_memory_usage
def check_similar_song(user_input: str):
    print("Using V1 Search Algorithm")
    best_match_ratio = 0
    best_match_path = None

    for path in audio_files:
        ratio = fuzz.partial_ratio(
            user_input.lower(), os.path.basename(path).lower())
        if ratio > best_match_ratio:
            best_match_ratio = ratio
            best_match_path = path

    if best_match_path and best_match_ratio >= 70:  # Adjust the threshold as needed
        return True, best_match_path
    else:
        return False, None


@timing
@measure_memory_usage
async def output_voicev2(text: str, expect_return=False):
    tts = gTTS(text, lang='en')
    fp = BytesIO()

    tts.write_to_fp(fp)
    fp.seek(0)
    song = AudioSegment.from_file(fp, format="mp3")
    play(song)

    return expect_return


@timing
@measure_memory_usage
async def output_voice(text: str, expect_return=False):

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
@measure_memory_usage
def update_conversation(input, output):
    # Single Operation Conversation
    conversation.extend([
        {'role': 'user', 'content': input},
        {'role': 'assistant', 'content': output}
    ])
    print("Conversation Updated")


@measure_memory_usage
async def process_input(recognized_text):
    # doc = nlp(recognized_text)
    try:
        tokens = word_tokenize(recognized_text)
        tagged_tokens = pos_tag(tokens)

        # 0.00012 seconds in intent detection
        # play_intent = any(token.text.lower() in play_keywords or token.pos_ == "VERB" for token in doc)
        # stop_intent = any(token.text.lower() in stop_keywords or token.pos_ == "VERB" for token in doc)

        play_intent = any(word.lower() in play_keywords or pos ==
                        "VB" for word, pos in tagged_tokens)
        stop_intent = any(word.lower() in stop_keywords or pos ==
                        "VB" for word, pos in tagged_tokens)

    except Exception as e:
        play_intent = False
        stop_intent = False

    print(f"Play Intent? {play_intent}")
    print(f"Stop Intent? {stop_intent}")

    if play_intent:
        similar_song_found, song_path = check_similar_song(
            recognized_text)
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

        print(f"Response : {conversation}")
        display(speech)
        await output_voice(speech)


def voice_filler():
    return random.choice(seq=['yes', 'yes tell me', 'sup', 'whats up', 'yo yo'])


@measure_memory_usage
async def speech_to_text():
    with sr.Microphone() as source:

        recognizer.adjust_for_ambient_noise(source)

        listen = True

        if listen:
            print("Listening for Wake Word")

            audio = recognizer.listen(source)

            print("There was some audio input!")

            try:
                recognized_text = recognizer.recognize_google(audio).lower()
                print(f"Recognized Text : {recognized_text}")

                wake_word = fuzz.partial_ratio(recognized_text, WAKE_WORD)
                yes_wake_word = fuzz.partial_ratio(
                    recognized_text, f"yes google")

                print(f"Wake Word Spoken: {wake_word}")

                if wake_word > 70:
                    if recognized_text.lower().startswith(WAKE_WORD) and len(recognized_text) == len(WAKE_WORD):
                        while True:
                            # TODO: Trigger LED LIGHT
                            # response = await output_voice(voice_filler(), expect_return=True)

                            print("ARE WE READY TO LISTEN")
                            print("Microphone is back Online")

                            print("Listeing for second command!")
                            audio = recognizer.listen(source)

                            print("I GUESS WE ARE")

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
                print(f"Some Error Occoured : {e}")


audio_files = []


@measure_memory_usage
def load_audio_files():
    folder_path = "audio_files"

    for filename in os.listdir(folder_path):
        if filename.lower().endswith('.mp3'):
            audio_files.append(os.path.join(folder_path, filename))

    global trie  # Assuming trie is a global variable


@measure_memory_usage
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
        load_audio_files()
        print(f"Loaded {len(audio_files)} Songs & Rhymes")
        while True:
            await speech_to_text()


if __name__ == "__main__":
    asyncio.run(main())
