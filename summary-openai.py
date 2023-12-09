import os

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
# open_ai_api_key = os.getenv("OPENAI_API_KEY")


def chunk_text(text, chunk_size):
    """Divide the text into chunks of approximately `chunk_size` characters."""
    for start in range(0, len(text), chunk_size):
        yield text[start : start + chunk_size]


def summarize_chunk(chunk, open_ai_api_key):
    """Summarize a single chunk of text."""
    # openai.api_key = open_ai_api_key
    print("chunk")
    print(chunk)
    print("&&&&&&&&&&&&&&&&&&&&&&&&&&&& END ***************")
    client = OpenAI(api_key=open_ai_api_key)
    try:
        response = client.chat.completions.create(
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": f"Summarize this text: {chunk}"},
            ],
            model="gpt-3.5-turbo",
            # api_key=open_ai_api_key,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print("Error while getting summary: ", e)
        return ""


def get_overall_summary(summaries, open_ai_api_key):
    """Summarize the combined summaries for an overall summary."""
    combined_summaries = " ".join(summaries)
    return summarize_chunk(combined_summaries, open_ai_api_key)


def get_summary(file_path, open_ai_api_key):
    # Read the content of the file
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            text = file.read()
    except Exception as e:
        print("Error reading file: ", e)
        return

    # Estimate the token count (assuming 1 token ≈ 4 characters, this is a rough estimate)
    max_tokens_per_request = 4000  # Adjust based on the actual limit
    chunk_size = (
        max_tokens_per_request * 4
    )  # Adjust chunk size based on character count

    # Chunk the text and summarize each chunk
    chunks = chunk_text(text, chunk_size)
    individual_summaries = [summarize_chunk(chunk, open_ai_api_key) for chunk in chunks]

    # Get an overall summary of the individual summaries
    overall_summary = get_overall_summary(individual_summaries, open_ai_api_key)
    print("Output Summary")
    print(overall_summary)
    return overall_summary


# Example usage

open_ai_api_key = os.getenv("OPENAI_API_KEY")
print("open_ai_api_key", open_ai_api_key)
file_path = (
    "./videoFiles//outputDir/downloaded_audio_20231203_085751_20231203_105701.txt"
)

summary = get_summary(file_path, open_ai_api_key)
print(summary)
