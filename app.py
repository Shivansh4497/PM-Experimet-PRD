import streamlit as st
import pandas as pd
import re
from functools import partial

# Import functions from your utility files.
# Note: Ensure you have these utility files in a 'utils' folder.
# For this example, placeholder functions will be used if imports fail.
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
            return {"Statement": data, "Rationale": "Generated Rationale", "Behavioral Basis": "Generated Basis"}
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


# --- Custom CSS for a Polished UI ---
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
        "calculations": {},
        "risks": []
    }
if "editing_section" not in st.session_state:
    st.session_state.editing_section = None
if "editing_risk" not in st.session_state:
    st.session_state.editing_risk = None


# --- Helper & Callback Functions ---
def next_stage():
    """Navigates to the next stage in the process."""
    current_index = STAGES.index(st.session_state.stage)
    if current_index < len(STAGES) - 1:
        st.session_state.stage = STAGES[current_index + 1]

def back_stage():
    """Navigates to the previous stage in the process."""
    current_index = STAGES.index(st.session_state.stage)
    if current_index > 0:
        st.session_state.stage = STAGES[current_index - 1]

def set_stage(stage_name):
    """Sets the current stage directly."""
    if stage_name in STAGES:
        st.session_state.stage = stage_name

def set_editing_section(section_title):
    """Sets the currently edited PRD section, clearing risk editing."""
    st.session_state.editing_section = section_title
    st.session_state.editing_risk = None

def set_editing_risk(risk_index):
    """Sets the currently edited risk, clearing section editing."""
    st.session_state.editing_risk = risk_index
    st.session_state.editing_section = None

def save_edit(section_title):
    """Saves changes to a PRD section from its text area."""
    edited_text = st.session_state[f"text_area_{section_title}"]
    original_content = st.session_state.prd_data["prd_sections"][section_title]
    if isinstance(original_content, list):
        st.session_state.prd_data["prd_sections"][section_title] = [line.strip("- ").strip() for line in edited_text.split('\n') if line.strip()]
    else:
        st.session_state.prd_data["prd_sections"][section_title] = edited_text
    
    st.session_state.editing_section = None
    cleaned_label = str(section_title).replace("_", " ").title()
    st.success(f"Changes to '{cleaned_label}' saved!")

def save_review_edit(section_title):
    """Saves changes to a PRD section from the review page."""
    edited_text = st.session_state[f"text_area_review_{section_title}"]
    save_edit(section_title) # Re-use the main save logic

def save_risk_edit(risk_index, edited_risk, edited_mitigation):
    """Saves changes to a specific risk."""
    st.session_state.prd_data["risks"][risk_index] = {
        "risk": edited_risk,
        "mitigation": edited_mitigation
    }
    st.session_state.editing_risk = None
    st.success(f"Changes to Risk {risk_index + 1} saved!")

def format_content_for_display(content):
    """Formats list or string content for consistent Markdown display."""
    if isinstance(content, list):
        return "\n".join([f"- {item}" for item in content])
    else:
        return str(content)

# --- UI Rendering Functions ---

