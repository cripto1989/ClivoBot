from django.core.mail import send_mail
from django.conf import settings


class SendGrid:
    """
    This class let us sends mails by SendGrid service.
    """

    @classmethod
    def send_notification_coach(cls, member, list_emails):
        """
        This method send a email by SendGrid service.
        :param member: Name of member e.g Linux Torvalds
        :param list_emails: Coach Email e.g ['email@domain.com','another@domain.com']
        :return None 
        """
        member = member.title()
        try:
            send_mail(
                'A member needs your help',
                f'The member "{member}" needs your support, give assistance immediateley, please.',
                settings.EMAIL_HOST_USER,
                list_emails,
                fail_silently=False,
            )
        except Exception as e:
            print(e)
        
