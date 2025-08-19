import streamlit as st
import pandas as pd
import re
# Import functions from your utility files.
from utils.api_handler import generate_content
from utils.calculations import calculate_sample_size, calculate_duration
from utils.pdf_generator import create_pdf

try:
    from utils.calculations import calculate_sample_size, calculate_duration
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
        "calculations": {}
    }
if "editing_section" not in st.session_state:
    st.session_state.editing_section = None


# --- Helper Functions ---
def next_stage():
    current_index = STAGES.index(st.session_state.stage)
    if current_index < len(STAGES) - 1:
        st.session_state.stage = STAGES[current_index + 1]

def back_stage():
    current_index = STAGES.index(st.session_state.stage)
    if current_index > 0:
        st.session_state.stage = STAGES[current_index - 1]

def set_editing_section(section_title):
    st.session_state.editing_section = section_title

def save_edit(section_title, edited_text):
    st.session_state.prd_data["prd_sections"][section_title] = edited_text
    st.session_state.editing_section = None
    st.success(f"Changes to '{section_title}' saved!")

def format_content_for_display(content):
    if isinstance(content, list):
        return "\n".join([f"- {item}" for item in content])
    elif isinstance(content, dict):
        formatted_str = ""
        for key, value in content.items():
            formatted_str += f"\n**{key}**:\n"
            if isinstance(value, list):
                bullet_list = "\n".join([f"- {item}" for item in value])
                formatted_str += f"{bullet_list}\n"
            else:
                formatted_str += f"{value}\n"
        return formatted_str
    else:
        return content


# --- UI Rendering Functions ---
import re

def render_intro_page():
    st.header("Step 1: The Basics 📝")
    st.write("Please provide some high-level details about your A/B test.")
    
    st.session_state.api_key = st.text_input("Enter your Groq API Key", type="password")

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
                placeholder="e.g., Login Rate, ARPDAU"
            )

            # --- Metric Unit with dropdown + custom ---
            metric_unit_choice = st.selectbox(
                "Metric Unit",
                options=["%", "INR", "USD", "count", "Other"],
                index=0
            )

            if metric_unit_choice == "Other":
                custom_metric_unit = st.text_input("Enter custom metric unit (letters, numbers, spaces only)")
                if custom_metric_unit:
                    if re.match(r"^[A-Za-z0-9 ]+$", custom_metric_unit):
                        st.session_state.prd_data["intro_data"]["metric_unit"] = custom_metric_unit
                    else:
                        st.warning("⚠️ Metric unit can only contain letters, numbers, and spaces. No special characters allowed.")
                        st.session_state.prd_data["intro_data"]["metric_unit"] = None
                else:
                    st.session_state.prd_data["intro_data"]["metric_unit"] = None
            else:
                st.session_state.prd_data["intro_data"]["metric_unit"] = metric_unit_choice

            st.session_state.prd_data["intro_data"]["current_value"] = st.number_input(
                "Current Metric Value",
                min_value=0.0,
                value=50.0,
                help="The current value of your key metric."
            )
        with col2:
            st.session_state.prd_data["intro_data"]["product_area"] = st.text_input(
                "Product Area",
                placeholder="e.g., Mobile App Onboarding"
            )
            st.session_state.prd_data["intro_data"]["target_value"] = st.number_input(
                "Target Metric Value",
                min_value=0.0,
                value=55.0,
                help="The value you are aiming for."
            )
            st.session_state.prd_data["intro_data"]["dau"] = st.number_input(
                "Daily Active Users (DAU)",
                min_value=100,
                value=10000,
                help="The total number of unique users daily."
            )
            st.session_state.prd_data["intro_data"]["product_type"] = st.selectbox(
                "Product Type",
                options=["SaaS Product", "Mobile App", "Web Platform", "Other"],
                index=1
            )

        submit_button = st.form_submit_button("Generate Hypotheses")
        if submit_button:
            if not st.session_state.api_key:
                st.error("Please provide your Groq API Key to proceed.")
            elif all(v for v in st.session_state.prd_data["intro_data"].values()):
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