def render_intro_page():
    st.header("Step 1: The Basics 📝")
    st.write("Please provide some high-level details about your A/B test.")
    
    st.session_state.api_key = st.text_input("Enter your Groq API Key", type="password", key="api_key_input")

    def process_intro_form():
        """Callback to process the intro form, generate hypotheses, and move to the next stage."""
        if not st.session_state.api_key:
            st.error("Please provide your Groq API Key to proceed.")
            return

        # Log data to session state from form fields
        st.session_state.prd_data["intro_data"]["business_goal"] = st.session_state.intro_business_goal
        st.session_state.prd_data["intro_data"]["key_metric"] = st.session_state.intro_key_metric
        st.session_state.prd_data["intro_data"]["metric_type"] = st.session_state.intro_metric_type
        st.session_state.prd_data["intro_data"]["current_value"] = st.session_state.intro_current_value
        st.session_state.prd_data["intro_data"]["product_area"] = st.session_state.intro_product_area
        st.session_state.prd_data["intro_data"]["target_value"] = st.session_state.intro_target_value
        st.session_state.prd_data["intro_data"]["dau"] = st.session_state.intro_dau
        st.session_state.prd_data["intro_data"]["product_type"] = st.session_state.intro_product_type
        if st.session_state.intro_metric_type == "Continuous":
            st.session_state.prd_data["intro_data"]["std_dev"] = st.session_state.intro_std_dev
        
        required_fields = ["business_goal", "key_metric", "metric_type", "current_value", "product_area", "target_value", "dau", "product_type"]
        if st.session_state.prd_data["intro_data"]["metric_type"] == "Continuous":
            required_fields.append("std_dev")

        if all(st.session_state.prd_data["intro_data"].get(field) is not None and st.session_state.prd_data["intro_data"].get(field) != "" for field in required_fields):
            with st.spinner("Generating hypotheses..."):
                hypotheses = generate_content(
                    st.session_state.api_key,
                    st.session_state.prd_data["intro_data"],
                    "hypotheses"
                )
                if "error" in hypotheses:
                    st.error(hypotheses["error"])
                else:
                    st.session_state.hypotheses = hypotheses
                    next_stage()
        else:
            st.error("Please fill out all the fields to continue.")

    with st.form("intro_form"):
        st.subheader("Business & Product Details")
        col1, col2 = st.columns(2)
        with col1:
            st.text_input("Business Goal", placeholder="e.g., Increase user engagement", key="intro_business_goal")
            st.text_input("Key Metric", placeholder="e.g., Login Rate, ARPDAU", key="intro_key_metric")
            st.selectbox("Metric Type", ["Proportion", "Continuous"], help="Proportion for percentages (e.g., CTR), Continuous for averages (e.g., ARPDAU).", key="intro_metric_type")
            st.number_input("Current Metric Value", min_value=0.0, value=50.0, help="The current value of your key metric.", key="intro_current_value")
            if st.session_state.intro_metric_type == "Continuous":
                st.number_input("Standard Deviation", min_value=0.0, value=10.0, help="The standard deviation of your key metric.", key="intro_std_dev")

        with col2:
            st.text_input("Product Area", placeholder="e.g., Mobile App Onboarding", key="intro_product_area")
            st.number_input("Target Metric Value", min_value=0.0, value=55.0, help="The value you are aiming for.", key="intro_target_value")
            st.number_input("Daily Active Users (DAU)", min_value=100, value=10000, help="The total number of unique users daily.", key="intro_dau")
            st.selectbox("Product Type", ["SaaS Product", "Mobile App", "Web Platform", "Other"], index=1, key="intro_product_type")

        st.form_submit_button("Generate Hypotheses", on_click=process_intro_form)


