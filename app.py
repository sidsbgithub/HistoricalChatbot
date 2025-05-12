import streamlit as st
import google.generativeai as genai
import os
import time 

# --- Configuration & Setup ---
GOOGLE_API_KEY = None
try:
    GOOGLE_API_KEY = st.secrets.get("GOOGLE_API_KEY")
    if GOOGLE_API_KEY:
        genai.configure(api_key=GOOGLE_API_KEY)
    else:
        # Attempt to use ADC
        pass 
except Exception as e:
    st.error(f"Failed to configure Gemini API: {e}. Check secrets or ADC.")
    st.stop()

# Initialize the client only if API key was found or ADC might work
# We'll rely on the SDK raising errors later if auth fails
try:
    # Test configuration by listing a model (optional)
    # _ = genai.get_generative_model(MODEL_NAME) # Test model access
    pass # Assume configuration is okay for now, errors handled later
except Exception as e:
    st.error(f"Gemini API configuration failed: {e}")
    st.stop()


PERSONA_DIR = "personas"
FIGURE_FILES = {
    "Leonardo da Vinci": "leonardo_da_vinci.md",
    "Napoleon Bonaparte": "napoleon_bonaparte.md",
    "William Shakespeare": "william_shakespeare.md",
    "Marie Curie": "marie_curie.md",
    "Mahatma Gandhi": "mahatma_gandhi.md",
    "Cleopatra VII": "cleopatra_vii.md",
}

# --- Model Configuration ---
MODEL_NAME = "gemini-1.5-flash-latest" # Or "gemini-pro", "gemini-1.5-pro-latest" etc.
SAFETY_SETTINGS = [
    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
]
GENERATION_CONFIG = {
    "temperature": 0.75, # Slightly increased for potentially more creative persona answers
    "top_p": 0.95,
    "top_k": 64, # Gemini often uses higher top_k
    "max_output_tokens": 8192, # Increased max output
}

# --- Persona Loading Messages ---
LOADING_MESSAGES = {
    "Leonardo da Vinci": "Consulting my codices... sketching some ideas...",
    "Napoleon Bonaparte": "Planning my next strategic conversational maneuver...",
    "William Shakespeare": "Hark! Tuning mine eloquence, fetching quills...",
    "Marie Curie": "Preparing my laboratory notes... observing the conversational elements...",
    "Mahatma Gandhi": "Spinning the thread of thought... reflecting on truth...",
    "Cleopatra VII": "Adorning myself with knowledge... preparing the royal audience...",
}

def load_system_prompt(figure_name):
    """Loads the system prompt for the given figure from its .md file."""
    file_path = os.path.join(PERSONA_DIR, FIGURE_FILES.get(figure_name, ""))
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        st.error(f"Persona file not found for {figure_name} at {file_path}")
        return None # Return None on error
    except Exception as e:
        st.error(f"Error loading persona for {figure_name}: {e}")
        return None # Return None on error

# --- Initialize Session State ---
if "current_figure_name" not in st.session_state:
    st.session_state.current_figure_name = None
# Stores separate message histories (for UI display): {figure_name: [messages]}
if "all_messages" not in st.session_state:
    st.session_state.all_messages = {}
# Stores separate Gemini chat sessions: {figure_name: chat_session_object}
if "all_chat_sessions" not in st.session_state:
    st.session_state.all_chat_sessions = {}

# --- UI Elements ---
st.set_page_config(page_title="Historical Figure Chatbot", layout="wide", initial_sidebar_state="expanded")
st.title(" Chat with Historical Figures 📜 (via Gemini)")
st.caption("Select a figure from the sidebar and ask your questions!")

