from django.core.management.base import BaseCommand
from django.utils import timezone
from app.business_owner.models import Job, TempAssignedJob, RequestForJob, AcceptedAssignedJob, CompletedAssignedJob
from app.accounts.models import CustomerUser
from random import choice, randint
from datetime import timedelta, datetime

class Command(BaseCommand):
    help = 'Generate fake data for jobs and assignments'

    def handle(self, *args, **kwargs):
        # Step 1: Create 30 Jobs for Business Owner
        business_owner = CustomerUser.objects.get(email='yflores@example.com')  # Business Owner User
        job_types = ['urgent', 'full_day', 'part_time']
        pay_types = ['hourly', 'flat_rate']
        active_status = ['approved', 'pending', 'rejected']

        jobs = []
        for i in range(30):
            # Generate start time as datetime object
            start_time = timezone.now().replace(hour=randint(8, 12), minute=0, second=0, microsecond=0)

            # Add a random timedelta to generate end time
            end_time = start_time + timedelta(hours=randint(1, 12))

            job = Job.objects.create(
                title=f"Job Title {i+1}",
                profession_type="Phlebotomy",
                job_info=f"Job information for Job {i+1}",
                location=f"Location {i+1}",
                date=timezone.now().date() + timedelta(days=randint(0, 30)),
                start_time=start_time.time(),  # Convert datetime to time
                end_time=end_time.time(),      # Convert datetime to time
                pay_type=choice(pay_types),
                pay_rate=randint(50, 150),
                job_types=choice(job_types),
                active_status=choice(active_status),
                created_by=business_owner
            )
            jobs.append(job)

        self.stdout.write(self.style.SUCCESS(f'Created {len(jobs)} jobs'))

        # Step 2: Assign Some Jobs to Phlebotomist (englishlisa@example.net)
        phlebotomist = CustomerUser.objects.get(email='englishlisa@example.net')  # Phlebotomist User
        for job in jobs[:15]:  # Assign 15 jobs
            TempAssignedJob.objects.create(
                job=job,
                assigned_to=phlebotomist,
                assigned_by=business_owner,
                assignment_start_time=timezone.now(),
                assignment_end_time=timezone.now() + timedelta(hours=randint(1, 8)),
                status='assigned',
                is_accepted=False
            )

        self.stdout.write(self.style.SUCCESS('Assigned some jobs to phlebotomist'))

        # Step 3: Phlebotomist requests jobs
        for job in jobs[10:20]:  # Phlebotomist requests jobs 10-20
            RequestForJob.objects.create(
                job=job,
                requested_by=phlebotomist,
                status='pending'
            )

        self.stdout.write(self.style.SUCCESS('Phlebotomist made job requests'))

        # Step 4: Business Owner assigns jobs to Phlebotomist (accepting some requests)
        for request in RequestForJob.objects.all():
            if choice([True, False]):  # Randomly accept or reject requests
                AcceptedAssignedJob.objects.create(
                    job=request.job,
                    assigned_to=request.requested_by,
                    assigned_by=business_owner,
                    accepted_on=timezone.now()
                )
                request.status = 'assigned'
                request.save()

        self.stdout.write(self.style.SUCCESS('Business owner assigned jobs to phlebotomist'))

        # Step 5: Mark Some Jobs as Completed
        for accepted_job in AcceptedAssignedJob.objects.all()[:10]:  # Mark 10 jobs as completed
            CompletedAssignedJob.objects.create(
                job=accepted_job.job,
                completed_by=accepted_job.assigned_to,
                assigned_by=accepted_job.assigned_by,
                completed_on=timezone.now(),
                payment_status=True  # Marking payment as complete
            )
            accepted_job.completed = True
            accepted_job.save()

        self.stdout.write(self.style.SUCCESS('Marked some jobs as completed'))
