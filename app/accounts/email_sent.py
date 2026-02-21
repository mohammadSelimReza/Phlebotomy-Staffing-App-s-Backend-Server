from django.core.mail import send_mail
from django.conf import settings



def send_warning_email(user_email, report_reason):
    subject = "Warning: Reported Behavior"
    message = f"Dear User,\n\nYou have been reported for the following behavior: {report_reason}. Please refrain from engaging in such activities.\n\nBest regards,\nAdmin Team"
    from_email = settings.EMAIL_HOST_USER
    
    send_mail(subject, message, from_email, [user_email])


def send_suspened_email(user_email, report_reason):
    subject = "Suspension Notice"
    message = f"Dear User,\n\nYour account has been suspended due to the following behavior: {report_reason}. Please contact support for more details.\n\nBest regards,\nAdmin Team"
    from_email = settings.EMAIL_HOST_USER
    
    send_mail(subject, message, from_email, [user_email])