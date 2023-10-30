from voice import TextToSpeechPlayer, output_voice, play_audio
from utils import get_last_n, store_data
from serial_number import get_serial_number
from measure import timing
from disply_lib import DisplayController
from cues import (audio_received_cues, audio_received_dict,
                  awaiting_response_cues, awaiting_response_dict,
                  chat_mode_activated_cues, chat_mode_activated_dict,
                  stop_chat_cues, stop_chat_dict, wake_word_cues,
                  wake_word_dict, audio_error_cues, audio_error_dict)
from config import DeviceConfig, get_configuration
import intents
from nltk.tokenize import word_tokenize
from nltk.tag import pos_tag
from fuzzywuzzy import fuzz
from dotenv import load_dotenv
import speech_recognition as sr
import requests as r
from logging.handlers import RotatingFileHandler
from datetime import datetime
import traceback
import subprocess
import signal
import random
import logging
import gc
import argparse
import asyncio
import atexit
import json
import multiprocessing
import os
import sys
import time
import speech_recognition

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = f"{os.getcwd()}/gconfig.json"


# from db.utils import get_data_in_date_range, get_last_n, store_data

# Create a logger
logger = logging.getLogger()

# Set the log level
logger.setLevel(logging.INFO)

# Define the log format
formatter = logging.Formatter(
    '%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

# Create the RotatingFileHandler
handler = RotatingFileHandler(
    'falcon_mini.log', maxBytes=5*1024*1024, backupCount=3)

# Set the formatter for the handler
handler.setFormatter(formatter)

# Clear any existing handlers (to avoid duplicate logs)
for h in logger.handlers[:]:
    logger.removeHandler(h)

# Add the rotating handler to the logger
logger.addHandler(handler)


def increase_volume():
    subprocess.call(
        ['sudo', '/home/rishi/falcon_mini/scripts/setup/set_volume.sh'])


increase_volume()

BPRAP = "voice_cues"


os.environ['ALSA_WARNINGS'] = '0'



headers = {
    'X-Device-Serial': get_serial_number()
}


load_dotenv()

API_URL = os.getenv('URL')
BASE_URL = os.getenv('BASE_URL')
WAKE_WORD = os.getenv('WAKE_WORD').lower()

test_device_uuid = "46135e88-2645-44ce-bd1f-cbc9bb9e6557"

CHAT_MODE = False
ASK_FOR_WAKE_WORD = True

configuration = get_configuration(BASE_URL, get_serial_number())


IDENTIFIER = configuration.user_info.identifier

tts = TextToSpeechPlayer(configuration.voice.url)

MEMORY_CONTEXT = 0

PHRASE_TIME_LIMIT = 5

if isinstance(configuration, str):
    print(configuration)
elif isinstance(configuration, DeviceConfig):
    print(configuration.to_dict)

    MEMORY_CONTEXT = configuration.memory.context_limit

    logger.info(f"Memory Context {MEMORY_CONTEXT}")
else:
    logger.info("Unexpected type of configuration data.")

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
    store_data(input, output)


@timing
async def process_input(recognized_text):
    awaiting_response_cue = random.choice(awaiting_response_cues)
    display_controller.render_text_threaded_v2(awaiting_response_cue)
    tts.load_and_play(
        f"{os.getcwd()}/assets/voice_cues/awaiting_response_cues/{awaiting_response_dict[awaiting_response_cue]}.mp3", use_thread=True)

    try:
        tokens = word_tokenize(recognized_text)

        bigrams = [" ".join(bigram) for bigram in zip(tokens[:-1], tokens[1:])]

        tagged_tokens = pos_tag(tokens)

        token_bigrams = [" ".join(bigram) for bigram in bigrams]

        play_intent = any(word.lower() in intents.play_keywords for word, pos in tagged_tokens) or \
            any(bigram.lower() in intents.play_keywords for bigram in token_bigrams)

        # Check for stop intent
        stop_intent = any(word.lower() in intents.stop_keywords for word, pos in tagged_tokens) or \
            any(bigram.lower() in intents.stop_keywords for bigram in token_bigrams)

        if play_intent and any(pos == "VB" for word, pos in tagged_tokens):
            play_intent = False

        if stop_intent and any(pos == "VB" for word, pos in tagged_tokens):
            stop_intent = False
        x = "what did we talk about today"
        logger.info(
            f"Asked For Summarization : {fuzz.partial_ratio(recognized_text, x)}")
        summarize_intent = fuzz.partial_ratio(recognized_text, "what did we talk about today") > 70 or fuzz.partial_ratio(
            recognized_text, "summarize our conversation today") > 70

    except Exception as e:
        play_intent = False
        stop_intent = False
        summarize_intent = False
        logger.warning(f"Failed Parsing NLP with {e}")

    logger.info(f"Play Intent -> {play_intent}")
    logger.info(f"Stop Intent -> {stop_intent}")
    logger.info(f"Summarize Intent -> {summarize_intent}")

    if play_intent:
        similar_song_found, song_path = check_similar_song(
            recognized_text, 'audio_files/')
        logger.info(
            f"Similar Song = {similar_song_found} and Path {song_path}")

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
    elif summarize_intent:
        logger.info(f"Summarize Intent Triggered via {recognized_text}")

        data = {
            'input': recognized_text,
            'child_id': IDENTIFIER,
        }

        conversation = get_last_n(MEMORY_CONTEXT)

        if len(conversation) > 0:
            data['conversation'] = json.dumps(conversation)

        try:
            response = r.post(API_URL, json=data, headers=headers)

            logger.info(f"AI TALK API RESPONSE {response.status_code}")

            speech = response.json()['response']
            update_conversation(recognized_text, speech)

            display_controller.render_text_threaded_v2(speech)
            tts.play(speech, headers)
        except Exception as e:
            logger.warning(f"API Call Fail with {data} & {e}")
    else:
        data = {
            'input': recognized_text,
            'child_id': IDENTIFIER,
        }

        try:

            response = r.post(API_URL, json=data, headers=headers)

            logger.info(f"AI TALK API RESPONSE {response.status_code}")

            speech = response.json()['response']
            update_conversation(recognized_text, speech)

            display_controller.render_text_threaded_v2(speech)
            tts.play(speech, headers)
        except Exception as e:
            logger.warning(f"API Call Fail with {data} & {e}")


def voice_filler():
    return random.choice(seq=['yes', 'yes tell me', 'sup', 'whats up', 'yo yo'])


@timing
async def interact():
    logger.info("Interact Mode Accessed")

    global CHAT_MODE
    global ASK_FOR_WAKE_WORD

    with sr.Microphone() as source:
        logger.info("Microphone On")
        try:
            recognizer.adjust_for_ambient_noise(source, duration=1)
            logger.info("Ambience Adjusted")
            recognizer.energy_threshold = 7000
            logger.info(
                f"Energy Threshold Set to {recognizer.energy_threshold}")
           
            

            listen = True
            if listen:
                logger.info("Listening for Wake Word")

                if ASK_FOR_WAKE_WORD:
                    wake_word_cue = random.choice(wake_word_cues)
                    display_controller.render_text_threaded_v2(wake_word_cue)
                    tts.load_and_play(
                        f"{os.getcwd()}/assets/voice_cues/wake_word_cues/{wake_word_dict[wake_word_cue]}.mp3")
                logger.info("User Informed About State")

                ASK_FOR_WAKE_WORD = False
                start_time = time.time()
                logger.info("Started Listening")
                audio = recognizer.listen(source)

                logger.info(
                    f"There was some audio input! Time Delta {time.time()-start_time:.2f}")

                try:
                    recognized_text = recognizer.recognize_google(
                        audio).lower()
                    logger.info(f"Recognized Text : {recognized_text}")


                    words = recognized_text.split()

                    wake_word_match = 0
                    lets_chat_match = 0

                    lets_chat_match = fuzz.partial_ratio(
                        recognized_text, "let's chat")

                    logger.info(
                        f"Match {recognized_text} and Lets Chat - {lets_chat_match}")

                    if lets_chat_match <= 70 and len(words) >= 2:
                        logger.info(
                            f"Lets Chat Not Matched: Words Length {len(words)}")
                        first_two_words = " ".join(words[:2])
                        wake_word_match = fuzz.partial_ratio(
                            first_two_words, WAKE_WORD)

                        if wake_word_match > 70 and len(words) >= 4:
                            next_two_words = " ".join(words[2:4])
                            lets_chat_match = fuzz.partial_ratio(
                                next_two_words, "let's chat")

                    if wake_word_match > 70 or lets_chat_match > 70:
                        logger.info(
                            f"Wake Word Match {wake_word_match} and Lets Chat Match {lets_chat_match}")
                        if lets_chat_match > 70:
                            chat_mode_cue = random.choice(
                                chat_mode_activated_cues)
                            display_controller.render_text_threaded_v2(
                                chat_mode_cue)
                            tts.load_and_play(
                                f"{os.getcwd()}/assets/voice_cues/chat_mode_cues/{chat_mode_activated_dict[chat_mode_cue]}.mp3")

                            while True:

                                logger.info("Listening for second command!")
                                start_time = time.time()
                                audio = recognizer.listen(
                                    source, timeout=3, phrase_time_limit=PHRASE_TIME_LIMIT)

                                logger.info(
                                    f"Resuming Conversation - {time.time() - start_time:2f}")
                                try:

                                    recognized_text = recognizer.recognize_google(
                                        audio)
                                    
                                    logger.info(
                                        f"Recognized Text : {recognized_text}")

                                    if fuzz.partial_ratio(recognized_text, "stop chat") > 70:
                                        logger.info(
                                            "Stop Chat Command Received")
                                        stop_chat_cue = random.choice(
                                            stop_chat_cues)
                                        display_controller.render_text_threaded_v2(
                                            stop_chat_cue)
                                        tts.load_and_play(
                                            f"{os.getcwd()}/assets/voice_cues/stop_chat_cues/{stop_chat_dict[stop_chat_cue]}.mp3")
                                        ASK_FOR_WAKE_WORD = True
                                        break

                                    await process_input(recognized_text)
                                    gc.collect()
                                except speech_recognition.UnknownValueError:
                                    logger.warning("Google Web Speech API could not understand audio (ResumeConv)")
                                    audio_error_cue = random.choice(audio_error_cues)
                                    display_controller.render_text_threaded_v2(
                                            audio_error_cue)
                                    tts.load_and_play(
                                                f"{os.getcwd()}/assets/voice_cues/audio_error_cues/{audio_error_dict[audio_error_cue]}.mp3")

                                except speech_recognition.RequestError as e:
                                    logger.warning(f"Could not request results from Google Web Speech API (ResumeConv): {e}")
                                except Exception as e:
                                    gc.collect()
                                    logger.warning(f"Recognition Failed : {e}")

                        else:
                            command = recognized_text.lower().replace(WAKE_WORD, "").strip()

                            await process_input(command)

                    else:
                        pass
                        logger.warning(f"False Trigger! Keep Sleeping!")
                # except speech_recognition.UnknownValueError:
                #     logger.warning("Google Web Speech API could not understand audio")
                #     audio_error_cue = random.choice(audio_error_cues)
                #     display_controller.render_text_threaded_v2(
                #             audio_error_cue)
                #     tts.load_and_play(
                #                 f"{os.getcwd()}/assets/voice_cues/audio_error_cues/{audio_error_dict[audio_error_cue]}.mp3")

                # except speech_recognition.RequestError as e:
                #     logger.warning(f"Could not request results from Google Web Speech API: {e}")
                except Exception as e:

                    logger.warning(
                        f"Some Error Occoured : {e}\n{traceback.format_exc()}")
                    logger.warning(f"Some Error Occoured 2 : {str(e)}")

        except Exception as e:
            display_controller.render_text_threaded_v2("I heard some noise")
            logger.warning(f"False Wake Up! Keep Sleeping! {e}")


@timing
async def main():
    logger.info(
        f"Falcon Mini Booted at {datetime.now().strftime('%A, %B %d, %Y, %H:%M:%S')}")
    parser = argparse.ArgumentParser(
        description="Process input and optionally generate output audio.")
    parser.add_argument("-O", "--output", dest="output_text",
                        help="Output audio for the given input text")

    args = parser.parse_args()

    if args.output_text:
        print(f"Output {args.output_text}")
        await output_voice(args.output_text)
    else:
        while True:
            await interact()

if __name__ == "__main__":
    asyncio.run(main())
