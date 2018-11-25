from django.core.mail import send_mail
from django.conf import settings


class SendGrid:
    """
    This class let us sends mails by SendGrid service.
    """

    @classmethod
    def send_notification_coach(cls, member, coach_email):
        """
        This method send a email by SendGrid service.
        :param member: Name of member e.g Linux Torvalds
        :param coach_email: Coach Email e.g email@domain.com
        :return None 
        """
        member = member.title()
        try:
            send_mail(
                'Un miembro necesita ayuda',
                f'El miembro {member} necesita de tu ayuda, contáctalo.',
                settings.EMAIL_HOST_USER,
                [coach_email],
                fail_silently=False,
            )
        except Exception as e:
            print(e)
        
