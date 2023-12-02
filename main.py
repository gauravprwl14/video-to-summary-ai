import argparse
import subprocess
import os
import speech_recognition as sr
from openai import OpenAI
​
​
def extract_audio(input_video, output_audio):
    # Check if the input video file exists
    if not os.path.isfile(input_video):
        print(f"Error: The input video file '{input_video}' does not exist.")
        return
​
    # Run ffmpeg to extract audio
    try:
        subprocess.run(['ffmpeg', '-i', input_video, '-vn', '-acodec', 'pcm_s16le', '-ar', '44100', output_audio],
                       check=True)
        print(f"Audio extracted and saved to '{output_audio}'")
        return output_audio
    except subprocess.CalledProcessError as e:
        print(f"Error during ffmpeg execution: {e}")
        return
​
​
def get_summary(text):
    client = OpenAI(
        api_key="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",
    )
    try:
        response = client.chat.completions.create(
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": f"Summarise this text in 50 words {text} "}
            ],
            model="gpt-3.5-turbo",
        )
        return response.choices[0].message.content
    except Exception as e:
        print("Error while getting summary ", e)
        return
​
​
def extract_text_from_audio(input_audio):
    r = sr.Recognizer()
    try:
        next14tut = sr.AudioFile(input_audio)
        with next14tut as source:
            audio = r.record(source)
​
        output_text = r.recognize_google(audio)
        print("successfully extracted the text from audio \n")
        return output_text
    except Exception as e:
        print("Error in extracting text from audio ", e)
​
​
def get_video_summary(video_file):
    output_audio_file = "output_audio.wav"
    print(f'Processing video file: {video_file}')
    input_video_file = video_file
​
    extract_audio(input_video_file, output_audio_file)
​
    ## THIS SECTION IS FOR THE AUDIO TO TEXT GENERATION
​
    output_text = extract_text_from_audio(output_audio_file)
    print("ORIGINAL VIDEO TEXT : ",output_text)
​
    ## THIS SECTION IS FOR THE OPENAI CHAT
​
    if output_text:
        summaryText = get_summary(output_text)
        print("SUMMARY : ",summaryText)
​
​
def main():
    parser = argparse.ArgumentParser(description='Process a video file.')
    parser.add_argument('--filename', type=str, help='Path to the video file')
    args = parser.parse_args()
    if args.filename:
        get_video_summary(args.filename)
    else:
        print('Error: Please provide a filename using the --filename option.')
​
​
if __name__ == '__main__':
    main()
    # print(sr.__version__)
