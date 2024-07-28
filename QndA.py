import json
from youtube_transcript_api import YouTubeTranscriptApi
import google.generativeai as genai
from dotenv import load_dotenv
import os
from exa_py import Exa

# Load environment variables
load_dotenv()

# Initialize APIs
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
exa = Exa(api_key=os.getenv("EXA_API_KEY"))

def retrieve_transcript(yt_url):
    try:
        yt_id = yt_url.split("=")[1].split("&")[0]
        transcript = YouTubeTranscriptApi.get_transcript(yt_id)
        return transcript
    except Exception as e:
        return None

def generate_answer(question, transcript, url):
    if not transcript:
        return "Couldn't fetch transcript. Please provide a valid YouTube URL."

    formatted_transcript = {
        'parts': [{'text': part['text']} for part in transcript]
    }

    system_instruction = f'''
    You are an expert in answering questions based on YouTube video transcriptions. 
    Your task is to provide precise and relevant answers to the questions based on the provided transcription.
    Ensure that the answers are based on the content of the video and are well-supported by the transcript.
    If the transcription is not available or if the question is beyond the scope of the transcript, respond appropriately.
    '''

    genai_model = genai.GenerativeModel("gemini-pro")
    transcript_str = json.dumps(formatted_transcript)
    response = genai_model.generate_content(system_instruction + transcript_str + f"Q: {question}").text

    # Fetch similar content
    search_response = exa.find_similar_and_contents(url, num_results=5, text=False)
    similar_content = extract_titles_and_urls(search_response)

    return response + "\n\n### Similar Content\n" + "\n\n".join(similar_content)

def extract_titles_and_urls(search_response):
    formatted_results = []
    for item in search_response.results:
        title = item.title
        url = item.url
        formatted_results.append(f"**Title:** {title}\n**URL:** {url}")
    return formatted_results