def render_hypothesis_page():
    st.header("Step 2: Hypotheses 🧠")
    st.write("We've generated a few hypotheses for you. Select your favorite or write your own!")

    def select_hypothesis(hypothesis_data):
        """Callback to select a generated hypothesis and immediately move to the next stage."""
        st.session_state.prd_data["hypothesis"] = hypothesis_data
        st.session_state.hypotheses_selected = True
        st.success(f"You have selected: {hypothesis_data['Statement']}")
        next_stage() # Immediately go to the next stage

    def generate_from_custom():
        """Callback to generate an enriched hypothesis from custom user input."""
        custom_hypothesis = st.session_state.get("custom_hypothesis_input", "")
        if not st.session_state.api_key:
            st.error("Please provide your Groq API Key to proceed.")
        elif custom_hypothesis:
            with st.spinner("Generating from custom hypothesis..."):
                enriched_data = generate_content(
                    st.session_state.api_key,
                    custom_hypothesis,
                    "enrich_hypothesis"
                )
                if "error" in enriched_data:
                    st.error(enriched_data["error"])
                else:
                    st.session_state.custom_hypothesis_generated = enriched_data
                    st.success("Your custom hypothesis has been generated! Please review below.")
        else:
            st.error("Please write a custom hypothesis first.")

    def lock_custom_hypothesis():
        """Callback to lock in the generated custom hypothesis."""
        enriched = st.session_state.get("custom_hypothesis_generated")
        if enriched:
            st.session_state.prd_data["hypothesis"] = enriched
            st.session_state.hypotheses_selected = True
            st.success("Custom hypothesis locked!")

    def continue_to_prd():
        """Callback to proceed to the PRD stage after selection."""
        if st.session_state.get("hypotheses_selected", False):
            next_stage()
        else:
            st.error("Please select or generate a hypothesis before continuing.")

    if 'hypotheses' in st.session_state and isinstance(st.session_state.hypotheses, dict):
        cols = st.columns(len(st.session_state.hypotheses))
        for i, (name, data) in enumerate(st.session_state.hypotheses.items()):
            with cols[i]:
                with st.container(border=True):
                    st.subheader("Hypothesis Statement")
                    st.markdown(data.get("Statement", "N/A"))
                    st.subheader("Rationale")
                    st.markdown(data.get("Rationale", "N/A"))
                    st.subheader("Behavioral Basis")
                    st.markdown(data.get("Behavioral Basis", "N/A"))
                    st.button(f"Select {name}", key=f"select_{i}", on_click=select_hypothesis, args=(data,))

    st.write("---")
    st.subheader("Or, Write Your Own Hypothesis")
    st.text_area("Your Custom Hypothesis", placeholder="e.g., I hypothesize that...", key="custom_hypothesis_input")
    st.button("Generate from Custom", on_click=generate_from_custom, key="gen_custom_btn")

    if "custom_hypothesis_generated" in st.session_state:
        st.subheader("Generated Hypothesis Details")
        enriched = st.session_state.custom_hypothesis_generated
        st.markdown(f"**Statement:** {enriched.get('Statement', 'N/A')}")
        st.markdown(f"**Rationale:** {enriched.get('Rationale', 'N/A')}")
        st.markdown(f"**Behavioral Basis:** {enriched.get('Behavioral Basis', 'N/A')}")
        st.button("Lock This Hypothesis", on_click=lock_custom_hypothesis, key="lock_custom_btn")
        st.button("Continue to PRD Draft", on_click=continue_to_prd, key="continue_prd_btn")


def render_prd_page():
    st.header("Step 3: PRD Draft ✍️")
    st.write("We've drafted the core sections of your PRD. Please edit and finalize them.")
    
    if "prd_sections" not in st.session_state.prd_data or not st.session_state.prd_data["prd_sections"]:
        with st.spinner("Drafting PRD sections..."):
            raw_prd_sections = generate_content(
                st.session_state.api_key,
                st.session_state.prd_data["hypothesis"],
                "prd_sections"
            )
            if "error" in raw_prd_sections:
                st.error(raw_prd_sections["error"])
            else:
                # A more robust way to map potentially mislabeled keys
                clean_prd_sections = {}
                key_map = {
                    "problem": "Problem_Statement", "problem_statement": "Problem_Statement",
                    "goal": "Goal_and_Success_Metrics", "goal_and_success_metrics": "Goal_and_Success_Metrics",
                    "plan": "Implementation_Plan", "implementation_plan": "Implementation_Plan"
                }
                for raw_key, value in raw_prd_sections.items():
                    clean_key = key_map.get(raw_key.lower().replace(" ", "_"))
                    if clean_key:
                        clean_prd_sections[clean_key] = value
                st.session_state.prd_data["prd_sections"] = clean_prd_sections
                st.session_state.editing_section = None

    ordered_keys = ["Problem_Statement", "Goal_and_Success_Metrics", "Implementation_Plan"]
    prd_sections = st.session_state.prd_data.get("prd_sections", {})

    for key in ordered_keys:
        if key in prd_sections:
            content = prd_sections[key]
            cleaned_label = key.replace("_", " ").title()
            with st.container(border=True):
                col1, col2 = st.columns([10, 1])
                with col1:
                     st.subheader(f"**{cleaned_label}**")
                with col2:
                    st.button("✏️", key=f"edit_{key}", on_click=set_editing_section, args=(key,))
                
                if st.session_state.editing_section != key:
                    st.markdown(format_content_for_display(content))
                else:
                    st.text_area(
                        f"Edit {cleaned_label}",
                        value=format_content_for_display(content),
                        height=300,
                        key=f"text_area_{key}"
                    )
                    st.caption("You can use Markdown for formatting (e.g., **bold**, *italics*, - lists).")
                    st.button("Save Changes", key=f"save_{key}", on_click=save_edit, args=(key,))

    st.write("---")
    st.button("Save & Continue to Calculations", on_click=next_stage, key="to_calcs")


