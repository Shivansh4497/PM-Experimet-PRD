import streamlit as st
import pandas as pd
import re
from functools import partial
import streamlit.components.v1 as components

# Import functions from your utility files.
# Note: Ensure you have these utility files in a 'utils' folder.
# For this example, placeholder functions will be used if imports fail.

# --- Option Lists ---
business_goals = [
    "Increase retention",
    "Boost DAU",
    "Improve conversion",
    "Monetization growth"
]

product_areas = [
    "Onboarding",
    "Search",
    "Recommendations",
    "Payments",
    "Notifications"
]

metrics = [
    "DAU",
    "WAU",
    "Retention D30",
    "CTR",
    "Revenue per user"
]

try:
    from utils.api_handler import generate_content
    from utils.calculations import calculate_sample_size_proportion, calculate_sample_size_continuous, calculate_duration
    from utils.pdf_generator import create_pdf
except ImportError:
    # Define placeholder functions if utils are not available
    def generate_content(api_key, data, content_type):
        st.warning(f"Could not import 'generate_content'. Using placeholder data for {content_type}.")
        if content_type == "hypotheses":
            return {
                "Hypothesis 1": {"Statement": "Statement 1", "Rationale": "Rationale 1", "Behavioral Basis": "Basis 1"},
                "Hypothesis 2": {"Statement": "Statement 2", "Rationale": "Rationale 2", "Behavioral Basis": "Basis 2"},
            }
        if content_type == "enrich_hypothesis":
            return {"Statement": data.get("custom_hypothesis", ""), "Rationale": "Generated Rationale", "Behavioral Basis": "Generated Basis"}
        if content_type == "prd_sections":
            return {
                "Problem_Statement": "This is the generated problem statement.",
                "Goal_and_Success_Metrics": "This is the generated goal and success metrics section.",
                "Implementation_Plan": "- Step 1\n- Step 2"
            }
        if content_type == "risks":
            return {"risks": [{"risk": "A potential risk.", "mitigation": "A potential mitigation."}]}
        return {"error": "Content generation utility is not available."}

    def calculate_sample_size_proportion(current_value, min_detectable_effect, confidence, power):
        return 1000
    def calculate_sample_size_continuous(mean, std_dev, min_detectable_effect, confidence, power):
        return 1200
    def calculate_duration(sample_size, daily_active_users, coverage):
        return 14
    def create_pdf(prd_data):
        return b"This is a placeholder PDF."


try:
    from scipy.stats import norm
    CALCULATIONS_AVAILABLE = True
except ImportError as e:
    CALCULATIONS_AVAILABLE = False
    CALC_ERROR_MSG = str(e)

# Set the page layout to wide and hide the default sidebar
st.set_page_config(layout="wide", initial_sidebar_state="collapsed")

