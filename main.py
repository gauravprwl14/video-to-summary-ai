import argparse
import os
import subprocess
from datetime import datetime

import speech_recognition as sr
import whisper
import youtube_dl
from openai import OpenAI

model = whisper.load_model("base")
result = model.transcribe("audio.mp3")
print(result["text"])


def download_audio(url, output_dir="./downloads", filename="downloaded_audio"):
    # Ensure the output directory exists
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Get current date and time for the filename
    current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename_with_timestamp = f"{filename}_{current_time}"

    ydl_opts = {
        "format": "bestaudio/best",
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }
        ],
        "outtmpl": os.path.join(output_dir, f"{filename_with_timestamp}.%(ext)s"),
    }

    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])


def transcribe_audio(file_path):
    # Load the Whisper model
    model = whisper.load_model("base")

    # Transcribe the audio
    result = model.transcribe(file_path)

    # Return the transcription
    return result["text"]


def download_and_transcribe(url):
    audio_file = download_audio(url)
    transcription = transcribe_audio(audio_file)
    return transcription


def extract_audio(input_video, output_audio):
    # Check if the input video file exists
    if not os.path.isfile(input_video):
        print(f"Error: The input video file '{input_video}' does not exist.")
        return

    # Run ffmpeg to extract audio
    try:
        subprocess.run(
            [
                "ffmpeg",
                "-i",
                input_video,
                "-vn",
                "-acodec",
                "pcm_s16le",
                "-ar",
                "44100",
                output_audio,
            ],
            check=True,
        )
        print(f"Audio extracted and saved to '{output_audio}'")
        return output_audio
    except subprocess.CalledProcessError as e:
        print(f"Error during ffmpeg execution: {e}")
        return


def get_summary(text):
    client = OpenAI(api_key="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")
    try:
        response = client.chat.completions.create(
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": f"Summarise this text in 50 words: {text}"},
            ],
            model="gpt-3.5-turbo",
        )
        return response.choices[0].message.content
    except Exception as e:
        print("Error while getting summary: ", e)
        return


def extract_text_from_audio(input_audio):
    r = sr.Recognizer()
    try:
        with sr.AudioFile(input_audio) as source:
            audio = r.record(source)

        output_text = r.recognize_google(audio)
        print("Successfully extracted the text from audio.\n")
        print(output_text)
        return output_text
    except Exception as e:
        print("Error in extracting text from audio: ", e)


def get_video_summary(video_file):
    output_audio_file = "output_audio.wav"
    print(f"Processing video file: {video_file}")
    input_video_file = video_file

    extract_audio(input_video_file, output_audio_file)

    # Audio to text generation
    output_text = extract_text_from_audio(output_audio_file)
    print("ORIGINAL VIDEO TEXT: ", output_text)

    # OpenAI Chat for summary
    if output_text:
        summaryText = get_summary(output_text)
        print("SUMMARY: ", summaryText)


def main():
    parser = argparse.ArgumentParser(description="Process a video file.")
    parser.add_argument("--filename", type=str, help="Path to the video file")
    args = parser.parse_args()

    if args.filename:
        # get_video_summary(args.filename)
        output_audio_file = "./output_audio.wav"
        audio_to_text = extract_text_from_audio(output_audio_file)
        print("result")
        print(audio_to_text)
    else:
        print("Error: Please provide a filename using the --filename option.")


if __name__ == "__main__":
    main()