def render_hypothesis_page():
    st.header("Step 2: Hypotheses 🧠")
    st.write("We've generated a few hypotheses for you. Select your favorite or write your own!")
    
    # --- Show generated hypotheses (from intro stage) ---
    if isinstance(st.session_state.hypotheses, dict):
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
                    st.subheader("Implementation Steps")
                    st.markdown(data.get("Implementation Steps", "N/A"))
                    if st.button(f"Select {name}", key=f"select_{i}"):
                        st.session_state.prd_data["hypothesis"] = data
                        st.success(f"You have selected: {data['Statement']}")
                        st.session_state.hypotheses_selected = True

    st.write("---")
    st.subheader("Or, Write Your Own Hypothesis")
    custom_hypothesis = st.text_area("Your Custom Hypothesis", placeholder="e.g., I hypothesize that...")

    # --- Generate enriched hypothesis from custom ---
    if st.button("Generate from Custom", key="gen_custom_btn"):
        if not st.session_state.api_key:
            st.error("Please provide your Groq API Key to proceed.")
        elif custom_hypothesis:
            with st.spinner("Generating from custom hypothesis..."):
                # FIX: Pass the raw string for enrichment
                enriched_data = generate_content(
                    st.session_state.api_key,
                    custom_hypothesis,  # raw string, not dict
                    "enrich_hypothesis"
                )
                if "error" in enriched_data:
                    st.error(enriched_data["error"])
                else:
                    st.session_state.custom_hypothesis_generated = enriched_data
                    st.success("Your custom hypothesis has been generated! Please review below.")

    # --- Show enriched hypothesis (before locking) ---
    if "custom_hypothesis_generated" in st.session_state:
        st.subheader("Generated Hypothesis Details")
        enriched = st.session_state.custom_hypothesis_generated
        st.markdown(f"**Statement:** {enriched.get('Statement', 'N/A')}")
        st.markdown(f"**Rationale:** {enriched.get('Rationale', 'N/A')}")
        st.markdown(f"**Behavioral Basis:** {enriched.get('Behavioral Basis', 'N/A')}")
        st.markdown(f"**Implementation Steps:** {enriched.get('Implementation Steps', 'N/A')}")

        if st.button("Lock This Hypothesis", key="lock_custom_btn"):
            st.session_state.prd_data["hypothesis"] = enriched
            st.session_state.hypotheses_selected = True
            st.success("Custom hypothesis locked!")

    st.write("---")
    if st.button("Continue to PRD Draft", key="continue_prd_btn"):
        if "hypotheses_selected" in st.session_state and st.session_state.hypotheses_selected:
            next_stage()
        else:
            st.error("Please select or generate a hypothesis before continuing.")


def render_prd_page():
    st.header("Step 3: PRD Draft ✍️")
    st.write("We've drafted the core sections of your PRD. Please edit and finalize them.")
    
    if not st.session_state.prd_data.get("prd_sections"):
        with st.spinner("Drafting PRD sections..."):
            prd_sections = generate_content(
                st.session_state.api_key,
                st.session_state.prd_data["hypothesis"],
                "prd_sections"
            )
            if "error" in prd_sections:
                st.error(prd_sections["error"])
            else:
                st.session_state.prd_data["prd_sections"] = prd_sections
                st.session_state.editing_section = None

    for section_title, content in st.session_state.prd_data["prd_sections"].items():
        with st.container(border=True):
            col1, col2 = st.columns([1, 10])
            with col1:
                if st.session_state.editing_section != section_title:
                    if st.button("✏️", key=f"edit_{section_title}"):
                        set_editing_section(section_title)
            with col2:
                st.subheader(f"**{section_title}**")
            
            if st.session_state.editing_section != section_title:
                st.markdown(format_content_for_display(content))
            else:
                edited_text = st.text_area(
                    "Edit this section",
                    value=format_content_for_display(content),
                    height=200,
                    key=f"text_area_{section_title}"
                )
                if st.button("Save Changes", key=f"save_{section_title}"):
                    save_edit(section_title, edited_text)

    st.write("---")
    if st.button("Save & Continue to Calculations", key="to_calcs"):
        next_stage()


def render_calculations_page():
    if not CALCULATIONS_AVAILABLE:
        st.error("⚠️ Experiment calculations are unavailable because a required dependency (`scipy`) is missing.")
        return
    st.header("Step 4: Experiment Calculations 📊")
    st.write("Verify the inputs below to calculate your required sample size and duration.")

    intro_data = st.session_state.prd_data["intro_data"]
    dau = intro_data.get("dau", 10000)
    current_value = intro_data.get("current_value", 50.0)
    target_value = intro_data.get("target_value", 55.0)
    unit = intro_data.get("metric_unit", "")

    # Sidebar controls
    st.sidebar.subheader("Experiment Parameters")
    st.session_state.prd_data["calculations"]["confidence"] = st.sidebar.slider(
        "Confidence Level (%)", min_value=50, max_value=99, value=95, step=1
    ) / 100
    st.session_state.prd_data["calculations"]["power"] = st.sidebar.slider(
        "Power Level (%)", min_value=50, max_value=99, value=80, step=1
    ) / 100
    st.session_state.prd_data["calculations"]["coverage"] = st.sidebar.slider(
        "Coverage (%)", min_value=5, max_value=100, value=50, step=5
    )
    st.session_state.prd_data["calculations"]["min_detectable_effect"] = st.sidebar.number_input(
        "Minimum Detectable Effect (%)", min_value=0.0, value=5.0
    )

    st.subheader("Key Metrics")
    st.markdown(f"**Key Metric:** {intro_data.get('key_metric', 'N/A')} ({unit})")
    st.markdown(f"**Current Value:** {intro_data.get('current_value', 'N/A')} {unit}")
    st.markdown(f"**Target Value:** {intro_data.get('target_value', 'N/A')} {unit}")
    st.markdown(f"**Daily Active Users (DAU):** {dau}")

    if st.button("Calculate", key="calc_btn"):
        try:
            sample_size_per_variant = calculate_sample_size(
                current_value=current_value,
                min_detectable_effect=st.session_state.prd_data["calculations"]["min_detectable_effect"],
                confidence=st.session_state.prd_data["calculations"]["confidence"],
                power=st.session_state.prd_data["calculations"]["power"]
            )
            duration_in_days = calculate_duration(
                sample_size=sample_size_per_variant,
                daily_active_users=dau,
                coverage=st.session_state.prd_data["calculations"]["coverage"]
            )
            st.session_state.prd_data["calculations"]["sample_size"] = sample_size_per_variant
            st.session_state.prd_data["calculations"]["duration"] = duration_in_days
            st.success("Calculations complete!")
        except Exception as e:
            st.error(f"Error in calculations: {e}")

    if "sample_size" in st.session_state.prd_data["calculations"]:
        st.subheader("Results")
        st.info(f"**Required Sample Size per Variant:** {st.session_state.prd_data['calculations']['sample_size']}")
        st.info(f"**Estimated Experiment Duration:** {st.session_state.prd_data['calculations']['duration']} days")
        if st.button("Continue to Final Review", key="to_review"):
            next_stage()



