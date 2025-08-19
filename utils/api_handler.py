import os
import json
import re
import requests

# --- Safe JSON Parse Helper ---
def safe_json_parse(raw_text):
    try:
        return json.loads(raw_text)
    except json.JSONDecodeError:
        # Attempt quick repair: strip junk before/after JSON
        match = re.search(r"\{.*\}", raw_text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group())
            except Exception:
                pass
        return {"error": "Failed to parse LLM response as JSON", "raw": raw_text}


# --- Core Function ---
def generate_content(api_key, data, mode="hypotheses"):
    """
    Calls Groq API for various content generation tasks.
    - mode: "hypotheses", "prd_sections", "enrich_hypothesis", "risks"
    """
    try:
        url = "https://api.groq.com/openai/v1/chat/completions"
        user_prompt = ""

        # --- Build Prompt based on mode ---
        if mode == "hypotheses":
            user_prompt = f"""
            Based on the A/B test inputs, generate 2 strong hypotheses.
            Inputs: {json.dumps(data, indent=2)}
            Each hypothesis should be a JSON object with "Statement", "Rationale", and "Behavioral Basis".
            Return a single JSON object with keys "Hypothesis 1" and "Hypothesis 2".
            """
        elif mode == "prd_sections":
            # FIX: Re-engineered prompt to enforce clean keys AND structured values (like lists for plans).
            user_prompt = f"""
            Draft PRD sections for this hypothesis: {json.dumps(data, indent=2)}
            You MUST return a single JSON object. 
            The keys of this object MUST be exactly "Problem_Statement", "Goal_and_Success_Metrics", and "Implementation_Plan".
            The value for "Problem_Statement" and "Goal_and_Success_Metrics" should be a string.
            The value for "Implementation_Plan" MUST be a list of strings, where each string is a distinct step.
            """
        elif mode == "enrich_hypothesis":
            user_prompt = f"""
            Enrich this custom hypothesis: "{data}"
            Return JSON with: "Statement", "Rationale", "Behavioral Basis".
            """
        elif mode == "risks":
            user_prompt = f"""
            Analyze the following A/B test idea and identify 3 potential risks.
            Business Goal: {data.get("business_goal")}
            Hypothesis: {data.get("hypothesis")}
            Return a JSON object with a single key "risks", which is a list of objects.
            Each object in the list should have two keys: "risk" and "mitigation".
            Example: {{"risks": [{{"risk": "...", "mitigation": "..."}}]}}
            """
        else:
            return {"error": f"Invalid mode '{mode}'"}

        # --- API Call ---
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": "llama-3.3-70b-versatile",
            "messages": [
                {"role": "system", "content": "You are an expert product manager. Respond with concise, valid JSON that strictly follows the user's requested format."},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": 0.5,
            "max_tokens": 1200,
            "response_format": {"type": "json_object"}
        }

        response = requests.post(url, headers=headers, json=payload)
        if response.status_code != 200:
            return {"error": f"API Error {response.status_code}: {response.text}"}

        raw_text = response.json()["choices"][0]["message"]["content"]
        return safe_json_parse(raw_text)

    except Exception as e:
        return {"error": str(e)}
