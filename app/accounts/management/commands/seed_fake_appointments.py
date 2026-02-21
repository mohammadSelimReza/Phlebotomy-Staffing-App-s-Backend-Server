import random  # Import the random module
from django.core.management.base import BaseCommand
from faker import Faker
from app.business_owner.models import Job
from app.accounts.models import CustomerUser,AppointmentModel
from datetime import timedelta, datetime
from django.utils import timezone

fake = Faker()

class Command(BaseCommand):
    help = "Generate fake appointments"

    def handle(self, *args, **kwargs):
        # Get the business owner (for this example, hardcoding email of business owner)
        business_owner = CustomerUser.objects.get(email='yflores@example.com')

        # Get all the jobs created by the business owner
        jobs = Job.objects.filter(created_by=business_owner)

        # Get the clients (create fake clients if necessary)
        clients = CustomerUser.objects.filter(role='user')  # Fetch existing clients

        if not clients:
            self.stdout.write(self.style.ERROR("No clients found. Please create clients first."))
            return
        
        appointments = []
        for _ in range(60):  # Create 60 appointments
            # Randomly pick a job and client
            job = random.choice(jobs)  # Use random.choice here
            client = random.choice(clients)  # Use random.choice here

            # Generate random appointment times
            start_date = fake.date_this_year()
            start_time = fake.time()

            # Convert start_time string to datetime.time object
            start_time_obj = datetime.strptime(start_time, "%H:%M:%S").time()

            # Parse total_working_hour string to calculate timedelta
            total_working_hours = job.total_working_hour.split(":")
            hours = int(total_working_hours[0])
            minutes = int(total_working_hours[1])

            # Calculate end_time based on the job's total working hours
            start_datetime = timezone.datetime.combine(start_date, start_time_obj)
            end_time = start_datetime + timedelta(hours=hours, minutes=minutes)

            # Create the appointment instance
            appointment = AppointmentModel(
                user=client,
                test_package=job,
                start_date=start_date,
                start_date_start_time=start_time,
                start_date_end_time=end_time.time(),
                end_date=start_date,
                end_date_start_time=end_time.time(),
                end_date_end_time=(end_time + timedelta(hours=hours, minutes=minutes)).time(),
                hospital=fake.company(),
                location=fake.address(),
                current_medication=fake.text(),
                prescription=None,  # Can add fake prescriptions if needed
                known_allergies=fake.text(),
                medical_conditions=[],  # Add as needed
                special_request=fake.text(),
                email_notification_enable=fake.boolean(),
                terms_and_condition_agreement=True,
                agreement=True,
                initial_fee=fake.random_number(digits=2),
                service_fee=fake.random_number(digits=2),
                tax_fee=fake.random_number(digits=2),
                street_address=fake.address(),
                city=fake.city(),
                state=fake.state(),
                zip_code=fake.zipcode(),
                payment_status=fake.boolean(),
                assigned=business_owner,  # This could be dynamic depending on your structure
            )
            appointment.save()
            appointments.append(appointment)

            self.stdout.write(self.style.SUCCESS(f"Appointment created for {client.full_name} for {job.title}"))

        self.stdout.write(self.style.SUCCESS(f"Successfully created {len(appointments)} appointments"))
