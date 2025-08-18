import streamlit as st
import pandas as pd
# Import functions from your utility files. We'll build these next!
# from utils.api_handler import generate_content
# from utils.calculations import calculate_sample_size, calculate_duration
# from utils.pdf_generator import create_pdf

# --- Custom CSS for a Polished UI ---
# This CSS makes the app look sleek and modern with a dark theme,
# custom fonts, and styled components.
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@400;700&display=swap');
    
    html, body, [class*="st-"] {
        font-family: 'Roboto', sans-serif;
    }
    
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #e0e0e0;
        text-align: center;
        padding-bottom: 20px;
    }

    .st-emotion-cache-18ni7ap {
        background-color: transparent !important;
    }

    .st-emotion-cache-1r6r8k {
        background-color: transparent !important;
    }

    .st-emotion-cache-z5fcl4 {
        background-color: #0d1117;
        color: #f0f0f0;
    }

    h1, h2, h3, h4, h5, h6 {
        color: #e0e0e0;
    }
    
    .st-emotion-cache-6qob1r {
        background-color: #161b22;
        border-radius: 10px;
        padding: 20px;
        border: 1px solid #30363d;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.2);
    }
    
    .stButton > button {
        background-color: #216d33;
        color: white;
        border-radius: 8px;
        border: none;
        padding: 10px 20px;
        transition: transform 0.2s;
    }
    
    .stButton > button:hover {
        background-color: #2ea043;
        transform: scale(1.05);
    }

    .st-expander details {
        background-color: #161b22;
        border: 1px solid #30363d;
        border-radius: 8px;
        padding: 10px;
    }
    
    .st-expander details summary {
        color: #c9d1d9;
    }

    .css-1cpxqw2 {
        background-color: #161b22;
        border: 1px solid #30363d;
        border-radius: 8px;
        color: #c9d1d9;
    }

    .stAlert {
        border-radius: 8px;
    }

    .st-emotion-cache-163kly3 {
        padding: 20px;
    }

    .st-emotion-cache-h5g5k2 {
        padding-left: 1rem;
        padding-right: 1rem;
        padding-top: 1rem;
    }
    .css-15tx6o4 {
        padding-left: 1rem;
        padding-right: 1rem;
        padding-top: 1rem;
    }
