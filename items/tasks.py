from huey.contrib.djhuey import db_task
from django.core.mail import send_mail
from django.conf import settings
import logging

logger = logging.getLogger('task_notifications')

@db_task()
def send_task_notification_email(task_id, task_description, category, date, owner_email):
    """
    Send an email notification when a new task is created.
    The db_task decorator ensures database connections are properly managed.
    """
    subject = f"New Task Added: {task_description[:30]}..."
    message = f"""
    Hello,
    
    A new task has been added to your Task Manager:
    
    Description: {task_description}
    Category: {category}
    Due Date: {date}
    
    You can view this task in your Task Manager application.
    
    Best regards,
    Task Manager Team
    """
    
    try:
        # Send the email
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[owner_email],
            fail_silently=False,
        )
        logger.info(f"Successfully sent notification email for task {task_id} to {owner_email}")
        return True
    except Exception as e:
        logger.error(f"Failed to send notification email for task {task_id}: {str(e)}")
        # Re-raise to mark task as failed in Huey
        raise