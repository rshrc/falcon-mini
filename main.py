import speech_recognition as sr
import requests as r
from gtts import gTTS
from io import BytesIO
import pygame
from tempfile import TemporaryFile
import json
import argparse
# /home/rishi/maii/main.py
from pydub import AudioSegment
from pydub.playback import play
from dotenv import load_dotenv
import os


load_dotenv()

API_URL = os.getenv('URL')


def output_audio(text):
    tts = gTTS(text, lang='en')

    fp = TemporaryFile()

    tts.write_to_fp(fp)
    fp.seek(0)
    song = AudioSegment.from_file(fp, format="mp3")
    play(song)
    # pygame.mixer.init()
    # pygame.mixer.music.load(fp)
    # pygame.mixer.music.play()
    # while pygame.mixer.music.get_busy():
    #     pygame.time.Clock().tick(10)

def test_connection():
    pass

mp3_fp = BytesIO()

audio_source = "/home/rishi/maii/twinkle.mp3"

# for memory
conversation = []

def play_mp3(file_path):
    pygame.init()
    pygame.mixer.init()

    try:
        pygame.mixer.music.load(file_path)
        pygame.mixer.music.play()
        
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)
    except Exception as e:
        print("Error:", e)
    finally:
        pygame.mixer.quit()


recognizer = sr.Recognizer()
def speech_to_text():
    
    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source)
        
        if True:
            print("Listening")
    
            audio = recognizer.listen(source)
            
            try: 
                recognized_text = recognizer.recognize_google(audio)
        
                print(f"Speech to text {recognized_text}")

                data = {
                    'input': recognized_text, 'age': 4, 
                }

                if len(conversation) > 0:
                    data['conversation'] = json.dumps(conversation)
                
                response = r.post(API_URL, json=data)
        
                print(response.status_code)

                speech = response.json()['response']

                conversation.append({'role': 'user', 'content': recognized_text})
                conversation.append({'role': 'assistant', 'content': speech})

                print(f"Line 75 : {conversation}")

                output_audio(speech)
            
            except Exception as e:
                print(f"Some Error Occoured : {e}")



def main():
    parser = argparse.ArgumentParser(description="Process input and optionally generate output audio.")
    parser.add_argument("-O", "--output", dest="output_text", help="Output audio for the given input text")
    
    args = parser.parse_args()
    
    if args.output_text:
        print(f"Line 112 {args.output_text}")
        output_audio(args.output_text)
    else:
        while True:
            speech_to_text()

if __name__ == "__main__":
    main()

# play_mp3(audio_source)
 