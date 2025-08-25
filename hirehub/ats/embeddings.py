from sentence_transformers import SentenceTransformer

# Load the model only once when the application starts
# This model creates 384-dimensional vectors
model = SentenceTransformer('all-MiniLM-L6-v2')

def get_embedding(text):
    return model.encode(text)

def generate_job_embedding_text(job_position):
    """Combines the most relevant fields for a job into a single string."""
    return f"Job Title: {job_position.title}\nDescription: {job_position.description}\nRequirements: {job_position.requirements}"

def generate_applicant_embedding_text(applicant):
    """Uses the resume text for the applicant embedding."""
    return applicant.resume_text
