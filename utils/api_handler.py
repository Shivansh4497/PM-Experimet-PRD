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
            optional_context = ""
            if data.get("user_persona"):
                optional_context += f"\\n- Target User Persona: {data['user_persona']}"
            if data.get("app_description"):
                optional_context += f"\\n- App Description: {data['app_description']}"
            
            if optional_context:
                optional_context = f"\\nAdditional Context:\\n{optional_context}"
            user_prompt = f"""
            Based on the A/B test inputs, generate 3 strong hypotheses.You are the world's best product manager especiallising in product sense and product intuition. You understand user pschology to the fullest. You are a master retention and monetization expert.
            For each input think deeply and give highly perosnalised response to the inputs.            
            Inputs: {json.dumps(data, indent=2)}
            Each hypothesis should be a JSON object with "Statement", "Rationale", and "Behavioral Basis".
            Return a single JSON object with keys "Hypothesis 1" and "Hypothesis 2".
            Do not use any special character that could mess up json parsing in your answer whatsoever.
            """
        elif mode == "prd_sections":
            optional_context = ""
            if data.get("user_persona"):
                optional_context += f"\\n- Target User Persona: {data['user_persona']}"
            if data.get("app_description"):
                optional_context += f"\\n- App Description: {data['app_description']}"
            
            if optional_context:
                optional_context = f"\\nAdditional Context:\\n{optional_context}"
            user_prompt = f"""
            You are the world's best product manager especiallising in product sense and product intuition. You understand user pschology to the fullest. You are a master retention and monetization expert.
            For each input think deeply and give highly perosnalised response to the inputs.
            Draft PRD sections for this hypothesis and context: {json.dumps(data, indent=2)}
            You MUST return a single JSON object. 
            The keys of this object MUST be exactly "Problem_Statement", "Goal_and_Success_Metrics", and "Implementation_Plan".
            The value for "Problem_Statement" and "Goal_and_Success_Metrics" should be a string.
            The value for "Implementation_Plan" MUST be a list of strings, where each string is a distinct step.
            Do not use any special character that could mess up json parsing in your answer whatsoever.
            """
        elif mode == "enrich_hypothesis":
            optional_context = ""
            if data.get("user_persona"):
                optional_context += f"\\n- Target User Persona: {data['user_persona']}"
            if data.get("app_description"):
                optional_context += f"\\n- App Description: {data['app_description']}"
            
            if optional_context:
                optional_context = f"\\nAdditional Context:\\n{optional_context}"
            user_prompt = f"""
            You are the world's best product manager especiallising in product sense and product intuition. You understand user pschology to the fullest. You are a master retention and monetization expert.
            Enrich this custom hypothesis: "{data.get('custom_hypothesis')}"
            Use the following context to make it more specific and relevant.
            Context: {json.dumps(data, indent=2)}
            Return JSON with: "Statement", "Rationale", "Behavioral Basis". The "Statement" should be the enriched version of the custom hypothesis.
            Do not use any special character that could mess up json parsing in your answer whatsoever.
            """
        elif mode == "risks":
            optional_context = ""
            if data.get("user_persona"):
                optional_context += f"\\n- Target User Persona: {data['user_persona']}"
            if data.get("app_description"):
                optional_context += f"\\n- App Description: {data['app_description']}"
            
            if optional_context:
                optional_context = f"\\nAdditional Context:\\n{optional_context}"

            user_prompt = f"""
            You are the world's best product manager especiallising in product sense and product intuition. You understand user pschology to the fullest. You are a master retention and monetization expert.
            For each input think deeply and give highly perosnalised response to the inputs.
            Analyze the following A/B test idea and identify 3 potential risks.
            Business Goal: {data.get("business_goal")}
            Hypothesis: {data.get("hypothesis")}
            {optional_context}
            Return a JSON object with a single key "risks", which is a list of objects.
            Each object in the list should have two keys: "risk" and "mitigation".
            Example: {{"risks": [{{"risk": "...", "mitigation": "..."}}]}}
            Do not use any special character that could mess up json parsing in your answer whatsoever.
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
