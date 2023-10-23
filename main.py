import argparse
import asyncio
import atexit
import json
import multiprocessing
import os
import sys
import time
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = f"{os.getcwd()}/gconfig.json"
import subprocess
import random
import signal
from serial_number import get_serial_number, serial_number

import gc

import requests as r
import speech_recognition as sr
from dotenv import load_dotenv
from fuzzywuzzy import fuzz
from icecream.icecream import IceCreamDebugger
from nltk.tag import pos_tag
from nltk.tokenize import word_tokenize
from config import get_configuration
from utils import store_data, get_last_n

# from db.utils import get_data_in_date_range, get_last_n, store_data
from disply_lib import DisplayController
import intents
from config import get_configuration, read_config, DeviceConfig
from cues import (audio_received_cues, audio_received_dict,
                        awaiting_response_cues, awaiting_response_dict,
                        wake_word_cues, wake_word_dict, chat_mode_activated_dict, chat_mode_activated_cues)
from measure import timing
from voice import TextToSpeechPlayer, output_voice, play_audio

def increase_volume():
    subprocess.call(['sudo', '/home/rishi/falcon_mini/scripts/setup/set_volume.sh'])

increase_volume()

BPRAP = "voice_cues"

ic = IceCreamDebugger()

os.environ['ALSA_WARNINGS'] = '0'

IDENTIFIER = read_config()['user']['id']

headers = {
    'X-Device-Serial': get_serial_number()
}

tts = TextToSpeechPlayer()

load_dotenv()

API_URL = os.getenv('URL')
BASE_URL = os.getenv('BASE_URL')
WAKE_WORD = os.getenv('WAKE_WORD').lower()

test_device_uuid = "5caa2cef-3411-4368-9a6d-f9eefe9c34f9"

CHAT_MODE = False
ASK_FOR_WAKE_WORD = True


# Configure Device etc
configuration = get_configuration(BASE_URL, test_device_uuid)

MEMORY_CONTEXT = 0

if isinstance(configuration, str):
    print(configuration)
elif isinstance(configuration, DeviceConfig):
    print(configuration.to_dict)

    MEMORY_CONTEXT = configuration.memory.context_limit

    print(f"Memory Context {MEMORY_CONTEXT}")
else:
    print("Unexpected type of configuration data.")

# sys.exit()


# Number of conversations that are kept track of, depend on get_configuration

# Example Usage:
display_controller = DisplayController()


@timing
def check_similar_song(user_input: str, directory_path: str):
    print("Using V1 Search Algorithm")
    best_match_ratio = 0
    best_match_path = None

    # Iterate over files in the directory directly
    for filename in os.listdir(directory_path):
        if filename.endswith('.mp3') or filename.endswith('.wav'):
            ratio = fuzz.partial_ratio(user_input.lower(), filename.lower())
            if ratio > best_match_ratio:
                best_match_ratio = ratio
                best_match_path = os.path.join(directory_path, filename)

    if best_match_path and best_match_ratio >= 70:  # Adjust the threshold as needed
        return True, best_match_path
    else:
        return False, None


# for memory, TODO: convert to database
conversation = []


recognizer = sr.Recognizer()
microphone = sr.Microphone()


@timing
def update_conversation(input, output):

    # store in DB
    store_data(input, output)
    
    # Single Operation Conversation
    # conversation.extend([
    #     {'role': 'user', 'content': input},
    #     {'role': 'assistant', 'content': output}
    # ])
    # print("Conversation Updated")


@timing
async def process_input(recognized_text):
    # doc = nlp(recognized_text)
    awaiting_response_cue = random.choice(awaiting_response_cues)
    # play(f"voice_cues/awaiting_response_cues/{awaiting_response_dict[awaiting_response_cue]}")
    # tts.text_to_speech(awaiting_response_cue, "awaiting_response_cue.mp3")
    display_controller.render_text_threaded_v2(awaiting_response_cue)
    tts.load_and_play(
        f"{os.getcwd()}/assets/voice_cues/awaiting_response_cues/{awaiting_response_dict[awaiting_response_cue]}.mp3", use_thread=True)

    try:
        tokens = word_tokenize(recognized_text)

        bigrams = [" ".join(bigram) for bigram in zip(tokens[:-1], tokens[1:])]

        tagged_tokens = pos_tag(tokens)

        token_bigrams = [" ".join(bigram) for bigram in bigrams(tokens)]

        play_intent = any(word.lower() in intents.play_keywords for word, pos in tagged_tokens) or \
            any(bigram.lower() in intents.play_keywords for bigram in token_bigrams)

        # Check for stop intent
        stop_intent = any(word.lower() in intents.stop_keywords for word, pos in tagged_tokens) or \
            any(bigram.lower() in intents.stop_keywords for bigram in token_bigrams)

        if play_intent and any(pos == "VB" for word, pos in tagged_tokens):
            play_intent = False

        if stop_intent and any(pos == "VB" for word, pos in tagged_tokens):
            stop_intent = False

    except Exception as e:
        play_intent = False
        stop_intent = False

    print(f"Play Intent -> {play_intent}")
    print(f"Stop Intent -> {stop_intent}")

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
            # todo: random choice should be from directory
            random_song = random.choice(seq=[f for f in os.listdir(
                'audio_files') if os.path.isfile(os.path.join('audio_files', f))])
            update_conversation(random_song, f"Played song {random_song}")
            play_audio(random_song)
    elif stop_intent:
        await output_voice("Sure thing! Stopping")
        return
    else:
        data = {
            'input': recognized_text, 
            'child_id': IDENTIFIER, 
            'serial_number': serial_number,
        }

        print(data)

        # not gonna take conversation, to reduce token utilization
        
        if False and len(conversation) > 0:
            data['conversation'] = json.dumps(conversation[:MEMORY_CONTEXT])

        print(f"POST DATA {data}")

        response = r.post(API_URL, json=data, headers=headers)

        print(response.status_code)

        speech = response.json()['response']
        update_conversation(recognized_text, speech)

        # print(f"Response : {conversation}")
        display_controller.render_text_threaded_v2(speech)
        # await output_voice(speech)
        tts.text_to_speech(speech, "output.mp3")


