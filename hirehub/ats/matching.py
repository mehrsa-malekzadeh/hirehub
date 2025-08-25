from .models import Applicant, JobPosition
from pgvector.django.expressions import CosineDistance

def find_top_applicants_for_job(job_id, top_n=10):
    """
    Finds the top N most relevant applicants for a given job ID
    based on cosine similarity of their embeddings.
    """
    try:
        job = JobPosition.objects.get(id=job_id)
        if job.embedding is None:
            return [] # Job has no embedding yet

        # Find applicants and order them by the cosine distance to the job's embedding
        # CosineDistance: 0 = identical, 2 = opposite. So we order ascending.
        top_applicants = Applicant.objects.exclude(embedding__isnull=True).order_by(
            CosineDistance('embedding', job.embedding)
        )[:top_n]

        return top_applicants

    except JobPosition.DoesNotExist:
        return []
