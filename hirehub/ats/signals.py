from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import JobPosition, Applicant
from .embeddings import get_embedding, generate_job_embedding_text, generate_applicant_embedding_text

@receiver(post_save, sender=JobPosition)
def update_job_embedding(sender, instance, created, **kwargs):
    # Avoid recursion and only update if text has changed
    text_to_embed = generate_job_embedding_text(instance)
    new_embedding = get_embedding(text_to_embed)

    # Update without triggering the signal again
    JobPosition.objects.filter(pk=instance.pk).update(embedding=new_embedding)

@receiver(post_save, sender=Applicant)
def update_applicant_embedding(sender, instance, **kwargs):
    if instance.resume_text: # Only if there's resume text
        text_to_embed = generate_applicant_embedding_text(instance)
        new_embedding = get_embedding(text_to_embed)
        Applicant.objects.filter(pk=instance.pk).update(embedding=new_embedding)
