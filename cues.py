wake_word_cues = [
    "Ready when you are!",
    "Your little friend's waiting!",
    "I'm all ears!",
    "I'm online and ready to roll!",
    "Guess who's awake? It's me!",
    "I'm up and active!",
    "Powered on and pumped!",
    "Just booted up and raring to go!",
    "Tuned in and ready!",
    "Ears on standby!",
    "I'm alive and kicking!",
    "Ready for some fun!",
    "Eyes open, circuits buzzing!",
    "Ready to go!",
    "Back in action and feeling good!",
    "I'm here and alert!",
    "All set and waiting!",
    "Let's have some fun!",
    "I'm on and ready!",
    "Eager and waiting!"
]

wake_word_dict = {cue: idx for idx, cue in enumerate(wake_word_cues, 1)}


audio_received_cues = [
    "Okey-dokey...",
    "Heard that!",
    "Gotcha!",
    "Hmm, let's see...",
]

audio_received_dict = {cue: idx for idx, cue in enumerate(audio_received_cues, 1)}


awaiting_response_cues = [
    "Ummm...",
    "Hmm...",
    "Er...",
    "Ah...",
    "Oh...",
    "Mmm...",
    "Huh...",
    "Eh...",
    "Well...",
    "Aha...",
    "Let's see...",
    "Hang on...",
    "Wait...",
    "Thinking...",
    "Pondering...",
    "Uh-huh...",
    "Erm..."
]

awaiting_response_dict = {cue: idx for idx, cue in enumerate(awaiting_response_cues, 1)}



chat_mode_activated_cues = [
    "Sure thing! Let's chat away.",
    "Chat mode is on! What's on your mind?",
    "Alright! I'm all ears. Let's chat.",
    "Yay! I love our chat sessions. Go ahead.",
    "Chat time! Tell me everything.",
    "Okay! I'm ready for our chat adventure.",
    "Sounds fun! Let's dive into our chat.",
    "You got it! Let's chat up a storm.",
    "Awesome choice! I'm excited to chat with you.",
    "You said the magic words! Let's chat.",
    "You've got my full attention. Let's chat!"
]

chat_mode_activated_dict = {cue: idx for idx, cue in enumerate(chat_mode_activated_cues, 1)}

stop_chat_cues = [
    "Chat's on break!",
    "Taking a pause!",
    "Chat nap time!",
    "See you soon!",
    "Chat time-out!",
    "Break time, buddy!",
    "Chat's resting!",
    "Later, friend!",
    "Tiny chat break!",
    "Be back soon!"
]

stop_chat_dict = {cue: idx for idx, cue in enumerate(stop_chat_cues, 1)}