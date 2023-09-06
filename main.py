import argparse
import json
import sys
from multiprocessing import process
import os
import random
from email.mime import audio
from io import BytesIO
from tempfile import TemporaryFile
import asyncio
import requests as r
import spacy
import speech_recognition as sr
from dotenv import load_dotenv
from fuzzywuzzy import fuzz
from gtts import gTTS
from pydub import AudioSegment
from pydub.playback import play
from spacy.lang.en import English
import alsaaudio


load_dotenv()

API_URL = os.getenv('URL')

WAKE_WORD = os.getenv('WAKE_WORD').lower()


# nlp = spacy.load("en_core_web_sm")

nlp = English()

def mute_microphone():
    os.system('amixer set Capture nocap')

# Function to unmute the microphone
def unmute_microphone():
    os.system('amixer set Capture cap')

def check_similar_song(user_input: str):
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


def test_connection():
    pass


mp3_fp = BytesIO()


# for memory
conversation = []


recognizer = sr.Recognizer()
microphone = sr.Microphone()


def update_conversation(input, output):
    conversation.append(
        {'role': 'user', 'content': input})
    conversation.append(
        {'role': 'assistant', 'content': output})
    print("Conversation Updated")

async def process_input(recognized_text):
    doc = nlp(recognized_text)

    play_intent = any((token.text.lower() == "play" or (token.text.lower(
    ) == 'song' or token.text.lower() == 'rhyme')) or token.pos_ == "VERB" for token in doc)
    stop_intent = any(
        (token.text.lower() == "stop" or token.pos_ == "VERB") or
        (token.text.lower() == "quit" or token.pos_ == "VERB") or
        (token.text.lower() == "exit" or token.pos_ == "VERB") or
        (token.text.lower() == "end" or token.pos_ == "VERB")
        for token in doc
    )

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
            data['conversation'] = json.dumps(conversation)

        print(f"Line 126 {data}")

        response = r.post(API_URL, json=data)

        print(response.status_code)

        speech = response.json()['response']
        update_conversation(recognized_text, speech)

        print(f"Response : {conversation}")

        await output_voice(speech)

def voice_filler():
    return random.choice(seq=['yes', 'yes tell me', 'sup', 'whats up', 'yo yo'])

async def speech_to_text():
    with sr.Microphone() as source:
        
        recognizer.adjust_for_ambient_noise(source)

        if True:
            print("Listening for Wake Word")

            audio = recognizer.listen(source)

            print("There was some audio input!")

            try:
                recognized_text = recognizer.recognize_google(audio).lower()
                print(f"Recognized Text : {recognized_text}")

                wake_word = fuzz.partial_ratio(recognized_text, WAKE_WORD)

                print(f"Wake Word Spoken: {wake_word}")

                if wake_word > 70:
                    if recognized_text.lower().startswith(WAKE_WORD) and len(recognized_text) == len(WAKE_WORD):
                        while True:
                            # recognizer.pause_threshold()
                            # mute_microphone()
                            response = await output_voice(voice_filler(), expect_return=True)
                            
                            if response:

                                print("ARE WE READY TO LISTEN")
                                # unmute_microphone()
                                print("Microphone is back Online")
                                # break
                                # audio captured again after normal wake word is detected
                                # with sr.Microphone as source2:
                                print("Listeing for second command!")
                                audio = recognizer.listen(source)

                                print("I GUESS WE ARE")

                                recognized_text = recognizer.recognize_google(audio)

                                print(f"Recognized Instruction : {recognized_text}")

                                await process_input(recognized_text)
                        
                    else :
                        command = recognized_text.lower().replace(WAKE_WORD, "").strip()

                        await process_input(command)

                        
                else:
                    pass
                    print(f"Keep Sleeping")
            except Exception as e:
                print(f"Some Error Occoured : {e}")


audio_files = []


def load_audio_files():
    folder_path = "audio_files"

    for filename in os.listdir(folder_path):
        if filename.lower().endswith('.mp3'):
            audio_files.append(os.path.join(folder_path, filename))


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
