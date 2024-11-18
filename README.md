<img src="img/logo.png" alt="NoteWorthy Logo" width="100" height="100">

# NoteFlow

**Author**: @Maryam-Sikander

## Overview
NoteFlow is a cutting-edge web application designed to simplify note-taking for students. It generates detailed notes from lecture and YouTube video URLs, offers content recommendations, and provides options to download notes as PDFs. Experience seamless interaction with video content and explore related materials effortlessly.
## Try noteworthy
[![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://noteflow.streamlit.app/)

## Motivation
In an era where students and professionals alike juggle numerous sources of information, efficiently capturing and organizing knowledge is essential. NoteFlow was inspired by the need for a comprehensive tool that can not only generate notes from various sources but also enhance the learning experience with personalized content recommendations. By providing a streamlined note-taking process and insightful content suggestions, NoteWorthy aims to make studying and information retrieval more efficient and effective.

## Built With
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)
![Google Gemini](https://img.shields.io/badge/Google%20Gemini-00A1E0?style=for-the-badge&logo=google&logoColor=white)
![EXA.ai](https://img.shields.io/badge/EXA.ai-00A1E0?style=for-the-badge&logo=exa&logoColor=white)
![ReportLab](https://img.shields.io/badge/ReportLab-FFD700?style=for-the-badge&logo=reportlab&logoColor=black)
![YouTube Transcript API](https://img.shields.io/badge/YouTube%20Transcript%20API-FF0000?style=for-the-badge&logo=youtube&logoColor=white)

## Features
- **Note Generation from URLs**: Create comprehensive notes from your lectures and video content.
- **Chat with Video**: Interact directly with video content to extract precise information.
- **PDF Download**: Easily download your notes in a clean, well-formatted PDF.
- **Content Recommendations**: Discover similar content based on your queries.

## Getting Started
1. Clone the repository:
   ```bash
   git clone https://github.com/Maryam-Sikander/noteflow.git
   cd noteflow
2. Install the required packages:
   ```bash
   pip install -r requirements.txt
3. Create an environment file and add your API keys:
   ```bash
   touch .env
   echo GEMINI_API_KEY=[Your API Key] > .env
   echo EXA_API_KEY=[Your API Key] >> .env
4. Run the application using Streamlit:
   ```bash
   streamlit run app.py