def render_calculations_page():
    if not CALCULATIONS_AVAILABLE:
        st.error(f"⚠️ Experiment calculations are unavailable. Dependency error: {CALC_ERROR_MSG}")
        return
    st.header("Step 4: Experiment Calculations 📊")
    st.write("Verify the inputs below to calculate your required sample size and duration.")

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
    st.number_input("Minimum Detectable Effect (%)", min_value=0.1, value=5.0, step=0.1, help="The relative percentage lift you want to be able to detect.", key="calc_mde")

    def perform_calculations():
        """Callback to run sample size and duration calculations."""
        try:
            # Log data from widgets to session state
            st.session_state.prd_data["calculations"]["confidence"] = st.session_state.calc_confidence / 100
            st.session_state.prd_data["calculations"]["power"] = st.session_state.calc_power / 100
            st.session_state.prd_data["calculations"]["coverage"] = st.session_state.calc_coverage
            st.session_state.prd_data["calculations"]["min_detectable_effect"] = st.session_state.calc_mde

            if metric_type == "Proportion":
                sample_size_per_variant = calculate_sample_size_proportion(
                    current_value=current_value,
                    min_detectable_effect=st.session_state.calc_mde,
                    confidence=st.session_state.calc_confidence / 100,
                    power=st.session_state.calc_power / 100
                )
            else: # Continuous
                sample_size_per_variant = calculate_sample_size_continuous(
                    mean=current_value,
                    std_dev=intro_data.get("std_dev"),
                    min_detectable_effect=st.session_state.calc_mde,
                    confidence=st.session_state.calc_confidence / 100,
                    power=st.session_state.calc_power / 100
                )
            
            duration_in_days = calculate_duration(
                sample_size=sample_size_per_variant,
                daily_active_users=dau,
                coverage=st.session_state.calc_coverage
            )
            st.session_state.prd_data["calculations"]["sample_size"] = sample_size_per_variant
            st.session_state.prd_data["calculations"]["duration"] = duration_in_days
            st.success("Calculations complete!")
        except Exception as e:
            st.error(f"Error in calculations: {e}")

    st.button("Calculate", on_click=perform_calculations, key="calc_btn")

    if "sample_size" in st.session_state.prd_data["calculations"]:
        st.subheader("Results")
        sample_size = st.session_state.prd_data['calculations']['sample_size']
        duration = st.session_state.prd_data['calculations']['duration']
        st.info(f"**Required Sample Size per Variant:** {sample_size:,}" if isinstance(sample_size, int) else "Calculation Error")
        st.info(f"**Estimated Experiment Duration:** {duration} days" if isinstance(duration, int) else "Calculation Error")
        st.button("Continue to Final Review", on_click=next_stage, key="to_review")


