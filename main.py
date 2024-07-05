from google.cloud import texttospeech as tts
import os

from dotenv import find_dotenv, load_dotenv
from pydub import AudioSegment

import yaml
import random

load_dotenv(find_dotenv())

source_file = "/Users/odewahn/Desktop/content/summaries/0636920934394-generative-ai-for-developers-creating-a/00010-lesson-2-5-prompt-engineering.md.00010.audio-narration.txt"
voice = "en-US-Studio-O"


# ***********************************************************************
# Misc functions
# ***********************************************************************
def read_file(file_path):
    with open(os.path.expanduser(file_path), "r") as file:
        return file.read()


# Split the text into smaller chunks by paragraphs
# No chunck should exceed 5000 characters
def split_text(text: str, max_chars: int = 2000):
    chunks = []
    chunk = ""
    for paragraph in text.split("\n"):
        if len(chunk) + len(paragraph) < max_chars:
            chunk += paragraph + "\n"
        else:
            chunks.append(chunk)
            chunk = paragraph + "\n"
    chunks.append(chunk)
    return chunks


# ***********************************************************************
# Functions related to text to speech
# ***********************************************************************


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


# ***********************************************************************
# Functions related to making the intro
# ***********************************************************************


def make_intro(text, out_fn, voice=voice):
    text_to_mp3(voice, out_fn, text)


def overlay_intro_with_music(voice_narration_fn, intro_music_fn, out_fn):
    voice_narration = AudioSegment.from_mp3(os.path.expanduser(voice_narration_fn))
    music = AudioSegment.from_mp3(os.path.expanduser(intro_music_fn))
    print(f"Voice narration: {len(voice_narration):,} ms")
    print(f"Music: {len(music):,} ms")
    offset_start_ms = 1000
    offset_end_ms = 2000
    narration_len_ms = len(voice_narration)
    music_len_ms = len(music)
    # overlay the voice narration on the music
    audio = (
        music[: offset_start_ms + narration_len_ms + offset_end_ms]
        .fade_out(offset_end_ms)
        .overlay(voice_narration, position=offset_start_ms, gain_during_overlay=-6)
    )
    audio.export(out_fn, format="mp3")


def text_to_audio(text, intro_filename, out_fn):
    print(f"Text length: {len(text):,} characters")
    chunks = split_text(text)
    file_names = [intro_filename]
    for i, chunk in enumerate(chunks):
        fn = f"segment-{i:02d}.mp3"
        file_names.append(fn)
        text_to_mp3(voice, fn, chunk)
    # use pydub to merge the mp3 files
    audio = AudioSegment.empty()
    for fn in file_names:
        audio += AudioSegment.from_mp3(fn)
    audio.export(out_fn, format="mp3")


if __name__ == "__main__":
    intro_text = """
    Welcome to the AI generated interview from Generative AI for Developers by Tom Taulli.
    """
    make_intro(intro_text, "intro.mp3", "en-GB-Studio-B")
    overlay_intro_with_music(
        "intro.mp3",
        "~/Desktop/content/intro-opengameart-crystal-cave.mp3",
        "intro-final.mp3",
    )

    # content_text = read_file(source_file)
    # text_to_audio(content_text, "intro-final.mp3", "content.mp3")
    # assemble_audio("intro.mp3", "~/Desktop/content/intro-opengameart-crystal-cave.mp3")
    # Read in the yaml from a file
    with open("interview/script.yaml", "r") as txt:
        script = yaml.safe_load(txt)
    audio = AudioSegment.empty()
    audio += AudioSegment.from_mp3("intro-final.mp3")
    for voice in script:
        # Read the text from the file
        text = read_file("interview/" + voice["file"])
        output_fn = voice["file"].split(".")[0] + ".mp3"
        # text_to_mp3(voice["voice"], output_fn, text)
        # Add a bit of random silce, anywhere from 250 to 500 ms
        rnd = 250 + 250 * random.random()
        audio += AudioSegment.silent(duration=rnd)
        audio += AudioSegment.from_mp3(output_fn)
    audio.export("interview.mp3", format="mp3")