# --- Custom CSS for a Polished UI ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@400;700&display=swap');
    
    /* --- HIDE DEFAULT STREAMLIT UI --- */
    section[data-testid="stSidebar"] {
        display: none !important;
    }
    button[data-testid="stSidebarNavCollapseButton"] {
        display: none !important;
    }
    div[data-testid="stAppViewContainer"] {
        margin-top: -6rem; /* Adjust this value as needed */
    }
    /* --- APP HEADER STYLES --- */
    .app-header {
        text-align: center;
        padding: 1rem 0;
        margin-bottom: 1rem;
    }
    .app-header h1 {
        font-size: 2.5rem;
        font-weight: 700;
        color: #e0e0e0;
        margin: 0;
    }
    .app-header p {
        font-size: 1.1rem;
        color: #8b949e;
        margin: 0;
    }

    /* --- TOPBAR STYLES --- */
    .top-nav {
        display: flex;
        justify-content: center;
        align-items: center;
        padding: 10px 0;
        border-bottom: 1px solid #30363d;
        margin-bottom: 2rem;
    }
    .nav-button {
        background-color: transparent;
        border: 2px solid #30363d;
        color: #8b949e;
        font-weight: bold;
        padding: 8px 16px;
        margin: 0 5px;
        border-radius: 8px;
        text-align: center;
        white-space: nowrap;
    }
    .nav-button.complete-stage {
        border-color: #216d33;
        color: #c9d1d9;
    }
    .nav-button.active-stage {
        background-color: #216d33;
        color: white;
        border-color: #2ea043;
    }

    /* --- MOBILE TOPBAR STYLES --- */
    @media (max-width: 768px) {
        .top-nav {
            justify-content: flex-start;
            overflow-x: auto;
            -ms-overflow-style: none;
            scrollbar-width: none;
        }
        .top-nav::-webkit-scrollbar {
            display: none;
        }
    }
    
    /* --- GENERAL STYLES --- */
    html, body, [class*="st-"] {
        font-family: 'Roboto', sans-serif;
    }
    
    .main .block-container {
        padding-top: 0 !important;
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
    /* --- SUGGESTION BUTTON STYLES --- */
    .suggestion-buttons {
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
        margin-bottom: 1rem;
    }
    .suggestion-buttons .stButton > button {
        background-color: #21262d;
        border: 1px solid #30363d;
        font-size: 0.8rem;
        padding: 4px 10px;
        min-height: auto;
    }
    .suggestion-buttons .stButton > button:hover {
        border-color: #8b949e;
        color: #c9d1d9;
    }
    /* Additional restored styles */
    .st-emotion-cache-18ni7ap, .st-emotion-cache-1r6r8k {
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
        "calculations": {},
        "risks": []
    }
if "editing_section" not in st.session_state:
    st.session_state.editing_section = None
if "editing_risk" not in st.session_state:
    st.session_state.editing_risk = None
if "scroll_to_top" not in st.session_state:
    st.session_state.scroll_to_top = False


def scroll_to_top():
    """Injects JavaScript to scroll to the top of the page."""
    components.html(
        """
        <script>
            window.parent.scrollTo(0, 0);
        </script>
        """,
        height=0,
    )

# --- Helper & Callback Functions ---
def next_stage():
    """Navigates to the next stage in the process."""
    st.session_state.scroll_to_top = True
    st.session_state.editing_section = None
    st.session_state.editing_risk = None
    current_index = STAGES.index(st.session_state.stage)
    if current_index < len(STAGES) - 1:
        st.session_state.stage = STAGES[current_index + 1]
        st.rerun()



def set_stage(stage_name):
    """Sets the current stage directly."""
    st.session_state.scroll_to_top = True
    # This function is kept for potential future use but is not called by the non-interactive topbar.
    if stage_name in STAGES:
        st.session_state.stage = stage_name
        st.rerun()

def set_editing_section(section_title):
    """Sets the currently edited PRD section to trigger the modal."""
    st.session_state.editing_section = section_title
    st.session_state.editing_risk = None

def set_editing_risk(risk_index):
    """Sets the currently edited risk, clearing section editing."""
    st.session_state.editing_risk = risk_index
    st.session_state.editing_section = None

def save_edit(section_title):
    """Saves changes to a PRD section from its text area in the modal."""
    edited_text = st.session_state[f"text_area_{section_title}"]
    original_content = st.session_state.prd_data["prd_sections"][section_title]
    if isinstance(original_content, list):
        st.session_state.prd_data["prd_sections"][section_title] = [line.strip("- ").strip() for line in edited_text.split('\n') if line.strip()]
    else:
        st.session_state.prd_data["prd_sections"][section_title] = edited_text
    
    st.session_state.editing_section = None # Close the modal
    cleaned_label = str(section_title).replace("_", " ").title()
    st.success(f"Changes to '{cleaned_label}' saved!")

def save_risk_edit(risk_index):
    """Saves changes to a specific risk from the dialog."""
    edited_risk = st.session_state[f"text_area_risk_{risk_index}"]
    edited_mitigation = st.session_state[f"text_area_mitigation_{risk_index}"]
    st.session_state.prd_data["risks"][risk_index] = {
        "risk": edited_risk,
        "mitigation": edited_mitigation
    }
    st.session_state.editing_risk = None # Close the modal
    st.success(f"Changes to Risk {risk_index + 1} saved!")

def save_summary_edit():
    """Saves changes to the executive summary."""
    st.session_state.prd_data["intro_data"]["business_goal"] = st.session_state.summary_business_goal
    st.session_state.prd_data["hypothesis"]["Statement"] = st.session_state.summary_hypothesis
    st.session_state.prd_data["intro_data"]["user_persona"] = st.session_state.summary_user_persona
    st.session_state.prd_data["intro_data"]["app_description"] = st.session_state.summary_app_description
    st.session_state.editing_section = None # Close the modal
    st.success("Executive Summary updated!")

def format_content_for_display(content):
    """Formats list or string content for consistent Markdown display."""
    if isinstance(content, list):
        return "\n".join([f"- {item}" for item in content])
    else:
        return str(content)

@st.dialog("Edit Section")
def edit_section_dialog(section_title):
    """A dialog to edit a PRD section."""
    content = st.session_state.prd_data["prd_sections"][section_title]
    cleaned_label = section_title.replace("_", " ").title()
    
    st.text_area(
        f"Edit {cleaned_label}",
        value=format_content_for_display(content),
        height=300,
        key=f"text_area_{section_title}"
    )
    st.caption("You can use Markdown for formatting (e.g., **bold**, *italics*, - lists).")
    if st.button("Save Changes", key=f"save_dialog_{section_title}"):
        save_edit(section_title)
        st.rerun()

@st.dialog("Edit Risk")
def edit_risk_dialog(risk_index):
    """A dialog to edit a risk and its mitigation."""
    risk_item = st.session_state.prd_data["risks"][risk_index]
    
    st.text_area("Risk", value=risk_item['risk'], height=100, key=f"text_area_risk_{risk_index}")
    st.text_area("Mitigation", value=risk_item['mitigation'], height=100, key=f"text_area_mitigation_{risk_index}")

    if st.button("Save Changes", key=f"save_dialog_risk_{risk_index}"):
        save_risk_edit(risk_index)
        st.rerun()

@st.dialog("Edit Executive Summary")
def edit_summary_dialog():
    """A dialog to edit the executive summary fields."""
    prd = st.session_state.prd_data
    st.text_input("Business Goal", value=prd['intro_data'].get('business_goal', ''), key="summary_business_goal")
    st.text_area("Hypothesis", value=prd['hypothesis'].get('Statement', ''), key="summary_hypothesis")
    st.text_area("Target User Persona (Optional)", value=prd['intro_data'].get('user_persona', ''), key="summary_user_persona")
    st.text_area("App Description (Optional)", value=prd['intro_data'].get('app_description', ''), key="summary_app_description")
    if st.button("Save Changes", key="save_summary_dialog"):
        save_summary_edit()
        st.rerun()

# --- UI Rendering Functions ---

def render_header():
    """Renders the main application header."""
    st.markdown("""
        <div class="app-header">
            <h1>A/B Test PRD Generator</h1>
            <p>Create AI Powered Product Requirement Documents for your experiments.</p>
        </div>
    """, unsafe_allow_html=True)

def render_topbar():
    """Renders the horizontal top navigation bar as a non-interactive progress indicator."""
    current_stage_index = STAGES.index(st.session_state.stage)
    
    button_html_list = []
    for i, stage in enumerate(STAGES):
        class_list = "nav-button"
        if i == current_stage_index:
            class_list += " active-stage"
        elif i < current_stage_index:
            class_list += " complete-stage"
        
        button_html_list.append(f'<div class="{class_list}">{stage}</div>')
        
    all_buttons_html = "".join(button_html_list)
    top_nav_html = f'<div class="top-nav">{all_buttons_html}</div>'
    
    st.markdown(top_nav_html, unsafe_allow_html=True)


def render_intro_page():
    st.header("Step 1: The Basics 📝")
    st.info("""
        **Welcome!** Let's start by gathering some high-level details about your A/B test. 
        The more context you provide, the better the generated hypotheses and PRD will be.
    """)
    
    if "GROQ_API_KEY" not in st.secrets:
        st.error("Groq API key not found. Please add it to your Streamlit secrets to run this app.")
        st.stop()

    def process_intro_form():
        """Callback to process the intro form, generate hypotheses, and move to the next stage."""
        # Safely get values from session_state
        # Safely get values from session_state
        st.session_state.prd_data["intro_data"]["business_goal"] = st.session_state.intro_business_goal
        st.session_state.prd_data["intro_data"]["key_metric"] = st.session_state.intro_key_metric
        st.session_state.prd_data["intro_data"]["product_area"] = st.session_state.intro_product_area
        st.session_state.prd_data["intro_data"]["metric_type"] = st.session_state.intro_metric_type
        st.session_state.prd_data["intro_data"]["current_value"] = st.session_state.intro_current_value
        st.session_state.prd_data["intro_data"]["target_value"] = st.session_state.intro_target_value
        st.session_state.prd_data["intro_data"]["dau"] = st.session_state.intro_dau
        st.session_state.prd_data["intro_data"]["product_type"] = st.session_state.intro_product_type
        st.session_state.prd_data["intro_data"]["user_persona"] = st.session_state.intro_user_persona
        st.session_state.prd_data["intro_data"]["app_description"] = st.session_state.intro_app_description
        
        if st.session_state.get("intro_metric_type") == "Continuous":
            st.session_state.prd_data["intro_data"]["std_dev"] = st.session_state.get("intro_std_dev")
        
        required_fields = ["business_goal", "key_metric", "metric_type", "current_value", "product_area", "target_value", "dau", "product_type"]
        if st.session_state.prd_data["intro_data"]["metric_type"] == "Continuous":
            required_fields.append("std_dev")

        if all(st.session_state.prd_data["intro_data"].get(field) for field in required_fields):
            with st.spinner("Generating hypotheses..."):
                hypotheses = generate_content(st.secrets["GROQ_API_KEY"], st.session_state.prd_data["intro_data"], "hypotheses")
                if "error" in hypotheses:
                    st.error(hypotheses["error"])
                else:
                    st.session_state.hypotheses = hypotheses
                    next_stage()
        else:
            st.error("Please fill out all the fields to continue.")
    def suggestion_buttons(options, text_key):
        st.markdown('<div class="suggestion-buttons">', unsafe_allow_html=True)
        cols = st.columns(len(options))
        for i, option in enumerate(options):
            with cols[i]:
                if st.button(option, key=f"{text_key}_{option}"):
                    st.session_state[text_key] = option
                    st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)



        st.subheader("Business & Product Details")
        col1, col2 = st.columns(2)
        with col1:
            st.text_input("Business Goal", key="intro_business_goal")
            business_goals = ["Increase user engagement", "Improve user retention", "Increase revenue"]
            suggestion_buttons(business_goals, "intro_business_goal")

            st.text_input("Key Metric", key="intro_key_metric")
            key_metrics = ["Login Rate", "ARPDAU", "Conversion Rate", "Click-Through Rate"]
            suggestion_buttons(key_metrics, "intro_key_metric")

            st.selectbox("Metric Type", ["Proportion", "Continuous"], key="intro_metric_type", help="Proportion metrics are percentages (e.g., Conversion Rate). Continuous metrics are numerical averages (e.g., ARPDAU).")
            st.number_input("Current Metric Value", min_value=0.0, value=50.0, key="intro_current_value")
            
            if st.session_state.get("intro_metric_type") == "Continuous":
                st.number_input("Standard Deviation", min_value=0.0, value=10.0, key="intro_std_dev", help="The standard deviation of your metric.")
        with col2:
            st.text_input("Product Area", key="intro_product_area")
            product_areas = ["Mobile App Onboarding", "Web App Dashboard", "E-commerce Checkout"]
            suggestion_buttons(product_areas, "intro_product_area")

            st.number_input("Target Metric Value", min_value=0.0, value=55.0, key="intro_target_value")
            st.number_input("Daily Active Users (DAU)", min_value=100, value=10000, key="intro_dau")
            st.selectbox("Product Type", ["SaaS Product", "Mobile App", "Web Platform", "Other"], index=1, key="intro_product_type")

        st.subheader("Optional Context")
        st.text_area("Target User Persona (Optional)", placeholder="e.g., Tech-savvy millennials...", key="intro_user_persona")
        st.text_area("App Description (Optional)", placeholder="e.g., A mobile app for tracking water intake...", key="intro_app_description")

        if st.button("Generate Hypotheses", on_click=process_intro_form):
            pass

