from django.db import models

class Message(models.Model):
    TEXT = "text"
    FILE = "file"
    IMAGE = "image"
    MESSAGE_TYPES = [
        (TEXT, "Text"),
        (FILE, "File"),
        (IMAGE, "Image")
    ]

    sender = models.ForeignKey("accounts.CustomerUser", on_delete=models.CASCADE, related_name="sent_messages")
    receiver = models.ForeignKey("accounts.CustomerUser", on_delete=models.CASCADE, related_name="received_messages")
    message_type = models.CharField(max_length=10, choices=MESSAGE_TYPES)
    content = models.TextField(blank=True, null=True)
    file_url = models.URLField(blank=True, null=True)
    ai_approval_status = models.CharField(
        max_length=50,
        choices=[("approved", "Approved"), ("pending", "Pending"), ("inappropriate", "Inappropriate")],
        default="pending"
    )
    admin_decision = models.CharField(
        max_length=50,
        choices=[("approved", "Approved"), ("pending", "Pending"), ("delete", "Delete"), ('suspend', 'Suspend')],
        default="pending"
    )
    sent_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message from {self.sender.email} to {self.receiver.email} on {self.sent_on}"

class InappropriateMessageReport(models.Model):
    sender = models.ForeignKey("accounts.CustomerUser", on_delete=models.SET_NULL, null=True, related_name="inappropriate_messages_sent")
    receiver = models.ForeignKey("accounts.CustomerUser", on_delete=models.CASCADE, null=True, related_name="inappropriate_messages_received")
    
    message = models.ForeignKey(Message, on_delete=models.SET_NULL, null=True, related_name="inappropriate_reports")

    
    assigned_job = models.CharField(max_length=255, blank=True, null=True)
    reported_reason = models.TextField(blank=True, null=True)
    reported_title = models.CharField(max_length=255, blank=True, null=True)
    message_content = models.TextField()
    admin_decision = models.CharField(
        max_length=50,
        choices=[("approved", "Approved"), ("pending", "Pending"), ("delete", "Delete"), ('suspend', 'Suspend')],
        default="pending"
    )
    created_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Inappropriate message report by {self.sender.full_name} to {self.receiver.full_name} on {self.created_on}"
