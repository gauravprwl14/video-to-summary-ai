import argparse
import os
import subprocess
from datetime import datetime

import speech_recognition as sr
import whisper
import youtube_dl
from dotenv import load_dotenv
from openai import OpenAI
from tqdm import tqdm

# model = whisper.load_model("base")
# result = model.transcribe("audio.mp3")
# print(result["text"])

# Load environment variables from .env file
load_dotenv()
open_ai_api_key = os.getenv("OPENAI_API_KEY")


def download_audio(url, output_dir="./videoFiles/youtube", filename="downloaded_audio"):
    # Ensure the output directory exists
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Get current date and time for the filename
    current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename_with_timestamp = f"{filename}_{current_time}"

    def my_hook(d):
        if d["status"] == "downloading":
            print("\rDownloading... {}%".format(d["_percent_str"]), end="")
        if d["status"] == "finished":
            print("\nDone downloading, now converting ...")

    # First, retrieve the video title
    with youtube_dl.YoutubeDL({"quiet": True}) as ydl:
        info_dict = ydl.extract_info(url, download=False)
        video_title = info_dict.get("title", None)

    # Sanitize the video title to create a valid filename
    sanitized_title = "".join(
        [c for c in video_title if c.isalnum() or c in [" ", "-", "_"]]
    ).rstrip()
    final_filename = f"{sanitized_title}_{current_time}"

    ydl_opts = {
        "format": "bestaudio/best",
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "wav",
                "preferredquality": "192",
            }
        ],
        # "outtmpl": os.path.join(output_dir, f"{filename_with_timestamp}.%(ext)s"),
        "outtmpl": os.path.join(output_dir, f"{final_filename}.%(ext)s"),
        "progress_hooks": [my_hook],
        "verbose": True,
    }

    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

    return os.path.join(output_dir, f"{filename_with_timestamp}.wav")


def transcribe_audio(file_path):
    # Load the Whisper model
    model = whisper.load_model("medium")

    # Transcribe the audio
    result = model.transcribe(file_path)

    # Return the transcription
    return result["text"]


def save_transcription(transcription, audio_file_path, output_dir):
    base_name = os.path.splitext(os.path.basename(audio_file_path))[0]
    current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file_name = f"{base_name}_{current_time}.txt"
    output_file_path = os.path.join(output_dir, output_file_name)

    with open(output_file_path, "w", encoding="utf-8") as file:
        file.write(transcription)

    return output_file_path


def download_and_transcribe(url, output_dir="./videoFiles/outputDir/"):
    audio_file = download_audio(url)
    # audio_file = "./videoFiles/youtube/downloaded_audio_20231203_085751.wav"
    print("audio_file_path")
    print(audio_file)
    transcription = transcribe_audio(audio_file)
    output_file = save_transcription(transcription, audio_file, output_dir)
    print("Transcription Saved Location: ")
    print(output_file)
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
    client = OpenAI(open_ai_api_key)
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
    parser.add_argument("--url", type=str, help="Youtube video URL")
    args = parser.parse_args()

    if args.filename:
        # get_video_summary(args.filename)
        # output_audio_file = "./output_audio.wav"
        # audio_to_text = extract_text_from_audio(output_audio_file)

        output_dir = "./videoFiles/outputDir/"
        transcription = transcribe_audio(args.filename)
        output_file = save_transcription(transcription, args.filename, output_dir)
        print("result")
        print(output_file)
    elif args.url:
        print(args.url)
        download_and_transcribe(args.url)
    else:
        print("Error: Please provide a filename using the --filename option.")


if __name__ == "__main__":
    main()