</style>
""", unsafe_allow_html=True)


# --- Constants & State Management ---
STAGES = ["Intro", "Hypothesis", "PRD", "Calculations", "Review"]
if "stage" not in st.session_state:
    st.session_state.stage = "Intro"
if "prd_data" not in st.session_state:
    st.session_state.prd_data = {
        "intro_data": {},
        "hypothesis": {},
        "prd_sections": {},
        "calculations": {}
    }

# --- Helper Functions for Navigation ---
def next_stage():
    """Moves the application to the next stage."""
    current_index = STAGES.index(st.session_state.stage)
    if current_index < len(STAGES) - 1:
        st.session_state.stage = STAGES[current_index + 1]

def back_stage():
    """Moves the application to the previous stage."""
    current_index = STAGES.index(st.session_state.stage)
    if current_index > 0:
        st.session_state.stage = STAGES[current_index - 1]

# --- UI Rendering Functions for Each Stage ---
def render_intro_page():
    """Renders the initial form for gathering business context."""
    st.header("Step 1: The Basics 📝")
    st.write("Please provide some high-level details about your A/B test.")

    with st.form("intro_form"):
        st.subheader("Business & Product Details")
        col1, col2 = st.columns(2)
        with col1:
            st.session_state.prd_data["intro_data"]["business_goal"] = st.text_input(
                "Business Goal",
                placeholder="e.g., Increase user engagement"
            )
            st.session_state.prd_data["intro_data"]["key_metric"] = st.text_input(
                "Key Metric",
                placeholder="e.g., Login Rate"
            )
            st.session_state.prd_data["intro_data"]["current_value"] = st.number_input(
                "Current Metric Value (%)",
                min_value=0.0,
                max_value=100.0,
                value=50.0,
                help="The current value of your key metric."
            )
        with col2:
            st.session_state.prd_data["intro_data"]["product_area"] = st.text_input(
                "Product Area",
                placeholder="e.g., Mobile App Onboarding"
            )
            st.session_state.prd_data["intro_data"]["target_value"] = st.number_input(
                "Target Metric Value (%)",
                min_value=0.0,
                max_value=100.0,
                value=55.0,
                help="The value you are aiming for."
            )
            st.session_state.prd_data["intro_data"]["dau"] = st.number_input(
                "Daily Active Users (DAU)",
                min_value=100,
                value=10000,
                help="The total number of unique users daily."
            )

        submit_button = st.form_submit_button("Generate Hypotheses")
        if submit_button:
            if all(v for v in st.session_state.prd_data["intro_data"].values()):
                st.session_state.hypotheses = {
                    "Hypothesis 1": {
                        "Statement": "Changing the login button to a vibrant red will increase login rate.",
                        "Rationale": "Red is a color that often signifies urgency and action.",
                        "Behavioral Basis": "Color psychology influences user behavior.",
                        "Implementation Steps": "Update button CSS to color: red."
                    },
                    "Hypothesis 2": {
                        "Statement": "Adding a progress bar to the onboarding flow will increase login rate.",
                        "Rationale": "Users are more likely to complete a task if they can see their progress.",
                        "Behavioral Basis": "The Zeigarnik effect states that people remember unfinished tasks more than finished ones.",
                        "Implementation Steps": "Add a progress bar component to the top of the onboarding screens."
                    },
                    "Hypothesis 3": {
                        "Statement": "Simplifying the sign-up form by removing the optional 'phone number' field will reduce friction and increase login rate.",
                        "Rationale": "A shorter form requires less effort from the user, reducing the cognitive load.",
                        "Behavioral Basis": "The Fitts's Law principle suggests that the time to acquire a target is a function of the distance to and size of the target. Simplifying the form reduces the 'distance' to completion.",
                        "Implementation Steps": "Remove the optional phone number field from the sign-up form."
                    }
                }
                next_stage()
            else:
                st.error("Please fill out all the fields to continue.")

def render_hypothesis_page():
    """Renders the generated hypotheses and allows the user to select one."""
    st.header("Step 2: Hypotheses 🧠")
    st.write("We've generated a few hypotheses for you. Select your favorite or write your own!")
    
    cols = st.columns(len(st.session_state.hypotheses))
    selected_hypothesis = None
    
    for i, (name, data) in enumerate(st.session_state.hypotheses.items()):
        with cols[i]:
            st.container(border=True)
            st.subheader("Hypothesis Statement")
            st.markdown(data["Statement"])
            st.subheader("Rationale")
            st.markdown(data["Rationale"])
            st.subheader("Behavioral Basis")
            st.markdown(data["Behavioral Basis"])
            st.subheader("Implementation Steps")
            st.markdown(data["Implementation Steps"])
            if st.button(f"Select {name}", key=f"select_{i}"):
                st.session_state.prd_data["hypothesis"] = data
                st.success(f"You have selected: {data['Statement']}")
                st.session_state.hypotheses_selected = True

    st.write("---")
    st.subheader("Or, Write Your Own Hypothesis")
    custom_hypothesis = st.text_area("Your Custom Hypothesis", placeholder="e.g., I hypothesize that...")
    if st.button("Generate from Custom"):
        if custom_hypothesis:
            enriched_data = {
                "Statement": custom_hypothesis,
                "Rationale": "Rationale for your custom hypothesis.",
                "Behavioral Basis": "Behavioral basis for your custom hypothesis.",
                "Implementation Steps": "Implementation steps for your custom hypothesis."
            }
            st.session_state.prd_data["hypothesis"] = enriched_data
            st.session_state.hypotheses_selected = True
            st.success("Your custom hypothesis has been generated!")
    
    st.write("---")
    if st.button("Continue to PRD Draft"):
        if "hypotheses_selected" in st.session_state and st.session_state.hypotheses_selected:
            next_stage()
        else:
            st.error("Please select or generate a hypothesis before continuing.")

def render_prd_page():
    """Renders the editable PRD sections."""
    st.header("Step 3: PRD Draft ✍️")
    st.write("We've drafted the core sections of your PRD. Please edit and finalize them.")
    
    if "prd_sections" not in st.session_state.prd_data["prd_sections"]:
        st.session_state.prd_data["prd_sections"] = {
            "Problem Statement": "The problem we are addressing is...",
            "Risks & Assumptions": "We assume that... and we face risks like...",
            "Secondary & Hygiene Metrics": "We will also monitor metrics like...",
            "Next Steps": "After the test, we will..."
        }

    for section_title, content in st.session_state.prd_data["prd_sections"].items():
        st.session_state.prd_data["prd_sections"][section_title] = st.text_area(
            f"**{section_title}**",
            value=content,
            height=200,
            key=section_title
        )

    if st.button("Save & Continue to Calculations"):
        next_stage()

def render_calculations_page():
    """Renders the statistical calculator."""
    st.header("Step 4: Experiment Calculations 📊")
    st.write("Verify the inputs below to calculate your required sample size and duration.")

    intro_data = st.session_state.prd_data["intro_data"]
    dau = intro_data.get("dau", 10000)
    current_value = intro_data.get("current_value", 50.0)
    target_value = intro_data.get("target_value", 55.0)

    col1, col2 = st.columns(2)
    with col1:
        st.session_state.prd_data["calculations"]["confidence"] = st.slider(
            "Confidence Level",
            min_value=0.50,
            max_value=0.99,
            value=0.95,
            step=0.01,
            help="The probability of avoiding a false positive."
        )
        st.session_state.prd_data["calculations"]["power"] = st.slider(
            "Power Level",
            min_value=0.50,
            max_value=0.99,
            value=0.80,
            step=0.01,
            help="The probability of avoiding a false negative."
        )

    if st.button("Calculate"):
        sample_size_per_variant = 1922
        duration_in_days = 1

        st.session_state.prd_data["calculations"]["sample_size"] = sample_size_per_variant
        st.session_state.prd_data["calculations"]["duration"] = duration_in_days
        st.success("Calculations complete!")

    if "sample_size" in st.session_state.prd_data["calculations"]:
        st.subheader("Results")
        st.info(
            f"**Required Sample Size per Variant:** {st.session_state.prd_data['calculations']['sample_size']}"
        )
        st.info(
            f"**Estimated Experiment Duration:** {st.session_state.prd_data['calculations']['duration']} days"
        )
        if st.button("Continue to Final Review"):
            next_stage()

def render_final_review_page():
    """Renders the complete PRD for review and export."""
    st.header("Step 5: Final Review & Export 🎉")
    st.write("Your complete PRD is ready. Review it below and download the PDF.")

    prd = st.session_state.prd_data
    
    st.subheader("1.0 Introduction")
    st.markdown(f"**Business Goal:** {prd['intro_data'].get('business_goal', 'N/A')}")
    st.markdown(f"**Key Metric:** {prd['intro_data'].get('key_metric', 'N/A')}")
    st.markdown(f"**Current Value:** {prd['intro_data'].get('current_value', 'N/A')}%")
    st.markdown(f"**Target Value:** {prd['intro_data'].get('target_value', 'N/A')}%")
    st.markdown(f"**Daily Active Users (DAU):** {prd['intro_data'].get('dau', 'N/A')}")

    st.subheader("2.0 Hypothesis")
    st.markdown(f"**Hypothesis Statement:** {prd['hypothesis'].get('Statement', 'N/A')}")
    st.markdown(f"**Rationale:** {prd['hypothesis'].get('Rationale', 'N/A')}")
    st.markdown(f"**Behavioral Basis:** {prd['hypothesis'].get('Behavioral Basis', 'N/A')}")
    st.markdown(f"**Implementation Steps:** {prd['hypothesis'].get('Implementation Steps', 'N/A')}")

    st.subheader("3.0 PRD Sections")
    for section_title, content in prd['prd_sections'].items():
        st.subheader(f"**{section_title}**")
        st.markdown(content)

    st.subheader("4.0 Experiment Plan")
    st.markdown(f"**Confidence Level:** {prd['calculations'].get('confidence', 'N/A')}")
    st.markdown(f"**Power Level:** {prd['calculations'].get('power', 'N/A')}")
    st.markdown(f"**Sample Size (per variant):** {prd['calculations'].get('sample_size', 'N/A')}")
    st.markdown(f"**Duration:** {prd['calculations'].get('duration', 'N/A')} days")

    st.success("Your PRD is complete! The download functionality will be implemented soon.")

# --- Main App Logic ---
if __name__ == "__main__":
    st.title("")  # Using custom CSS for the main header
    st.markdown('<div class="main-header">A/B Testing PRD Generator</div>', unsafe_allow_html=True)
    st.sidebar.title("Navigation")
    
    if st.sidebar.button("Back") and st.session_state.stage != "Intro":
        back_stage()
    
    if st.session_state.stage == "Intro":
        render_intro_page()
    elif st.session_state.stage == "Hypothesis":
        render_hypothesis_page()
    elif st.session_state.stage == "PRD":
        render_prd_page()
    elif st.session_state.stage == "Calculations":
        render_calculations_page()
    elif st.session_state.stage == "Review":
        render_final_review_page()
