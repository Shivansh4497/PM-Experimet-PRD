import groq
import json

def generate_content(api_key, data, content_type):
    """
    Generates content using the Groq API based on the specified content type.

    Args:
        api_key (str): The API key for Groq.
        data (dict or str): The input data for the prompt.
        content_type (str): The type of content to generate (e.g., 'hypotheses', 'enrich_hypothesis', 'prd_sections').

    Returns:
        dict: The generated content as a dictionary or a dictionary with an error message.
    """
    client = groq.Groq(api_key=api_key)
    model = "llama3-8b-8192"  # Using a suitable Groq model

    # Prompts for different content types
    prompts = {
        "hypotheses": f"""
        You are a product manager's co-pilot for A/B testing.
        Based on the following business context, generate three distinct and well-defined hypotheses for an A/B test.
        For each hypothesis, provide a:
        - "Statement": A clear, concise hypothesis statement.
        - "Rationale": The reasoning behind the hypothesis.
        - "Behavioral Basis": A psychological or behavioral principle that supports the hypothesis.
        - "Implementation Steps": A high-level, actionable plan to implement the change.
        
        Business Context:
        {json.dumps(data)}
        
        Respond with a JSON object where the keys are "Hypothesis 1", "Hypothesis 2", and "Hypothesis 3".
        """,
        "enrich_hypothesis": f"""
        You are a product manager's co-pilot. A user has provided a custom hypothesis for an A/B test.
        Based on the following hypothesis statement, please provide a detailed:
        - "Statement": The user's original statement.
        - "Rationale": The reasoning behind the hypothesis.
        - "Behavioral Basis": A psychological or behavioral principle that supports the hypothesis.
        - "Implementation Steps": A high-level, actionable plan to implement the change.

        Hypothesis Statement:
        {data}

        Respond with a JSON object with keys: "Statement", "Rationale", "Behavioral Basis", and "Implementation Steps".
        """,
        "prd_sections": f"""
        You are a product manager's co-pilot. A user has selected a hypothesis for their A/B test.
        Based on the following hypothesis, draft the following sections for a Product Requirements Document (PRD):
        - "Problem Statement": Briefly describe the problem this experiment addresses.
        - "Risks & Assumptions": Outline potential risks and key assumptions.
        - "Secondary & Hygiene Metrics": List other metrics to monitor.
        - "Next Steps": Detail what happens after the experiment concludes.

        Selected Hypothesis:
        {json.dumps(data)}
        
        Respond with a JSON object with keys: "Problem Statement", "Risks & Assumptions", "Secondary & Hygiene Metrics", and "Next Steps".
        """
    }

    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": prompts[content_type],
                }
            ],
            model=model,
            response_format={"type": "json_object"},
            temperature=0.5
        )
        response_content = chat_completion.choices[0].message.content
        return json.loads(response_content)
    except Exception as e:
        return {"error": f"An error occurred with the LLM call: {e}"}

