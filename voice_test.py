from google.cloud import texttospeech

import os

from pydub import AudioSegment, playback

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/Users/rishibanerjee/Downloads/core-cascade-401808-1ceff861a20a.json"


def text_to_speech(text, output_filename):
    # Initialize the client
    client = texttospeech.TextToSpeechClient()

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
    response = client.synthesize_speech(
        input=synthesis_input, voice=voice, audio_config=audio_config
    )

    # Write the response to the output file.
    with open(output_filename, "wb") as out:
        out.write(response.audio_content)
    
    print("Audio Stored")

    audio = AudioSegment.from_mp3("output.mp3")

    print("Loaded Audio")
    playback.play(audio)
    


text = "Ba Ba Black Sheep have you any wool, yes sir yes sir, 3 bags full"
output_filename = "output.mp3"
text_to_speech(text, output_filename)
