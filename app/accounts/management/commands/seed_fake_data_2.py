from django.core.management.base import BaseCommand
from faker import Faker
import random
from django.utils import timezone
from datetime import timedelta, datetime

from app.accounts.models import CustomerUser, AppointmentModel, ActivityLog, NotificationModel, ReportUserModel
from app.accounts.models_profile import PhlebotomistProfile, BusinessOwnerProfile
from app.business_owner.models import Job, RequestForJob, TempAssignedJob, AcceptedAssignedJob, CompletedAssignedJob
from app.dashboard.models import PrivacyPolicy, TermsConditions
from app.message.models import Message, InappropriateMessageReport

fake = Faker()

class Command(BaseCommand):
    help = "Generate fake data for all models"

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.WARNING("Generating fake data..."))

        # ============================================================
        # 1. CREATE USERS (PHLEBOTOMISTS + BUSINESS OWNERS + NORMAL USERS)
        # ============================================================
        all_users = []

        for _ in range(200):  # Create 200 users
            role = random.choice(["user", "phlebotomist", "business_owner"])
            user = CustomerUser.objects.create(
                full_name=fake.name(),
                email=fake.unique.email(),
                phone=fake.phone_number(),
                gender=random.choice(["Male", "Female"]),
                birth_date=fake.date_of_birth(minimum_age=25, maximum_age=55),
                role=role,
                account_status=random.choice(["approved", "pending", "rejected"]),
                is_active=True
            )
            user.set_password("12345678")
            user.save()
            all_users.append(user)
            self.stdout.write(self.style.SUCCESS(f"{user.email} - {user.role} created"))
        self.stdout.write(self.style.SUCCESS("✔ Created CustomerUser records"))

        # ============================================================
        # 2. CREATE PHLEBOTOMIST PROFILES
        # ============================================================
        phlebotomists = CustomerUser.objects.filter(role="phlebotomist")

        for ph in phlebotomists:
            PhlebotomistProfile.objects.create(
                user=ph,
                license_number=f"LIC-{fake.random_int(10000, 99999)}",
                years_of_experience=random.randint(1, 15),
                service_area=fake.city(),
                speciality=fake.job(),
                weekly_schedule=[
                    {"day": "Monday", "start_time": "09:00", "end_time": "17:00"},
                    {"day": "Tuesday", "start_time": "09:00", "end_time": "17:00"},
                    {"day": "Wednesday", "start_time": "09:00", "end_time": "17:00"},
                    {"day": "Thursday", "start_time": "09:00", "end_time": "17:00"},
                    {"day": "Friday", "start_time": "09:00", "end_time": "17:00"}
                ],
                skills=fake.text(50)
            )

        self.stdout.write(self.style.SUCCESS("✔ Created PhlebotomistProfile records"))

        # ============================================================
        # 3. CREATE BUSINESS OWNER PROFILES
        # ============================================================
        business_owners = CustomerUser.objects.filter(role="business_owner")

        for bo in business_owners:
            BusinessOwnerProfile.objects.create(
                user=bo,
                business_name=fake.company(),
                business_type=random.choice(["Hospital", "Clinic", "Lab"]),
                business_address=fake.address(),
                contact_person_name=fake.name(),
                business_phone=fake.phone_number(),
                business_description=fake.text(80),
                hourly_pay_rate=random.randint(25, 70),
                weekly_schedule=[
                    {"day": "Monday", "start_time": "09:00", "end_time": "17:00"},
                    {"day": "Tuesday", "start_time": "09:00", "end_time": "17:00"},
                    {"day": "Wednesday", "start_time": "09:00", "end_time": "17:00"},
                    {"day": "Thursday", "start_time": "09:00", "end_time": "17:00"},
                    {"day": "Friday", "start_time": "09:00", "end_time": "17:00"}
                ],
                agree=True
            )

        self.stdout.write(self.style.SUCCESS("✔ Created BusinessOwnerProfile records"))

        # ============================================================
        # 4. CREATE JOBS
        # ============================================================
        for _ in range(100):  # Create 100 jobs
            owner = random.choice(list(business_owners))
            start = datetime.now().replace(hour=random.randint(8, 12), minute=0)
            end = start + timedelta(hours=random.randint(2, 6))

            Job.objects.create(
                title=fake.job(),
                profession_type="Phlebotomy",
                job_info=fake.text(),
                location=fake.address(),
                date=fake.date_between(start_date="-10d", end_date="+10d"),
                start_time=start.time(),
                end_time=end.time(),
                pay_type=random.choice(["hourly", "flat_rate"]),
                pay_rate=random.randint(20, 60),
                job_types=random.choice(["urgent", "full_day", "part_time"]),
                active_status=random.choice(["approved", "pending", "rejected"]),
                created_by=owner
            )

        jobs = Job.objects.all()
        self.stdout.write(self.style.SUCCESS("✔ Created Job records"))

        # ============================================================
        # 5. CREATE TEMP ASSIGNED JOBS
        # ============================================================
        ph_list = list(phlebotomists)

        for _ in range(60):  # Create 60 temporary job assignments
            job = random.choice(jobs)
            assigned_to = random.choice(ph_list)
            start = timezone.now()
            end = start + timedelta(hours=random.randint(1, 8))

            TempAssignedJob.objects.create(
                job=job,
                assigned_to=assigned_to,
                assigned_by=random.choice(all_users),
                assignment_start_time=start,
                assignment_end_time=end,
                status=random.choice(["assigned", "completed", "cancelled"]),
                is_accepted=random.choice([True, False])
            )

        self.stdout.write(self.style.SUCCESS("✔ Created TempAssignedJob records"))

        # ============================================================
        # 6. CREATE APPOINTMENTS
        # ============================================================
        for _ in range(80):  # Create 80 appointments
            user = random.choice(all_users)
            job = random.choice(jobs)

            start_date = fake.date_between(start_date="today", end_date="+5d")
            AppointmentModel.objects.create(
                user=user,
                test_package=job,
                start_date=start_date,
                start_date_start_time="09:00",
                start_date_end_time="11:00",
                end_date=start_date,
                end_date_start_time="12:00",
                end_date_end_time="14:00",
                hospital=job.created_by.full_name,
                location=fake.address(),
                current_medication=fake.text(30),
                known_allergies="None",
                medical_conditions=["Hypertension"],
                initial_fee=50,
                service_fee=9,
                tax_fee=5,
                payment_status=random.choice([True, False])
            )

        self.stdout.write(self.style.SUCCESS("✔ Created AppointmentModel records"))

        # ============================================================
        # 7. CREATE REQUEST FOR JOBS
        # ============================================================
        for _ in range(60):  # Create 60 job requests
            job = random.choice(jobs)
            requested_by = random.choice(all_users)

            RequestForJob.objects.create(
                job=job,
                requested_by=requested_by,
                status=random.choice(["pending", "assigned", "rejected"]),
                is_active=True,
                requested_on=fake.date_this_year(),
                updated_on=fake.date_this_year()
            )

        self.stdout.write(self.style.SUCCESS("✔ Created RequestForJob records"))

        # ============================================================
        # 8. CREATE ACCEPTED ASSIGNED JOBS
        # ============================================================
        for _ in range(60):  # Create 60 accepted job assignments
            job = random.choice(jobs)
            assigned_to = random.choice(ph_list)

            AcceptedAssignedJob.objects.create(
                job=job,
                assigned_to=assigned_to,
                assigned_by=random.choice(all_users),
                accepted_on=fake.date_this_year(),
                is_active=True
            )

        self.stdout.write(self.style.SUCCESS("✔ Created AcceptedAssignedJob records"))

        # ============================================================
        # 9. CREATE COMPLETED ASSIGNED JOBS
        # ============================================================
        for _ in range(60):  # Create 60 completed job assignments
            job = random.choice(jobs)
            completed_by = random.choice(ph_list)

            CompletedAssignedJob.objects.create(
                job=job,
                completed_by=completed_by,
                assigned_by=random.choice(all_users),
                completed_on=fake.date_this_year(),
                is_active=True
            )

        self.stdout.write(self.style.SUCCESS("✔ Created CompletedAssignedJob records"))

        # ============================================================
        # 10. CREATE REPORT USERS
        # ============================================================
        for _ in range(40):  # Create 40 reports
            reporter = random.choice(all_users)
            victim = random.choice(all_users)

            ReportUserModel.objects.create(
                reported_to=victim,
                reported_reason=fake.text(30),
                additional_details=fake.text(50),
                ai_flag_title=fake.text(20),
                ai_flag=random.choice(["low", "medium", "high"]),
                reported_by=reporter
            )

        self.stdout.write(self.style.SUCCESS("✔ Created ReportUserModel records"))

        # ============================================================
        # 11. CREATE PRIVACY POLICY
        # ============================================================
        PrivacyPolicy.objects.create(content=fake.text())

        self.stdout.write(self.style.SUCCESS("✔ Created PrivacyPolicy records"))

        # ============================================================
        # 12. CREATE TERMS AND CONDITIONS
        # ============================================================
        TermsConditions.objects.create(content=fake.text())

        self.stdout.write(self.style.SUCCESS("✔ Created TermsConditions records"))

        # ============================================================
        # 13. CREATE MESSAGES
        # ============================================================
        for user in all_users:
            for _ in range(random.randint(30, 40)):  # Create 30-40 messages per user
                sender = random.choice(all_users)
                receiver = random.choice(all_users)

                Message.objects.create(
                    sender=sender,
                    receiver=receiver,
                    message_type="text",
                    content=fake.text(40),
                    ai_approval_status=random.choice(["approved", "pending", "inappropriate"])
                )

        self.stdout.write(self.style.SUCCESS("✔ Created Message records"))

        # ============================================================
        # 14. CREATE INAPPROPRIATE MESSAGE REPORTS
        # ============================================================
        for _ in range(20):  # Create 20 inappropriate message reports
            sender = random.choice(all_users)
            receiver = random.choice(all_users)

            InappropriateMessageReport.objects.create(
                sender=sender,
                receiver=receiver,
                assigned_job=fake.word(),
                reported_title=fake.sentence(),
                reported_reason=fake.text(40),
                message_content=fake.text(100),
                admin_decision=random.choice(["approved", "pending", "delete", "suspend"])
            )

        self.stdout.write(self.style.SUCCESS("\n🎉 ALL FAKE DATA GENERATED SUCCESSFULLY!"))


        # ============================================================
        # 15. CREATE ACTIVITY LOGS
        # ============================================================
        for user in all_users:
            for _ in range(random.randint(30, 40)):  # Create 30-40 activity logs per user
                ActivityLog.objects.create(
                    user=user,
                    title=fake.sentence(),
                    info=fake.text(),
                    log_time=fake.date_this_year()
                )

        self.stdout.write(self.style.SUCCESS("✔ Created ActivityLog records"))

        # ============================================================
        # 16. CREATE NOTIFICATIONS
        # ============================================================
        for user in all_users:
            for _ in range(random.randint(30, 40)):  # Create 30-40 notifications per user
                NotificationModel.objects.create(
                    user=user,
                    title=fake.sentence(),
                    info=fake.text(),
                    is_read=random.choice([True, False]),
                    created_on=fake.date_this_year()
                )

        self.stdout.write(self.style.SUCCESS("✔ Created NotificationModel records"))
