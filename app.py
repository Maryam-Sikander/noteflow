import streamlit as st
from dotenv import load_dotenv
from generate_content import generate_summary, ReportPDF 
from QndA import generate_answer, retrieve_transcript
from youtube_transcript_api import YouTubeTranscriptApi

# Load environment variables
load_dotenv()

# Set up the Streamlit app with custom styles
st.set_page_config(page_title="NoteFlow", page_icon="img/logo.png", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@700&display=swap');
    @import url('https://fonts.googleapis.com/css2?family=Lobster&display=swap');

    .sub-title {
        font-family: 'Roboto', sans-serif;
        font-size: 1.4em;
        color: #4682b4;
    }

    .sidebar-title {
        font-family: 'Roboto', sans-serif;
        font-size: 1.5em;
        color: #4682b4;
    }

    .highlight {
        background-color: #ff6347;
        color: white;
        padding: 0.2em 0.4em;
        border-radius: 0.2em;
    }

    .sidebar-info {
        background-color: #f0f8ff;
        padding: 1em;
        border-radius: 0.5em;
        text-align: center;
    }
    </style>
    """, unsafe_allow_html=True)

st.markdown("# :rainbow[NoteFlow]")
# Sidebar configuration
with st.sidebar:
    st.image("img/logo.png", use_column_width=True, width=30)
    st.info("**Hey Leaders! Start here ↓**", icon="👋🏾")

    selected_feature = st.radio(
        label="📋 **Select Feature**",
        options=["Generate Comprehensive Notes", "Talk with Video"],
        format_func=lambda x: f"📄 {x}" if x == "Generate Comprehensive Notes" else f"🔍 {x}"
    )

    st.markdown('<h3 class="sidebar-title">Select Font for PDF</h3>', unsafe_allow_html=True)
    fonts = ["Regular", "Bold", "Italic"]
    font = st.selectbox("Select Font", options=fonts)
    
def extract_video_id(url):
    if 'youtube.com/watch?v=' in url:
        return url.split('v=')[1].split('&')[0]
    elif 'youtu.be/' in url:
        return url.split('youtu.be/')[1]
    return ''

if selected_feature == "Generate Comprehensive Notes":
    st.markdown('<h3 class="sub-title">Generate Comprehensive Notes</h3>', unsafe_allow_html=True)
    youtube_url = st.text_input("🎥 Enter YouTube URL", "")

    if youtube_url:
        video_id = extract_video_id(youtube_url)
        if video_id:
            st.markdown(f'<img src="http://img.youtube.com/vi/{video_id}/0.jpg" class="custom-thumbnail">', unsafe_allow_html=True)

    if st.button("📝 Generate Notes"):
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

                formatted_transcript = {'parts': [{'text': part['text']} for part in transcript]}
                system_instruction = '''
                You are an expert in creating comprehensive notes from YouTube videos using their transcriptions. 
                Your primary task is to produce clear and well-organized notes based on the provided transcription. Gives notes a unique title. 
                Ensure that these notes capture all important information from the video and are structured into multiple paragraphs if necessary to enhance clarity and coherence. 
                Provide a relevant topic or title for the summary that accurately reflects the core subject of the video, and keep the length of the notes under 1000 words. 
                If the video focuses on creating an effective roadmap, ensure that the notes include actionable insights and a structured approach to roadmap creation. If there is no roadmap discussed in the video, then don't create the roadmap.
                While summarizing, correct any typos or grammatical errors found in the transcription but avoid introducing extraneous information that does not align with the video's content.
                If the transcription is meaningless or empty, please respond with, "Couldn't generate summary for the given video. Please provide the summary of the text given here: "
                '''

                summary_content = generate_summary(formatted_transcript, system_instruction, youtube_url)
                st.write("### Generated Notes:")
                st.write(summary_content)

                pdf_generator = ReportPDF(title="YouTube Video Summary", font=font, font_size=font_size)
                pdf_data = pdf_generator.generate_pdf(summary_content)

                st.download_button(
                    label="📥 Download Notes",
                    data=pdf_data,
                    file_name="My_Notes.pdf",
                    mime="application/pdf"
                )

        else:
            st.warning("Please enter a valid YouTube URL.")

elif selected_feature == "Talk with Video":
    st.markdown('<h3 class="sub-title">Chat with Video 🧾</h3>', unsafe_allow_html=True)
    youtube_url = st.text_input("🎥 Enter YouTube URL", "")
    user_question = st.text_area("❓ Enter Your Question", "")

    if st.button("🔍 Get Answer"):
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
