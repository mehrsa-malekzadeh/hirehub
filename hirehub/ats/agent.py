import requests
import os

def get_ai_match_summary(job, applicant):
    """
    Uses the chat API to generate a qualitative summary of why an applicant
    is a good match for a job.
    """

    prompt = f"""
    You are an expert technical recruiter. Your task is to evaluate a candidate's resume for a specific job position.
    Provide a concise analysis in the following format:
    - **Relevancy Score (1-10):** [Your score here]
    - **Summary:** [A brief, one-sentence summary of the candidate's fit.]
    - **Strengths:** [A bulleted list of 2-3 key skills or experiences from the resume that directly match the job requirements.]
    - **Potential Gaps:** [A bulleted list of 1-2 areas where the resume doesn't align with the job requirements or seems weak.]

    ---
    **Job Position Details:**
    **Title:** {job.title}
    **Description:** {job.description}
    **Requirements:** {job.requirements}
    ---
    **Candidate's Resume:**
    {applicant.resume_text}
    ---

    Now, provide your analysis.
    """

    url = "https://api.atlascloud.ai/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {os.getenv('ATLASCLOUD_API_KEY')}" # Use environment variables!
    }
    data = {
        "model": "openai/gpt-oss-20b",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.5,
        "max_tokens": 500,
    }

    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status() # Raise an exception for bad status codes
        # Assuming the response json is like {'choices': [{'message': {'content': '...'}}]}
        content = response.json()['choices'][0]['message']['content']
        return content
    except requests.exceptions.RequestException as e:
        return f"Error communicating with AI agent: {e}"
