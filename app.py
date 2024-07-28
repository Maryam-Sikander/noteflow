import streamlit as st
from dotenv import load_dotenv
from generate_content import generate_summary, ReportPDF
from QA import generate_answer, retrieve_transcript
from youtube_transcript_api import YouTubeTranscriptApi

# Load environment variables
load_dotenv()

# Set up the Streamlit app
st.set_page_config(page_title="NoteWorthy", page_icon="img/logo.png", layout="wide")
st.markdown("")
st.markdown("")
st.markdown("# :rainbow[NoteWorthy]")

# Custom CSS for sidebar styling
st.markdown("""
    <style>
    /* General Background */
    body {
        background-color: #f0f2f6;
    }

    /* Sidebar Styling */
    .sidebar .sidebar-content {
        background-color: #007bff;
        color: white;
    }
    .sidebar .sidebar-content h1 {
        color: white;
        font-family: 'Comic Sans MS', cursive, sans-serif;
        font-size: 24px;
    }
    .sidebar .sidebar-content h2 {
        color: white;
        font-family: 'Comic Sans MS', cursive, sans-serif;
        font-size: 18px;
    }
    .sidebar .sidebar-content ul {
        color: white;
    }

    /* Button Styling */
    .stButton>button {
        background-color: #28a745;
        color: white;
        border: none;
        border-radius: 5px;
        padding: 10px;
        cursor: pointer;
    }
    .stButton>button:hover {
        background-color: #218838;
    }

    /* Input Fields */
    .stTextInput>div>input {
        border: 2px solid #007bff;
        border-radius: 5px;
        padding: 10px;
    }
    .stTextArea>div>textarea {
        border: 2px solid #007bff;
        border-radius: 5px;
        padding: 10px;
    }

    /* Warning and Error Messages */
    .stWarning {
        background-color: #fff3cd;
        color: #856404;
        padding: 10px;
        border-radius: 5px;
    }
    .stError {
        background-color: #f8d7da;
        color: #721c24;
        padding: 10px;
        border-radius: 5px;
    }

    /* Title Styling */
    .main .block-container {
        padding: 20px;
    }
    .stTitle {
        font-family: 'Comic Sans MS', cursive, sans-serif;
        color: #007bff;
        text-align: center;
    }
    .stTitle img {
        height: 50px;
        vertical-align: middle;
        margin-right: 10px;
    }
    </style>
""", unsafe_allow_html=True)

# Sidebar configuration
with st.sidebar:
    st.image("img/logo.png", use_column_width=True, width=30)
    st.info("**Hey Leaders! Start here ↓**", icon="👋🏾")

    # Define custom CSS for radio buttons
    st.markdown("""
        <style>
        .stRadio > div > div > label > div {
            border-radius: 5px;
            padding: 10px;
            margin: 5px;
            border: 2px solid transparent;
        }
        .stRadio > div > div > label > div:hover {
            border-color: blue;
        }
        .stRadio > div > div > label.st-selected > div {
            border-color: blue;
            background-color: #f0f8ff; /* Light blue background */
        }
        </style>
    """, unsafe_allow_html=True)

    selected_feature = st.radio(
        label="🔍 Select Feature",
        options=["Generate Comprehensive Notes", "Talk with Video"],
        format_func=lambda x: f"📄 {x}" if x == "Generate Comprehensive Notes" else f"🔍 {x}"
    )

    st.markdown("""
    <h2 style="color: #A020F0;">📚 Explore Noteworthy’s Features:</h2>
    <ul style="list-style-type: none; padding: 0;">
        <li style="margin-bottom: 10px;">
            <strong style="color: #3498db;">📝 Generate Comprehensive Notes:</strong> 
            Simply input a YouTube URL, and Noteworthy will transform the video transcript into detailed, organized notes. Perfect for turning lengthy content into easy-to-read summaries!
        </li>
        <li>
            <strong style="color: #3498db;">❓ Talk with Video:</strong> 
            Have a question about the video? Just ask, and Noteworthy will provide precise answers based on the video content. Ideal for quick and accurate information retrieval!
        </li>
    </ul>
    """, unsafe_allow_html=True)
    st.markdown("""
    <style>
    .custom-thumbnail {
        width: 350px;
        height: auto; /* Maintain aspect ratio */
    }
    </style>
    """, unsafe_allow_html=True)

