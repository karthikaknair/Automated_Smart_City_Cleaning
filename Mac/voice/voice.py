from gtts import gTTS

text = "Garbage appears in area 1 , 1"
tts = gTTS(text)
tts.save("appear.mp3")