def render_hypothesis_page():
    st.header("Step 2: Hypotheses 🧠")
    st.info("""
        A hypothesis is a clear, testable statement about the expected outcome. We've generated a few for you below.
    """)

    def select_hypothesis(hypothesis_data):
        st.session_state.prd_data["hypothesis"] = hypothesis_data
        st.session_state.hypotheses_selected = True
        st.success(f"You have selected: {hypothesis_data['Statement']}")
        next_stage()

    def generate_from_custom():
        custom_hypothesis = st.session_state.get("custom_hypothesis_input", "")
        if not custom_hypothesis:
            st.error("Please write a custom hypothesis first.")
            return

        with st.spinner("Generating from custom hypothesis..."):
            context = {"custom_hypothesis": custom_hypothesis, **st.session_state.prd_data["intro_data"]}
            enriched_data = generate_content(st.secrets["GROQ_API_KEY"], context, "enrich_hypothesis")
            if "error" in enriched_data:
                st.error(enriched_data["error"])
            else:
                st.session_state.custom_hypothesis_generated = enriched_data
                st.success("Your custom hypothesis has been generated!")

    def lock_custom_hypothesis():
        enriched = st.session_state.get("custom_hypothesis_generated")
        if enriched:
            st.session_state.prd_data["hypothesis"] = enriched
            st.session_state.hypotheses_selected = True
            st.success("Custom hypothesis locked!")
            next_stage()

    st.subheader("Write Your Own Hypothesis")
    st.text_area("Your Custom Hypothesis", placeholder="e.g., I hypothesize that...", key="custom_hypothesis_input")
    st.button("Generate from Custom", on_click=generate_from_custom, key="gen_custom_btn")

    if "custom_hypothesis_generated" in st.session_state:
        st.subheader("Generated Hypothesis Details")
        enriched = st.session_state.custom_hypothesis_generated
        st.markdown(f"**Statement:** {enriched.get('Statement', 'N/A')}")
        st.markdown(f"**Rationale:** {enriched.get('Rationale', 'N/A')}")
        st.markdown(f"**Behavioral Basis:** {enriched.get('Behavioral Basis', 'N/A')}")
        st.button("Lock This Hypothesis & Continue", on_click=lock_custom_hypothesis, key="lock_custom_btn")

    st.write("---")
    
    st.subheader("Or, Select from our suggestions")
    if 'hypotheses' in st.session_state and isinstance(st.session_state.hypotheses, dict):
        cols = st.columns(len(st.session_state.hypotheses))
        for i, (name, data) in enumerate(st.session_state.hypotheses.items()):
            with cols[i]:
                with st.container(border=True):
                    st.subheader(f"Hypothesis {i+1}")
                    st.markdown(f"**Statement:** {data.get('Statement', 'N/A')}")
                    st.markdown(f"**Rationale:** {data.get('Rationale', 'N/A')}")
                    st.markdown(f"**Behavioral Basis:** {data.get('Behavioral Basis', 'N/A')}")

                    st.button(f"Select & Continue", key=f"select_{i}", on_click=select_hypothesis, args=(data,))


