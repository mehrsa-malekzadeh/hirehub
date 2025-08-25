import random
from django.core.management.base import BaseCommand
from faker import Faker
from ats.models import JobPosition, Applicant

class Command(BaseCommand):
    help = 'Seeds the database with fake data'

    def add_arguments(self, parser):
        parser.add_argument('model', type=str, help='The model to seed (JobPosition or Applicant)')
        parser.add_argument('--number', type=int, default=10, help='The number of records to create')

    def handle(self, *args, **options):
        model_name = options['model']
        number = options['number']
        self.stdout.write(f'Seeding {number} records for {model_name}...')

        if model_name == 'JobPosition':
            self.seed_job_positions(number)
        elif model_name == 'Applicant':
            self.seed_applicants(number)
        else:
            self.stderr.write(f'Unknown model: {model_name}')
            return

        self.stdout.write(self.style.SUCCESS('Successfully seeded the database.'))

    def seed_job_positions(self, number):
        fake = Faker()
        for _ in range(number):
            JobPosition.objects.create(
                title=fake.job(),
                description=fake.text(),
                requirements=fake.text(),
                is_active=random.choice([True, False])
            )

    def seed_applicants(self, number):
        fake = Faker()
        job_positions = list(JobPosition.objects.all())
        if not job_positions:
            self.stderr.write('No job positions found. Please seed job positions first.')
            return

        for _ in range(number):
            Applicant.objects.create(
                name=fake.name(),
                email=fake.email(),
                phone=fake.phone_number(),
                job_position=random.choice(job_positions),
                current_stage=random.choice([choice[0] for choice in Applicant.STAGE_CHOICES]),
                source=random.choice([choice[0] for choice in Applicant.SOURCE_CHOICES]),
                tags=', '.join(fake.words(nb=3)),
                resume_text=fake.text(),
                interviewers=', '.join(fake.name() for _ in range(random.randint(1, 3))),
                interview_dates=fake.date_time().isoformat(),
                comments_ta=fake.text(),
                comments_initial_call=fake.text(),
                comments_evaluation=fake.text(),
                overall_feedback=fake.text(),
                final_decision=fake.sentence(),
            )
