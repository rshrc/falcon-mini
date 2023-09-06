import argparse
import json
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

load_dotenv()

API_URL = os.getenv('URL')

# nlp = spacy.load("en_core_web_sm")

nlp = English()


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


def output_voice(text: str):
    tts = gTTS(text, lang='en')

    fp = TemporaryFile()

    tts.write_to_fp(fp)
    fp.seek(0)
    song = AudioSegment.from_file(fp, format="mp3")
    play(song)


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


def update_conversation(input, output):
    conversation.append(
        {'role': 'user', 'content': input})
    conversation.append(
        {'role': 'assistant', 'content': output})
    print("Conversation Updated")


def process_instruction(source: sr.Recognizer):

    while True:
        audio = recognizer.listen(source)

        recognized_text = recognizer.recognize_google(audio)

        print(f"Recognized Instruction : {recognized_text}")

        doc = nlp(recognized_text)

        play_intent = any((token.text.lower() == "play" and (token.text.lower(
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
            output_voice("Sure thing! Stopping")
            return
        else:
            data = {
                'input': recognized_text, 'age': 4,
            }

            if len(conversation) > 0:
                data['conversation'] = json.dumps(conversation)

            response = r.post(API_URL, json=data)

            print(response.status_code)

            speech = response.json()['response']
            update_conversation(recognized_text, speech)

            print(f"Response : {conversation}")

            output_voice(speech)


def speech_to_text():

    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source)

        if True:
            print("Listening for Wake Word")

            audio = recognizer.listen(source)

            print("There was some audio input!")

            try:
                recognized_text = recognizer.recognize_google(audio)
                print(f"Recognized Text : {recognized_text}")

                wake_word = fuzz.partial_ratio(recognized_text, "hey google")

                print(f"Wake Word Spoken: {wake_word}")

                if wake_word > 70:
                    # output_voice(random.choice(
                    #     ['yes', 'yes tell me', 'sup', 'whats up', 'yo yo']))

                    while True:
                        audio = recognizer.listen(source)

                        recognized_text = recognizer.recognize_google(audio)

                        print(f"Recognized Instruction : {recognized_text}")

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
                            output_voice("Sure thing! Stopping")
                            return
                        else:
                            data = {
                                'input': recognized_text, 'age': 4,
                            }

                            if len(conversation) > 0:
                                data['conversation'] = json.dumps(conversation)

                            response = r.post(API_URL, json=data)

                            print(response.status_code)

                            speech = response.json()['response']
                            update_conversation(recognized_text, speech)

                            print(f"Response : {conversation}")

                            output_voice(speech)
                else:
                    print(f"Keep Sleeping")
            except Exception as e:
                print(f"Some Error Occoured : {e}")


audio_files = []


def load_audio_files():
    folder_path = "audio_files"

    for filename in os.listdir(folder_path):
        if filename.lower().endswith('.mp3'):
            audio_files.append(os.path.join(folder_path, filename))


def main():
    parser = argparse.ArgumentParser(
        description="Process input and optionally generate output audio.")
    parser.add_argument("-O", "--output", dest="output_text",
                        help="Output audio for the given input text")

    args = parser.parse_args()

    if args.output_text:
        print(f"Output {args.output_text}")
        output_voice(args.output_text)
    else:
        load_audio_files()
        print(f"Loaded {len(audio_files)} Songs & Rhymes")
        while True:
            speech_to_text()


if __name__ == "__main__":
    main()