def render_prd_page():
    st.header("Step 3: PRD Draft ✍️")
    st.info("We've drafted the core sections of your PRD. Please review, edit, and finalize them.")
    
    if not st.session_state.prd_data.get("prd_sections"):
        with st.spinner("Drafting PRD sections..."):
            prd_context = {**st.session_state.prd_data["intro_data"], **st.session_state.prd_data["hypothesis"]}
            raw_prd_sections = generate_content(st.secrets["GROQ_API_KEY"], prd_context, "prd_sections")
            if "error" in raw_prd_sections:
                st.error(raw_prd_sections["error"])
            else:
                st.session_state.prd_data["prd_sections"] = raw_prd_sections

    prd_sections = st.session_state.prd_data.get("prd_sections", {})
    for key, content in prd_sections.items():
        cleaned_label = key.replace("_", " ").title()
        if st.session_state.editing_section == key:
            edit_section_dialog(key)
        with st.container(border=True):
            col1, col2 = st.columns([10, 1])
            with col1:
                 st.subheader(f"**{cleaned_label}**")
            with col2:
                st.button("✏️", key=f"edit_{key}", on_click=set_editing_section, args=(key,))
            st.markdown(format_content_for_display(content))

    st.write("---")
    st.button("Save & Continue to Calculations", on_click=next_stage, key="to_calcs")