def render_final_review_page():
    st.header("Step 5: Final Review & Export 🎉")
    st.write("Your complete PRD is ready. Review, polish, and export.")

    prd = st.session_state.prd_data

    # --- Section 1: Executive Summary ---
    with st.container(border=True):
        st.subheader("🚀 Executive Summary")
        st.markdown(f"**Business Goal:** {prd['intro_data'].get('business_goal', 'N/A')}")
        st.markdown(f"**Hypothesis:** {prd['hypothesis'].get('Statement', 'N/A')}")
        st.markdown(f"**Success Criteria:** Target {prd['intro_data'].get('key_metric', 'N/A')} → {prd['intro_data'].get('target_value', 'N/A')}")

    # --- Section 2: PRD Sections ---
    st.subheader("PRD Sections")
    prd_sections = prd.get('prd_sections', {})
    if not prd_sections:
        st.info("No PRD sections generated yet.")
    else:
        ordered_keys = ["Problem_Statement", "Goal_and_Success_Metrics", "Implementation_Plan"]
        for key in ordered_keys:
            if key in prd_sections:
                content = prd_sections[key]
                display_label = key.replace("_", " ").title()
                
                with st.container(border=True):
                    col1, col2 = st.columns([10, 1])
                    with col1:
                        st.subheader(display_label)
                    with col2:
                        st.button("✏️", key=f"edit_review_{key}", on_click=set_editing_section, args=(key,))
                    
                    if st.session_state.editing_section == key:
                        st.text_area(
                            f"Edit {display_label}", 
                            value=format_content_for_display(content), 
                            height=300, 
                            key=f"text_area_{key}" # Re-use key to link to save function
                        )
                        st.caption("You can use Markdown for formatting (e.g., **bold**, *italics*, - lists).")
                        st.button("Save Changes", key=f"save_review_{key}", on_click=save_edit, args=(key,))
                    else:
                        st.markdown(format_content_for_display(content))

    # --- Section 3: Experiment Metrics Dashboard ---
    with st.container(border=True):
        st.subheader("Experiment Metrics Dashboard 📊")
        metrics_cols = st.columns(4)
        metrics_cols[0].metric("Confidence", f"{int(prd['calculations'].get('confidence', 0)*100)}%")
        metrics_cols[1].metric("Power", f"{int(prd['calculations'].get('power', 0)*100)}%")
        sample_size = prd['calculations'].get('sample_size', 'N/A')
        sample_size_str = f"{sample_size:,}" if isinstance(sample_size, int) else "N/A"
        metrics_cols[2].metric("Sample Size", sample_size_str, "↑ per variant")
        metrics_cols[3].metric("Duration", f"{prd['calculations'].get('duration', 'N/A')} days")

    # --- Section 4: Risks & Next Steps ---
    with st.container(border=True):
        st.subheader("Risks & Next Steps ⚠️")

        def generate_risks():
            """Callback to generate risks and next steps."""
            with st.spinner("Generating contextual risks..."):
                risk_data = {
                    "business_goal": prd['intro_data'].get('business_goal'),
                    "hypothesis": prd['hypothesis'].get('Statement')
                }
                generated_risks = generate_content(st.session_state.api_key, risk_data, "risks")
                if "error" in generated_risks:
                    st.error(generated_risks["error"])
                else:
                    st.session_state.prd_data["risks"] = generated_risks.get("risks", [])
        
        st.button("Generate Risks & Next Steps", on_click=generate_risks)

        for i, r in enumerate(st.session_state.prd_data.get("risks", [])):
            if st.session_state.editing_risk == i:
                with st.form(key=f"edit_risk_form_{i}"):
                    edited_risk_text = st.text_area("Edit Risk", value=r['risk'], height=100)
                    edited_mitigation_text = st.text_area("Edit Mitigation", value=r['mitigation'], height=100)
                    st.form_submit_button("Save Risk", on_click=save_risk_edit, args=(i, edited_risk_text, edited_mitigation_text))
            else:
                st.markdown(f"**Risk {i+1}:** {r['risk']}")
                st.markdown(f"**Mitigation:** {r['mitigation']}")
                st.button(f"✏️ Edit Risk {i+1}", key=f"edit_risk_{i}", on_click=set_editing_risk, args=(i,))

    # --- Section 5: Download Button ---
    st.subheader("Download PRD")
    try:
        # Generate PDF bytes just before rendering the button.
        # This makes it a single-click download.
        pdf_bytes = create_pdf(prd)
        st.download_button(
            label="📥 Download PRD as PDF",
            data=pdf_bytes,
            file_name="AB_Testing_PRD.pdf",
            mime="application/pdf"
        )
    except Exception as e:
        st.error(f"Error generating PDF: {e}")


# --- Sidebar Navigation ---
st.sidebar.title("Navigation")
for s in STAGES:
    # Use partial to pass the stage name to the callback
    st.sidebar.button(s, key=f"nav_{s}", on_click=partial(set_stage, s))

st.sidebar.button("⬅️ Back", key="back_btn", on_click=back_stage)
st.sidebar.button("➡️ Next", key="next_btn", on_click=next_stage)

# --- Main Rendering Logic ---
# This part remains the same, as it correctly routes to the right page based on the stage.
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