def voice_filler():
    return random.choice(seq=['yes', 'yes tell me', 'sup', 'whats up', 'yo yo'])


@timing
async def interact():

    global CHAT_MODE
    global ASK_FOR_WAKE_WORD

    with sr.Microphone() as source:
        try:
            recognizer.adjust_for_ambient_noise(source, duration=1)
            recognizer.energy_threshold = 7000
            print("Energy threshold:", recognizer.energy_threshold)

            listen = True

            if listen:
                print("Listening for Wake Word")

                if ASK_FOR_WAKE_WORD:
                    wake_word_cue = random.choice(wake_word_cues)
                    # tts.text_to_speech(wake_word_cue, "wake_word_cue.mp3")
                    display_controller.render_text_threaded_v2(wake_word_cue)
                    tts.load_and_play(
                    f"{os.getcwd()}/assets/voice_cues/wake_word_cues/{wake_word_dict[wake_word_cue]}.mp3")
                    # tts.play(f"voice_cues/wake_word_cues/{wake_word_dict[wake_word_cue]}")
                
                ASK_FOR_WAKE_WORD = False
                audio = recognizer.listen(source)
                # audio_received_cue = random.choice(audio_received_cues)
                # tts.text_to_speech(audio_received_cue, "audio_received_cue.mp3")
                # display_controller.render_text_threaded_v2(audio_received_cue)
                # tts.load_and_play(
                #   f"{os.getcwd()}/assets/voice_cues/audio_received_cues/{audio_received_dict[audio_received_cue]}.mp3", use_thread=True)
                # play(f"voice_cues/audio_received_cues/{audio_received_dict[audio_received_cue]}")

                print("There was some audio input!")

                try:
                    recognized_text = recognizer.recognize_google(
                        audio).lower()
                    print(f"Recognized Text : {recognized_text}")

                    words = recognized_text.split()

                    wake_word_match = 0
                    lets_chat_match = 0

                    lets_chat_match = fuzz.partial_ratio(recognized_text, "let's chat")

                    # If "let's chat" isn't recognized, check for wake word in the first two words
                    if lets_chat_match <= 70 and len(words) >= 2:
                        first_two_words = " ".join(words[:2])
                        wake_word_match = fuzz.partial_ratio(first_two_words, WAKE_WORD)
                        
                        # If wake word is found and there are four or more words, 
                        # check words 3 and 4 for "let's chat"
                        if wake_word_match > 70 and len(words) >= 4:
                            next_two_words = " ".join(words[2:4])
                            lets_chat_match = fuzz.partial_ratio(next_two_words, "let's chat")

                    if wake_word_match > 70 or lets_chat_match > 70:
                        if lets_chat_match > 70:
                            chat_mode_cue = random.choice(chat_mode_activated_cues)
                            display_controller.render_text_threaded_v2(chat_mode_cue)
                            tts.load_and_play(f"{os.getcwd()}/assets/voice_cues/chat_mode_cues/{chat_mode_activated_dict[chat_mode_cue]}.mp3")
                            
                            while True:
                                print("Preparing for Audio I/O")

                                print("Listening for second command!")

                                audio = recognizer.listen(source, timeout=3)
                            
                                print("Resuming Conversation")
                                try:
                                
                                    recognized_text = recognizer.recognize_google(
                                    audio)

                                    print("Line 298")

                                    if fuzz.partial_ratio(recognized_text, "stop chat") > 70:
                                        print("We reached fuzz")
                                        ASK_FOR_WAKE_WORD = True
                                        break

                                    print(
                                    f"Recognized Instruction : {recognized_text}")
                                
                                    await process_input(recognized_text)
                                    gc.collect()
                                except Exception as e:
                                    gc.collect()
                                    print(f"Recognition Failed : {e}")
                                

                        else:
                            command = recognized_text.lower().replace(WAKE_WORD, "").strip()

                            await process_input(command)

                    else:
                        pass
                        print(f"Keep Sleeping")
                except Exception as e:
                    # display_controller.render_text_threaded_v2(
                    #     "Something happened?")
                    print(f"Some Error Occoured : {e}")
        except Exception as e:
            display_controller.render_text_threaded_v2("I heard some noise")
            print(f"Something Crashed {e}")


@timing
async def main():
    # while True:
    #     ic("I am running indeed")
    #     time.sleep(1)
    parser = argparse.ArgumentParser(
        description="Process input and optionally generate output audio.")
    parser.add_argument("-O", "--output", dest="output_text",
                        help="Output audio for the given input text")

    args = parser.parse_args()

    if args.output_text:
        print(f"Output {args.output_text}")
        await output_voice(args.output_text)
    else:
        # load data.yaml config file
        while True:
            await interact()


# def cleanup():
#     display_controller.render_text_threaded_v2("Not Running...")
#     print("Cleaning up before exiting...")


# def exit_handler():
#     cleanup()


# atexit.register(exit_handler)
# signal.signal(signal.SIGINT, exit_handler)
# signal.signal(signal.SIGNINT, exit_handler)

if __name__ == "__main__":
    asyncio.run(main())