def render_calculations_page():
    st.header("Step 4: Experiment Calculations 📊")
    st.info("""
        Verify the inputs below to calculate your required sample size and duration.
    """)

    intro_data = st.session_state.prd_data["intro_data"]
    dau = intro_data.get("dau", 10000)
    current_value = intro_data.get("current_value", 50.0)
    metric_type = intro_data.get("metric_type", "Proportion")

    st.subheader("Key Metrics")
    st.markdown(f"**Key Metric:** {intro_data.get('key_metric', 'N/A')}")
    st.markdown(f"**Metric Type:** {metric_type}")
    st.markdown(f"**Current Value:** {current_value}")
    if metric_type == "Continuous":
        st.markdown(f"**Standard Deviation:** {intro_data.get('std_dev', 'N/A')}")

    st.subheader("Experiment Parameters")
    st.slider("Confidence Level (%)", 50, 99, 95, 1, key="calc_confidence")
    st.slider("Power Level (%)", 50, 99, 80, 1, key="calc_power")
    st.slider("Coverage (%)", 5, 100, 50, 5, key="calc_coverage")
    st.number_input("Minimum Detectable Effect (%)", min_value=0.1, value=5.0, step=0.1, key="calc_mde")

    def perform_calculations():
        try:
            st.session_state.prd_data["calculations"]["confidence"] = st.session_state.calc_confidence / 100
            st.session_state.prd_data["calculations"]["power"] = st.session_state.calc_power / 100
            st.session_state.prd_data["calculations"]["coverage"] = st.session_state.calc_coverage
            st.session_state.prd_data["calculations"]["min_detectable_effect"] = st.session_state.calc_mde

            if metric_type == "Proportion":
                sample_size = calculate_sample_size_proportion(current_value, st.session_state.calc_mde, st.session_state.calc_confidence / 100, st.session_state.calc_power / 100)
            else:
                sample_size = calculate_sample_size_continuous(current_value, intro_data.get("std_dev"), st.session_state.calc_mde, st.session_state.calc_confidence / 100, st.session_state.calc_power / 100)
            
            duration = calculate_duration(sample_size, dau, st.session_state.calc_coverage)
            st.session_state.prd_data["calculations"]["sample_size"] = sample_size
            st.session_state.prd_data["calculations"]["duration"] = duration
            st.success("Calculations complete!")
        except Exception as e:
            st.error(f"Error in calculations: {e}")

    st.button("Calculate", on_click=perform_calculations, key="calc_btn")

    if "sample_size" in st.session_state.prd_data["calculations"]:
        st.subheader("Results")
        sample_size = st.session_state.prd_data['calculations']['sample_size']
        duration = st.session_state.prd_data['calculations']['duration']
        st.info(f"**Required Sample Size per Variant:** {sample_size:,}")
        st.info(f"**Estimated Experiment Duration:** {duration} days")
        st.button("Continue to Final Review", on_click=next_stage, key="to_review")


