from google.cloud import texttospeech as tts

from dotenv import find_dotenv, load_dotenv


load_dotenv(find_dotenv())

TEXT = """
Data is at the center of many challenges in system design today. Difficult
  issues need to be figured out, such as scalability, consistency, reliability, efficiency,
  and maintainability. In addition, we have an overwhelming variety of tools, including
  relational databases, NoSQL datastores, stream or batch processors, and message
  brokers. What are the right choices for your application? How do you make sense
  of all these buzzwords?


  In this practical and comprehensive guide, author Martin Kleppmann helps you navigate
  this diverse landscape by examining the pros and cons of various technologies for
  processing and storing data. Software keeps changing, but the fundamental principles
  remain the same. With this book, software engineers and architects will learn how
  to apply those ideas in practice, and how to make full use of data in modern applications.


  * Peer under the hood of the systems you already use, and learn how to use and operate
  them more effectively

  * Make informed decisions by identifying the strengths and weaknesses of different
  tools

  * Navigate the trade-offs around consistency, scalability, fault tolerance, and
  complexity

  * Understand the distributed systems research upon which modern databases are built

  * Peek behind the scenes of major online services, and learn from their architectures
"""

SSML_TEXT = """
<speak>
  <prosody rate="fast">Data is at the center of many challenges in system design today.</prosody>
  <emphasis level="strong">Difficult issues need to be figured out, such as scalability, consistency, reliability, efficiency, and maintainability.</emphasis>
  In addition, we have an overwhelming variety of tools, including relational databases, NoSQL datastores, 
  <prosody pitch="high" rate="fast">stream or batch processors, and message brokers.</prosody> 

  <emphasis level="moderate">What are the right choices for your application?</emphasis> 
  How do you make sense of all these buzzwords?

  <break time="500ms"/> 

  In this practical and comprehensive guide, 
  <prosody volume="loud">author Martin Kleppmann helps you navigate this diverse landscape</prosody> 
  by examining the pros and cons of various technologies for processing and storing data. 
  Software keeps changing, but the fundamental principles remain the same. 

  With this book, software engineers and architects will learn how to apply those ideas in practice, 
  and how to make full use of data in modern applications.

  <break time="500ms"/> 

  <emphasis level="strong">
  * Peer under the hood of the systems you already use, and learn how to use and operate them more effectively
  </emphasis>

  <emphasis level="reduced"> 
  * Make informed decisions by identifying the strengths and weaknesses of different tools
  </emphasis>

  <emphasis level="strong">
  * Navigate the trade-offs around consistency, scalability, fault tolerance, and complexity
  </emphasis>

  * Understand the distributed systems research upon which modern databases are built

  <prosody volume="loud">
  * Peek behind the scenes of major online services, and learn from their architectures
  </prosody>
</speak>
  """


def list_voices(language_code=None):
    client = tts.TextToSpeechClient()
    response = client.list_voices(language_code=language_code)
    voices = sorted(response.voices, key=lambda voice: voice.name)

    print(f" Voices: {len(voices)} ".center(60, "-"))
    for voice in voices:
        languages = ", ".join(voice.language_codes)
        name = voice.name
        gender = tts.SsmlVoiceGender(voice.ssml_gender).name
        rate = voice.natural_sample_rate_hertz
        print(f"{languages:<8} | {name:<24} | {gender:<8} | {rate:,} Hz")


def text_to_mp3(voice_name: str, filename: str, text: str):
    language_code = "-".join(voice_name.split("-")[:2])
    text_input = tts.SynthesisInput(text=text)
    voice_params = tts.VoiceSelectionParams(
        language_code=language_code, name=voice_name
    )
    audio_config = tts.AudioConfig(audio_encoding=tts.AudioEncoding.MP3)

    client = tts.TextToSpeechClient()
    response = client.synthesize_speech(
        input=text_input,
        voice=voice_params,
        audio_config=audio_config,
    )

    with open(filename, "wb") as out:
        out.write(response.audio_content)
        print(f'Generated speech saved to "{filename}"')


if __name__ == "__main__":
    text_to_mp3("en-GB-Wavenet-B", "normal.mp3", TEXT)
    text_to_mp3("en-GB-Wavenet-B", "excited.mp3", SSML_TEXT)
