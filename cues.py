wake_word_cues = [
    "Say 'Hey Panda' to start chatting!",
    "Waiting for you to say 'Hey Panda'!",
    "I'm all ears! Just say 'Hey Panda'.",
    "Ready when you say 'Hey Panda'!",
    "Want to chat? Call me with 'Hey Panda'!",
    "Listening for my cue: 'Hey Panda'!",
    "Eager to chat! Just say 'Hey Panda'.",
    "I'm on standby. Waiting for 'Hey Panda'!",
    "Ready for our next adventure! Call out 'Hey Panda'.",
    "Your robot pal is listening for 'Hey Panda'!",
    "I'm here and waiting. Just say 'Hey Panda'!",
    "Ready to converse when you say 'Hey Panda'!",
    "I perk up at 'Hey Panda'! Give it a try.",
    "Want my attention? 'Hey Panda' is the magic phrase.",
    "I'm tuned in for 'Hey Panda'. Let's chat!",
    "Ears activated for 'Hey Panda'!",
    "Ready for action! Waiting for 'Hey Panda'.",
    "Let's chat! Say 'Hey Panda' to begin.",
    "I'm here for you. Just call 'Hey Panda'.",
    "Listening mode on! Awaiting 'Hey Panda'."
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