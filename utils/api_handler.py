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
    Calls Groq API to generate hypotheses, PRD sections, or enrich hypotheses.
    - api_key: Groq API key (user-provided)
    - data: dict or string, depending on mode
    - mode: "hypotheses", "prd_sections", "enrich_hypothesis"
    """
    try:
        url = "https://api.groq.com/openai/v1/chat/completions"

        # --- Build Prompt ---
        if mode == "hypotheses":
            user_prompt = f"""
            Based on the following A/B test inputs, generate 2 strong hypotheses.

            Inputs:
            - Business Goal: {data.get("business_goal")}
            - Key Metric: {data.get("key_metric")} ({data.get("metric_unit")})
            - Current Value: {data.get("current_value")}
            - Target Value: {data.get("target_value")}
            - Product Area: {data.get("product_area")}
            - Product Type: {data.get("product_type")}
            - DAU: {data.get("dau")}

            Each hypothesis should be returned as JSON with fields:
            {{
              "Statement": "...",
              "Rationale": "...",
              "Behavioral Basis": "...",
              "Implementation Steps": "..."
            }}
            Return an object with keys Hypothesis 1, Hypothesis 2.
            """
        elif mode == "prd_sections":
            user_prompt = f"""
            Draft PRD sections based on the following hypothesis:

            {json.dumps(data, indent=2)}

            Return JSON with sections as keys (Problem, Goal, Success Metrics, Implementation Plan).
            """
        elif mode == "enrich_hypothesis":
            user_prompt = f"""
            Enrich the following custom hypothesis:

            {data}

            Return JSON with:
            {{
              "Statement": "...",
              "Rationale": "...",
              "Behavioral Basis": "...",
              "Implementation Steps": "..."
            }}
            """
        else:
            return {"error": f"Invalid mode '{mode}'"}

        # --- Make API Call ---
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }

        payload = {
            "model": "llama-3.3-70b-versatile",   # ✅ updated model
            "messages": [
                {"role": "system", "content": "You are an expert product manager helping draft PRDs."},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": 0.7,
            "max_tokens": 1200,
            "response_format": {"type": "json_object"}   # ✅ force JSON
        }

        response = requests.post(url, headers=headers, json=payload)
        if response.status_code != 200:
            return {"error": f"API Error {response.status_code}: {response.text}"}

        raw_text = response.json()["choices"][0]["message"]["content"]

        # --- Safe Parse ---
        return safe_json_parse(raw_text)

    except Exception as e:
        return {"error": str(e)}
