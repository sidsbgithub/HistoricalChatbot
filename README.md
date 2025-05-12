# Historical Figure Chatbot (with Gemini API)

This project is a Streamlit web application that allows users to chat with AI-powered personas of famous historical figures. The chatbot leverages Google's Gemini Pro API to generate responses that attempt to mimic the chosen figure's personality, perspective, and speaking style, but with access to knowledge up to the modern era.

## Features

*   **Multiple Personas:** Chat with figures like Leonardo da Vinci, Napoleon Bonaparte, William Shakespeare, Marie Curie, Mahatma Gandhi, and Cleopatra VII.
*   **Modern Knowledge:** Historical figures can discuss topics from any era, including modern times, while attempting to maintain their core persona.
*   **Chat Continuity:** Conversation history is maintained separately for each figure during your session.
*   **Thematic Loading:** Fun, persona-specific loading messages when switching figures.
*   **Easy-to-Use Interface:** Built with Streamlit for a clean and interactive user experience.
*   **Configurable:** Easily add new personas or modify existing ones by editing Markdown files.

## Project Structure
Use code with caution.
Markdown
historical_chatbot_project/

├── .venv/ # Virtual environment

├── app.py # Main Streamlit application file

├── personas/ # Directory for persona prompt definitions

│ ├── leonardo_da_vinci.md

│ ├── napoleon_bonaparte.md

│ ├── ... (other .md files)

├── .streamlit/ # Streamlit configuration directory

│ └── secrets.toml # For storing API keys securely

├── requirements.txt # Python package dependencies

├── README.md # This file

└── .gitignore # Specifies intentionally untracked files


## Setup and Installation

### Prerequisites

*   Python 3.8 or higher
*   Access to Google Cloud Platform and the Gemini API (or a Gemini API key from Google AI Studio)
*   `pip` (Python package installer)
*   `git` (optional, for version control)

