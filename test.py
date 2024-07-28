import streamlit as st
import os
from dotenv import load_dotenv
from youtube_transcript_api import YouTubeTranscriptApi
from generate_content import generate_combined_content, PDFDocument

# Load environment variables
load_dotenv()

st.title("YouTube Video Summarizer")

# Function to extract video ID from YouTube URL
def get_video_id(url):
    if "youtube.com/watch?v=" in url:
        return url.split("v=")[1].split("&")[0]
    elif "youtu.be/" in url:
        return url.split("youtu.be/")[1].split("?")[0]
    else:
        return None

# Input field for YouTube URL
yt_url = st.text_input("Enter YouTube URL", "")
if yt_url:
    video_id = get_video_id(yt_url)
    if video_id:
        st.image(f"http://img.youtube.com/vi/{video_id}/0.jpg", use_column_width=False, width=400)
    else:
        st.error("Invalid YouTube URL. Please enter a valid URL.")

# Button to generate and display notes
if st.button("Generate Notes"):
    if yt_url:
        yt_id = get_video_id(yt_url)
        
        # Get transcript
        try:
            transcript = YouTubeTranscriptApi.get_transcript(yt_id)
        except Exception as e:
            st.error(f"Error fetching transcript: {e}")
            transcript = []

        # Prepare formatted transcript
        formatted_transcript = {
            'parts': [{'text': part['text']} for part in transcript]
        }

        # Define system instruction for Gemini
        system_instruction = '''
        You are an expert in creating Notes with YouTube videos from their transcriptions.
        Your task is to produce a clear and comprehensive notes of the video based on the provided transcription.
        Ensure that the notes captures all important information from the transcription and is organized into multiple paragraphs if necessary to enhance clarity.
        Provide a relevant topic or title for the summary, and keep the length under 1000 words.
        While summarizing, fix any typos present in the transcription but avoid adding extraneous information that doesn’t align with the content.
        If the transcription is meaningless or empty, respond with "Couldn't generate summary for the given video. Please provide the summary of the text given here: "
        '''

        # Generate combined content
        combined_content = generate_combined_content(formatted_transcript, system_instruction, yt_url)
        
        # Display generated notes on the interface
        st.write("### Generated Notes:")
        st.write(combined_content)
        
        # Create PDF
        pdf_doc = PDFDocument(title="YouTube Video Summary")
        pdf_content = pdf_doc.create_pdf(combined_content)

        # Provide button to download PDF
        st.download_button(
            label="Download PDF",
            data=pdf_content,
            file_name="notes.pdf",
            mime="application/pdf"
        )
    else:
        st.warning("Please enter a valid YouTube URL.")
