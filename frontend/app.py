"""
SONA AI - Streamlit Frontend (MVP)
Simple interface for evaluation sessions
"""

import streamlit as st
import requests
from typing import Optional
import json

# API Configuration
API_BASE_URL = "http://localhost:8000/api/v1"


# ===========================
# Page Configuration
# ===========================

st.set_page_config(
    page_title="SONA AI - Learning Evaluator",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ===========================
# Custom CSS
# ===========================

st.markdown("""
    <style>
    .main-header {
        font-size: 3rem;
        font-weight: 700;
        text-align: center;
        margin-bottom: 1rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .subtitle {
        text-align: center;
        color: #666;
        margin-bottom: 2rem;
    }
    .score-card {
        padding: 1.5rem;
        border-radius: 10px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        text-align: center;
    }
    .score-value {
        font-size: 3rem;
        font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)


# ===========================
# Session State Initialization
# ===========================

if 'session_id' not in st.session_state:
    st.session_state.session_id = None
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'understanding_score' not in st.session_state:
    st.session_state.understanding_score = 50.0
if 'session_active' not in st.session_state:
    st.session_state.session_active = False
if 'tutor_response' not in st.session_state:
    st.session_state.tutor_response = None
if 'tutor_feedback_given' not in st.session_state:
    st.session_state.tutor_feedback_given = False


# ===========================
# Helper Functions
# ===========================

def create_session(claim: str, sources: list, tone: str, difficulty: str, user_name: str, initial_confidence: float):
    """Create new evaluation session"""
    payload = {
        "claim": claim,
        "sources": sources,
        "tone": tone,
        "difficulty": difficulty,
        "user_name": user_name,
        "confidence": initial_confidence
    }
    
    try:
        response = requests.post(f"{API_BASE_URL}/session/create", json=payload)
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Error creating session: {response.text}")
            return None
    except Exception as e:
        st.error(f"Connection error: {str(e)}")
        return None


def get_next_question(session_id: str):
    """Get next question from backend"""
    try:
        response = requests.get(f"{API_BASE_URL}/chat/question/{session_id}")
        if response.status_code == 200:
            return response.json()
        return None
    except Exception as e:
        st.error(f"Error getting question: {str(e)}")
        return None


def submit_answer(session_id: str, question_id: str, answer: str):
    """Submit answer and get evaluation"""
    payload = {
        "question_id": question_id,
        "answer": answer
    }
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/chat/answer/{session_id}",
            json=payload
        )
        if response.status_code == 200:
            return response.json()
        return None
    except Exception as e:
        st.error(f"Error submitting answer: {str(e)}")
        return None


def ask_tutor(session_id: str, question: str):
    """Ask the tutor a question"""
    payload = {"question": question}
    
    try:
        response = requests.post(f"{API_BASE_URL}/chat/ask/{session_id}", json=payload)
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 404:
            st.warning("Session expired or not found.")
            return None
        else:
            st.error(f"Error asking tutor: {response.text}")
            return None
    except Exception as e:
        st.error(f"Connection error: {str(e)}")
        return None


def send_feedback(session_id: str, score: float, comment: str = None):
    """Send user feedback to backend"""
    payload = {
        "session_id": session_id,
        "score": score,
        "comment": comment
    }
    try:
        requests.post(f"{API_BASE_URL}/chat/feedback", json=payload)
        return True
    except:
        return False


# ===========================
# Main UI
# ===========================

def main():
    # Header
    st.markdown('<h1 class="main-header">🧠 SONA AI</h1>', unsafe_allow_html=True)
    st.markdown(
        '<p class="subtitle">Socratic Navigator & Assessor - '
        'Prove what you\'ve understood, not just what you\'ve consumed</p>',
        unsafe_allow_html=True
    )
    
    # Sidebar - Session Setup
    with st.sidebar:
        st.header("📋 Session Setup")
        
        if not st.session_state.session_active:
            # Learning Claim
            claim = st.text_area(
                "What did you learn?",
                placeholder="e.g., I learned about HTTP caching mechanisms",
                height=100
            )
            
            # Source Upload
            st.subheader("📚 Learning Materials")
            source_type = st.selectbox(
                "Source Type",
                ["YouTube", "Website", "PDF", "Text"]
            )
            
            if source_type == "YouTube":
                source_input = st.text_input("YouTube URL")
            elif source_type == "Website":
                source_input = st.text_input("Website URL")
            elif source_type == "PDF":
                source_input = st.file_uploader("Upload PDF", type=['pdf'])
            else:
                source_input = st.text_area("Paste your text", height=150)
            
            # User Profile
            st.subheader("👤 User Profile")
            user_name = st.text_input("How should SONA call you?", value="Learner")
            
            initial_confidence = st.slider(
                "How confident are you in this?",
                min_value=0.0,
                max_value=1.0,
                value=0.5,
                help="How confident are you in this topic?"
            )
            
            # Tone Selection
            tone_label = st.selectbox(
                "How should SONA behave?",
                options=["Friendly", "Strict Professor", "Aggressive / Provocative"],
                index=0,
                help="Choose the personality of the AI tutor"
            )
            
            # Map UI labels to Backend Keys
            tone_mapping = {
                "Friendly": "friendly",
                "Strict Professor": "academic",
                "Aggressive / Provocative": "roast"
            }
            selected_tone_key = tone_mapping[tone_label]
            
            # Difficulty
            difficulty = st.select_slider(
                "Starting Difficulty",
                options=["Easy", "Medium", "Hard"],
                value="Medium"
            )
            
            # Start Session Button
            if st.button("🚀 Start Evaluation", type="primary", use_container_width=True):
                if claim and source_input:
                    with st.spinner("Creating session and processing sources..."):
                        # Map source input correctly based on type
                        source_type_lower = source_type.lower()
                        
                        if source_type_lower in ["youtube", "website"]:
                            # URL-based sources
                            sources = [{"type": source_type_lower, "url": str(source_input)}]
                        elif source_type == "PDF":
                             # PDF file logic is same, assuming imports exist above
                            import tempfile
                            import os
                            
                            temp_dir = tempfile.mkdtemp()
                            temp_path = os.path.join(temp_dir, source_input.name)
                            with open(temp_path, "wb") as f:
                                f.write(source_input.getbuffer())
                            sources = [{"type": "pdf", "file_path": temp_path}]
                        else:
                            sources = [{"type": "text", "content": str(source_input)}]
                        
                        # Pass all preferences to backend
                        result = create_session(
                            claim, 
                            sources, 
                            selected_tone_key, # Use mapped key
                            difficulty.lower(), 
                            user_name, 
                            initial_confidence
                        )
                        
                        if result:
                            st.session_state.session_id = result['session_id']
                            st.session_state.session_active = True
                            
                            # Show extraction stats
                            message = result.get('message', 'Session created')
                            st.success(f"✅ {message}")
                            
                            # Greeting Flow (Phase 9)
                            with st.spinner("Preparing your personalized session..."):
                                try:
                                    # Call greeting endpoint
                                    greeting_resp = requests.get(f"{API_BASE_URL}/session/greeting/{result['session_id']}")
                                    if greeting_resp.status_code == 200:
                                        greeting_text = greeting_resp.json()['greeting']
                                        
                                        # Add greeting to chat
                                        st.session_state.messages.append({
                                            "role": "assistant",
                                            "content": greeting_text
                                        })
                                        
                                        # Use a special state to indicate we are waiting for confirmation
                                        st.session_state.waiting_for_start = True
                                        
                                    else:
                                        # Fallback if greeting fails
                                        st.warning("Could not fetch greeting, starting directly.")
                                        question_data = get_next_question(result['session_id'])
                                        if question_data:
                                            st.session_state.messages.append({
                                                "role": "assistant",
                                                "content": question_data['question_text'], # FIXED: Matches backend model
                                                "question_id": question_data['question_id']
                                            })
                                            
                                except Exception as e:
                                    st.error(f"Error starting session: {e}")
                            
                            st.rerun()
                else:
                    st.warning("Please provide both a learning claim and source material")
        
        else:
            # Active Session Info
            st.success("✅ Session Active")
            
            # Understanding Score Display
            st.markdown("### 📊 Understanding Score")
            score = st.session_state.understanding_score
            
            st.markdown(f"""
                <div class="score-card">
                    <div class="score-value">{score:.1f}</div>
                    <div>out of 100</div>
                </div>
            """, unsafe_allow_html=True)
            
            # Progress Info
            st.markdown("---")
            st.metric("Questions Asked", len(st.session_state.messages) // 2)
            
            # End Session Button
            if st.button("🛑 End Session", use_container_width=True):
                st.session_state.session_active = False
                st.session_state.session_id = None
                st.session_state.messages = []
                st.session_state.understanding_score = 50.0
                st.rerun()
    
    # Main Content Area
    if st.session_state.session_active:
        
        # ===========================
        # Sidebar: Tutor Section (Moved here to clear main view)
        # ===========================
        with st.sidebar:
            st.markdown("---")
            with st.expander("🙋 Ask the Tutor (Help)", expanded=False):
                st.info("Stuck? Ask the AI Tutor for help!")
                
                tutor_question = st.text_input("Your Question:", key="tutor_input")
                
                if st.button("Ask Tutor", type="secondary"):
                    if tutor_question:
                        with st.spinner("Tutor is thinking..."):
                            tutor_response = ask_tutor(st.session_state.session_id, tutor_question)
                            
                            if tutor_response:
                                st.session_state.tutor_response = tutor_response
                                st.session_state.tutor_feedback_given = False
                    else:
                        st.warning("Please enter a question first.")

                # Display Persistent Response in Sidebar
                if st.session_state.tutor_response:
                    resp = st.session_state.tutor_response
                    st.markdown(f"**🎓 Answer:**")
                    st.markdown(resp['answer'])
                    
                    if resp.get('follow_up'):
                        st.info(f"💡 Thought: {resp['follow_up']}")
                    
                    # Mini Feedback UI
                    if not st.session_state.tutor_feedback_given:
                        col1, col2 = st.columns(2)
                        with col1:
                            if st.button("👍", key="tutor_up"):
                                send_feedback(st.session_state.session_id, 1.0, "Helpful")
                                st.session_state.tutor_feedback_given = True
                                st.rerun()
                        with col2:
                            if st.button("👎", key="tutor_down"):
                                send_feedback(st.session_state.session_id, 0.0, "Not Helpful")
                                st.session_state.tutor_feedback_given = True
                                st.rerun()
                    else:
                        st.caption("Thanks for feedback!")

        # ===========================
        # Main Chat Interface (Center Stage)
        # ===========================
        st.markdown("### 💬 Interrogation Session")
        
        # Create a container for chat history to keep it organized
        chat_container = st.container()
        
        with chat_container:
            if not st.session_state.messages:
                st.info("Waiting for the first question...")
            
            for message in st.session_state.messages:
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])
                    
                    # Show evaluation scores if available
                    if message["role"] == "assistant":
                        if "scores" in message:
                            scores = message["scores"]
                            # Use concise metrics row
                            c1, c2, c3 = st.columns(3)
                            c1.metric("Correctness", f"{scores['correctness']:.0f}%")
                            c2.metric("Depth", f"{scores['depth']:.0f}%")
                            c3.metric("Transfer", f"{scores['transfer']:.0f}%")
                        
                        # Show Source Verification (Phase 10)
                        if "source_context" in message:
                             with st.expander("🔍 Verified Source Context", expanded=False):
                                 st.caption("This question was generated based on:")
                                 st.markdown(f"_{message['source_context']}_")
        
        # Padding to push input to bottom
        st.markdown("<br><br>", unsafe_allow_html=True)

        # Answer Input
        if st.session_state.get("waiting_for_start", False):
            # Just show standard input, user types 'Yes' or whatever
            # We can't easily pre-fill 'value' in st.chat_input without a rerun-loop trick which is buggy.
            # Best UX here is just let them type.
            answer = st.chat_input("Type 'Yes' to begin...")
        else:
            answer = st.chat_input("Type your answer here...")
        
        if answer:
            # Add user message
            st.session_state.messages.append({"role": "user", "content": answer})
            
            # If we were waiting for start, now we fetch Q1
            if st.session_state.get("waiting_for_start", False):
                 st.session_state.waiting_for_start = False # Reset state
                 with st.spinner("Analyzing context..."):
                     q_data = get_next_question(st.session_state.session_id)
                     if q_data:
                         st.session_state.messages.append({
                             "role": "assistant",
                             "content": q_data['question_text'],
                             "question_id": q_data['question_id'],
                             "source_context": q_data.get('source_context') # Added
                         })
                 st.rerun()
            
            # Normal Flow: Submit answer and get evaluation
            else:
                with st.spinner("Evaluating your answer..."):
                    result = submit_answer(
                        st.session_state.session_id, 
                        st.session_state.messages[-2].get('question_id', 'unknown'),
                        answer
                    )
                    
                    if result:
                        # Update score
                        st.session_state.understanding_score = result['understanding_score']
                        
                        # Add evaluation response
                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": f"Score: {result['scores']['answer_score']}/100. \n\n" + (result.get('feedback') or "Good effort. Let's continue."),
                            "scores": result['scores']
                        })
                        
                        # Determine next step
                        if result['should_continue']:
                            # Get next question
                            q_data = get_next_question(st.session_state.session_id)
                            if q_data:
                                st.session_state.messages.append({
                                    "role": "assistant",
                                    "content": q_data['question_text'],
                                    "question_id": q_data['question_id'],
                                    "source_context": q_data.get('source_context') # Added
                                })
                        else:
                            st.balloons()
                            st.success("🎉 Session Complete! You have proven your understanding.")
            
                st.rerun()
    
    else:
        # Welcome Screen
        st.markdown("""
        ## 👋 Welcome to SONA AI
        
        **SONA doesn't teach. It interrogates, adapts, measures, and stops when it has enough evidence.**
        
        ### How it works:
        
        1. **Tell us what you learned** - Make a claim about your understanding
        2. **Show us your material** - Upload or link to what you studied
        3. **Get challenged** - Answer adaptive questions that probe your real understanding
        4. **See the truth** - Get honest feedback on correctness, depth, and transfer ability
        
        ### What we measure:
        
        - **Correctness** (50%): Are your answers factually accurate?
        - **Depth** (30%): Do you understand the nuances and context?
        - **Transfer** (20%): Can you apply concepts to new situations?
        
        ---
        
        **Ready to prove your understanding?** Use the sidebar to start a session →
        """)


if __name__ == "__main__":
    main()
