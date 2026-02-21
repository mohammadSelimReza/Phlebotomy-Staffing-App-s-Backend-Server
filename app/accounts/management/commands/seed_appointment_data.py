from django.core.management.base import BaseCommand
from app.accounts.models import CustomerUser, AppointmentModel
from app.business_owner.models import Job
from faker import Faker
import random

class Command(BaseCommand):
    help = "Generate 20 users and assign them appointments to available jobs"

    def handle(self, *args, **kwargs):
        fake = Faker()

        # Create 20 random users
        users = []
        for _ in range(20):
            user = CustomerUser.objects.create(
                full_name=fake.name(),
                email=fake.unique.email(),
                phone=fake.phone_number(),
                gender=random.choice(["Male", "Female"]),
                birth_date=fake.date_of_birth(minimum_age=25, maximum_age=55),
                role=CustomerUser.USER,
                account_status=CustomerUser.APPROVED,
                is_active=True,
            )
            user.set_password("password123")
            user.save()
            users.append(user)

        self.stdout.write(self.style.SUCCESS(f"Created {len(users)} users"))

        # List of job IDs that users will apply to
        job_ids = [
            "505787",  # Job ID from the list
            "621714",  # Job ID from the list
            "285023",  # Job ID from the list
            "111637",  # Job ID from the list
            "675068",  # Job ID from the list
        ]

        # Create appointments for each user and assign to a random job from job_ids
        for user in users:
            # Randomly pick a job from the list
            job_id = random.choice(job_ids)
            try:
                job = Job.objects.get(id=job_id)
            except Job.DoesNotExist:
                self.stdout.write(self.style.ERROR(f"Job with ID {job_id} does not exist"))
                continue

            # Create an appointment for this user
            appointment = AppointmentModel.objects.create(
                user=user,
                test_package=job.title,
                start_date=job.date,
                start_date_start_time=job.start_time,
                start_date_end_time=job.end_time,
                end_date=job.date,
                end_date_start_time=job.start_time,
                end_date_end_time=job.end_time,
                location=job.location,
                hospital=job.created_by.full_name,  # Assuming created_by is the business owner
                current_medication=fake.text(max_nb_chars=50),
                prescription=None,  # Assuming no prescription in this case
                known_allergies=fake.text(max_nb_chars=50),
                medical_conditions=["Condition1", "Condition2"],  # Example conditions
                special_request="No special request",
                email_notification_enable=True,
                terms_and_condition_agreement=True,
                agreement=True,
                initial_fee=0,
                service_fee=10,
                tax_fee=5,
                total=15,
                street_address=fake.address(),
                city=fake.city(),
                state=fake.state(),
                zip_code=fake.zipcode(),
                payment_status=True,  # Payment status initially false
            )
            self.stdout.write(self.style.SUCCESS(f"Created appointment {appointment.appointment_id} for user {user.full_name} on job {job.title}"))