# --- Sidebar for Figure Selection ---
with st.sidebar:
    st.header("Choose Your Conversationalist")
    figure_options = list(FIGURE_FILES.keys())
    current_figure_index = None
    if st.session_state.current_figure_name in figure_options:
        current_figure_index = figure_options.index(st.session_state.current_figure_name)

    selected_figure = st.selectbox(
        "Figure:",
        options=figure_options,
        index=current_figure_index,
        placeholder="Select a figure..."
    )

    # Handle Figure Change / Initial Selection
    if selected_figure:
        if selected_figure != st.session_state.current_figure_name:
            # Show persona-specific loading message
            loading_message = LOADING_MESSAGES.get(selected_figure, f"Summoning {selected_figure}...")
            with st.spinner(loading_message):
                # Update the currently selected figure
                st.session_state.current_figure_name = selected_figure

                # Initialize history and chat session ONLY IF they don't exist for this figure
                if selected_figure not in st.session_state.all_messages:
                    system_prompt_text = load_system_prompt(selected_figure)
                    if system_prompt_text: # Only proceed if prompt loaded successfully
                        st.session_state.all_messages[selected_figure] = [] # Init empty message list for display

                        try:
                            model = genai.GenerativeModel(
                                MODEL_NAME,
                                safety_settings=SAFETY_SETTINGS,
                                generation_config=GENERATION_CONFIG,
                                system_instruction=system_prompt_text
                            )
                            # Store the new chat session object
                            st.session_state.all_chat_sessions[selected_figure] = model.start_chat(history=[])
                            st.success(f"Ready to chat with {selected_figure}!") # Feedback after loading

                        except Exception as e:
                            st.error(f"Failed to initialize Gemini session for {selected_figure}: {e}")
                            # Reset selection if initialization failed
                            st.session_state.current_figure_name = None
                            if selected_figure in st.session_state.all_messages:
                                del st.session_state.all_messages[selected_figure]
                            if selected_figure in st.session_state.all_chat_sessions:
                                del st.session_state.all_chat_sessions[selected_figure]
                    else:
                        # Handle case where system prompt failed to load
                        st.error(f"Could not load persona for {selected_figure}. Please check files.")
                        st.session_state.current_figure_name = None # Reset selection
                # If the figure's data already exists, we don't need to do anything here

            st.rerun() # Rerun AFTER spinner to update the main UI

    # Display status and clear button if a figure is active
    active_figure = st.session_state.current_figure_name
    if active_figure and active_figure in st.session_state.all_chat_sessions:
        st.success(f"Chatting with: **{active_figure}**")
        if st.button(f"Clear Chat with {active_figure}"):
             with st.spinner(f"Resetting conversation with {active_figure}..."):
                # Re-initialize chat session and clear messages for this figure
                system_prompt_text = load_system_prompt(active_figure)
                if system_prompt_text:
                    try:
                        model = genai.GenerativeModel(
                            MODEL_NAME,
                            safety_settings=SAFETY_SETTINGS,
                            generation_config=GENERATION_CONFIG,
                            system_instruction=system_prompt_text
                        )
                        st.session_state.all_chat_sessions[active_figure] = model.start_chat(history=[])
                        st.session_state.all_messages[active_figure] = []
                    except Exception as e:
                         st.error(f"Failed to restart Gemini chat session: {e}")
                else:
                    st.error(f"Could not reload system prompt to clear chat for {active_figure}.")
             st.rerun()
    elif not active_figure:
        st.info("Please select a figure to begin.")
    # Handle case where figure is selected but session failed to init (error shown above)

# --- Main Chat Interface ---
active_figure = st.session_state.current_figure_name
if active_figure and active_figure in st.session_state.all_messages and active_figure in st.session_state.all_chat_sessions:
    # Display messages from the correct history list
    for message in st.session_state.all_messages[active_figure]:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # User input
    if prompt := st.chat_input(f"Your question for {active_figure}..."):
        # Add user message to the correct history list (for UI display)
        st.session_state.all_messages[active_figure].append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Get AI response using the correct chat session
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            full_response_content = ""
            try:
                # Get the specific chat session for the active figure
                chat_session = st.session_state.all_chat_sessions[active_figure]
                
                # Send message to the session
                response = chat_session.send_message(
                    prompt,
                    # stream=True # Optional for streaming
                )
                ai_response_content = response.text
                message_placeholder.markdown(ai_response_content)
                full_response_content = ai_response_content

            except genai.types.generation_types.BlockedPromptException as bpe:
                error_msg = "Prompt blocked by safety filters."
                st.warning(error_msg)
                full_response_content = f"Safety Error: {error_msg}"
            except genai.types.generation_types.StopCandidateException as sce:
                error_msg = "Model stopped generation."
                st.warning(error_msg)
                full_response_content = f"Generation Stop Error: {error_msg}"
            # Handle other specific Gemini/Google API errors if needed
            except Exception as e:
                error_msg = f"An unexpected error occurred with the Gemini API: {e}"
                st.error(error_msg)
                full_response_content = f"Unexpected Error: {error_msg}"

            # Add AI's response (or error message) to the correct history list
            st.session_state.all_messages[active_figure].append({"role": "assistant", "content": full_response_content})

else:
    if not st.session_state.current_figure_name:
        st.info("👋 Welcome! Please select a historical figure from the sidebar.")
    # Optional: Add a message if figure selected but session isn't ready (e.g., due to earlier error)
    elif st.session_state.current_figure_name and st.session_state.current_figure_name not in st.session_state.all_chat_sessions:
         st.warning(f"Chat session for {st.session_state.current_figure_name} could not be initialized. Please check errors or try selecting again.")