from gtts import gTTS
tts = gTTS('こんにちわ','co.jp','ja',False)
tts.save('hello.wav')