# Function to get video ID from URL
def extract_video_id(url):
    if 'youtube.com/watch?v=' in url:
        return url.split('v=')[1].split('&')[0]
    elif 'youtu.be/' in url:
        return url.split('youtu.be/')[1]
    return ''

# Main app content
if selected_feature == "Generate Comprehensive Notes":
    st.subheader(":orange[**Generate Comprehensive Notes**]")
    youtube_url = st.text_input(":green[Enter YouTube URL]", "")
    
    if youtube_url:
        video_id = extract_video_id(youtube_url)
        if video_id:
            st.markdown(f'<img src="http://img.youtube.com/vi/{video_id}/0.jpg" class="custom-thumbnail">', unsafe_allow_html=True)

    if st.button("Generate Notes"):
        if youtube_url:
            video_id = extract_video_id(youtube_url)

            # Display spinner while processing
            with st.spinner("👩🏾‍🍳 Whipping up your video into text..."):
                st.write("🙆‍♀️ Meanwhile, stand up and stretch in the meantime")

                try:
                    transcript = YouTubeTranscriptApi.get_transcript(video_id)
                except Exception as e:
                    st.error("Couldn't fetch transcript. Please try another URL or check the video availability.")
                    transcript = []

                formatted_transcript = {
                    'parts': [{'text': part['text']} for part in transcript]
                }

                system_instruction = '''
                You are an expert in creating comprehensive notes from YouTube videos using their transcriptions. 
                Your primary task is to produce clear and well-organized notes based on the provided transcription. 
                Ensure that these notes capture all important information from the video and are structured into multiple paragraphs if necessary to enhance clarity and coherence. 
                Provide a relevant topic or title for the summary that accurately reflects the core subject of the video, and keep the length of the notes under 1000 words. 
                If the video focuses on creating an effective roadmap, ensure that the notes include actionable insights and a structured approach to roadmap creation. If there is no roadmap discussed in the video, then don't create the roadmap.
                While summarizing, correct any typos or grammatical errors found in the transcription but avoid introducing extraneous information that does not align with the video's content.
                If the transcription is meaningless or empty, please respond with, "Couldn't generate summary for the given video. Please provide the summary of the text given here: "
                '''

                summary_content = generate_summary(formatted_transcript, system_instruction, youtube_url)
                st.write("### Generated Notes:")
                st.write(summary_content)

                pdf_generator = ReportPDF(title="YouTube Video Summary")
                pdf_data = pdf_generator.generate_pdf(summary_content)

                st.download_button(
                    label="Download PDF",
                    data=pdf_data,
                    file_name="my_notes.pdf",
                    mime="application/pdf"
                )
        else:
            st.warning("Please enter a valid YouTube URL.")

elif selected_feature == "Talk with Video":
    st.subheader(":orange[**Chat with Video 🧾**]")
    youtube_url = st.text_input(":green[**Enter YouTube URL**]", "")
    user_question = st.text_area(":green[**Enter Your Question**]", "")

    if st.button("Get Answer"):
        if youtube_url and user_question:
            with st.spinner("🔍 Processing your query..."):
                st.write("⚙️ Analyzing video transcript")
                st.write("🕒 This might take a moment...")

                transcript = retrieve_transcript(youtube_url)
                if transcript:
                    answer = generate_answer(user_question, transcript, youtube_url)
                    st.write("### Answer:")
                    st.write(answer)
                else:
                    st.error("Couldn't fetch transcript. Please try another URL or check the video availability.")
        elif not youtube_url:
            st.warning("Please enter a valid YouTube URL.")
        elif not user_question:
            st.warning("Please enter a question.")