def render_final_review_page():
    st.header("Step 5: Final Review & Export 🎉")
    st.write("Your complete PRD is ready. Review, polish, and export.")

    prd = st.session_state.prd_data

    # --- Executive Summary ---
    with st.container():
        st.markdown("""
        <div style="
            background-color:#161b22;
            padding:20px;
            border-radius:12px;
            border:1px solid #30363d;
            box-shadow: 0 4px 6px rgba(0,0,0,0.2);
            margin-bottom:15px;
            ">
            <h3>🚀 Executive Summary</h3>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"**Business Goal:** {prd['intro_data'].get('business_goal', 'N/A')}")
        st.markdown(f"**Hypothesis:** {prd['hypothesis'].get('Statement', 'N/A')}")
        st.markdown(
            f"**Success Criteria:** Target {prd['intro_data'].get('key_metric', 'N/A')} → "
            f"{prd['intro_data'].get('target_value', 'N/A')} {prd['intro_data'].get('metric_unit', '')}"
        )

    # --- PRD Sections with Proper Expanders ---
    st.subheader("3.0 PRD Sections")

    prd_sections = prd.get('prd_sections', {})
    if not prd_sections:
        st.info("No PRD sections generated yet.")
    else:
        for section_title, content in prd_sections.items():
            # Guarantee clean, non-empty section labels
            section_label = str(section_title).strip() or "Untitled Section"
            
            with st.expander(f"📑 {section_label}", expanded=False):
                if st.session_state.editing_section == section_label:
                    # Editable mode
                    edited_text = st.text_area(
                        "Edit this section",
                        value=format_content_for_display(content),
                        height=200,
                        key=f"text_area_review_{section_label}"
                    )
                    if st.button("Save Changes", key=f"save_review_{section_label}"):
                        save_edit(section_label, edited_text)
                else:
                    # Normal view mode
                    st.markdown(format_content_for_display(content))
                    if st.button(f"✏️ Edit {section_label}", key=f"edit_review_{section_label}"):
                        set_editing_section(section_label)

    # --- Experiment Metrics Dashboard ---
    st.subheader("4.0 Experiment Metrics Dashboard 📊")
    metrics_cols = st.columns(4)
    metrics_cols[0].metric("Confidence", f"{int(prd['calculations'].get('confidence', 0)*100)}%")
    metrics_cols[1].metric("Power", f"{int(prd['calculations'].get('power', 0)*100)}%")
    metrics_cols[2].metric("Sample Size", f"{prd['calculations'].get('sample_size', 'N/A')}", "↑ per variant")
    metrics_cols[3].metric("Duration", f"{prd['calculations'].get('duration', 'N/A')} days")

    # --- Risks & Next Steps ---
    st.subheader("5.0 Risks & Next Steps ⚠️")
    risks = [
        {"risk": "Low DAU may extend test duration", "mitigation": "Reduce variants or increase coverage"},
        {"risk": "Seasonality impact may bias results", "mitigation": "Run experiment over multiple weeks"},
    ]

    for i, r in enumerate(risks, start=1):
        st.markdown(f"**Risk {i}:** {r['risk']}")
        st.markdown(f"**Mitigation:** {r['mitigation']}")
        if st.button(f"✏️ Edit Risk {i}", key=f"edit_risk_{i}"):
            st.warning("Risk editing not yet implemented.")  # placeholder for now

    # --- Download as PDF ---
    if st.button("📥 Download PRD as PDF"):
        try:
            pdf_bytes = create_pdf(prd)
            st.download_button(
                label="Download PRD",
                data=pdf_bytes,
                file_name="AB_Testing_PRD.pdf",
                mime="application/pdf"
            )
        except Exception as e:
            st.error(f"Error generating PDF: {e}")


# --- Sidebar Navigation ---
st.sidebar.title("Navigation")
for s in STAGES:
    if st.sidebar.button(s, key=f"nav_{s}"):
        st.session_state.stage = s

if st.sidebar.button("⬅️ Back", key="back_btn"):
    back_stage()
if st.sidebar.button("➡️ Next", key="next_btn"):
    next_stage()

# --- Main Rendering ---
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