def render_final_review_page():
    st.header("Step 5: Final Review & Export 🎉")
    st.info("Your complete PRD is ready. Review, polish, and export.")

    prd = st.session_state.prd_data

    if st.session_state.editing_section == "executive_summary":
        edit_summary_dialog()

    with st.container(border=True):
        col1, col2 = st.columns([10, 1])
        with col1:
            st.subheader("🚀 Executive Summary")
        with col2:
            st.button("✏️", key="edit_summary", on_click=set_editing_section, args=("executive_summary",))
        
        st.markdown(f"**Business Goal:** {prd['intro_data'].get('business_goal', 'N/A')}")
        st.markdown(f"**Hypothesis:** {prd['hypothesis'].get('Statement', 'N/A')}")
        st.markdown(f"**Success Criteria:** Target {prd['intro_data'].get('key_metric', 'N/A')} → {prd['intro_data'].get('target_value', 'N/A')}")
        if prd['intro_data'].get('user_persona'):
            st.markdown(f"**Target User Persona:** {prd['intro_data']['user_persona']}")

    st.subheader("PRD Sections")
    for key, content in prd.get('prd_sections', {}).items():
        display_label = key.replace("_", " ").title()
        if st.session_state.editing_section == key:
            edit_section_dialog(key)
        with st.container(border=True):
            col1, col2 = st.columns([10, 1])
            with col1:
                st.subheader(display_label)
            with col2:
                st.button("✏️", key=f"edit_review_{key}", on_click=set_editing_section, args=(key,))
            st.markdown(format_content_for_display(content))

    with st.container(border=True):
        st.subheader("Experiment Metrics Dashboard 📊")
        cols = st.columns(3)
        cols[0].metric("Confidence", f"{int(prd['calculations'].get('confidence', 0)*100)}%")
        cols[1].metric("Power", f"{int(prd['calculations'].get('power', 0)*100)}%")
        cols[2].metric("Min. Detectable Effect", f"{prd['calculations'].get('min_detectable_effect', 'N/A')}%")
        cols[0].metric("Target Value", f"{prd['intro_data'].get('target_value', 'N/A')}")
        cols[1].metric("Sample Size", f"{prd['calculations'].get('sample_size', 'N/A'):,}", "per variant")
        cols[2].metric("Duration", f"{prd['calculations'].get('duration', 'N/A')} days")

    with st.container(border=True):
        st.subheader("Risks & Next Steps ⚠️")

        def generate_risks():
            with st.spinner("Generating contextual risks..."):
                risk_data = {**prd['intro_data'], "hypothesis": prd['hypothesis'].get('Statement')}
                generated_risks = generate_content(st.secrets["GROQ_API_KEY"], risk_data, "risks")
                if "error" in generated_risks:
                    st.error(generated_risks["error"])
                else:
                    st.session_state.prd_data["risks"] = generated_risks.get("risks", [])
        
        st.button("Generate Risks & Next Steps", on_click=generate_risks)

        for i, r in enumerate(st.session_state.prd_data.get("risks", [])):
            if st.session_state.editing_risk == i:
                edit_risk_dialog(i)
            with st.container(border=True):
                col1, col2 = st.columns([10, 1])
                with col1:
                    st.subheader(f"Risk {i+1}")
                    st.markdown(f"**Description:** {r['risk']}")
                    st.markdown(f"**Mitigation:** {r['mitigation']}")
                with col2:
                    st.button("✏️", key=f"edit_risk_{i}", on_click=set_editing_risk, args=(i,))

    if st.session_state.prd_data.get("risks"):
        st.subheader("Download PRD")
        pdf_bytes = create_pdf(prd)
        st.download_button("📥 Download PRD as PDF", pdf_bytes, "AB_Testing_PRD.pdf", "application/pdf")


# --- Main Rendering Logic ---
render_header()
render_topbar()

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

if st.session_state.get("scroll_to_top"):
    scroll_to_top()
    st.session_state.scroll_to_top = False # Reset the flag