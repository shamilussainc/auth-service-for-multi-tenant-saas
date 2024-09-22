
import resend
from app.settings import settings


class MailManager:
    def __init__(self) -> None:
        self.resend = resend
        self.resend.api_key = settings.RESEND_API_KEY.get_secret_value()
        self.sender_email = settings.RESEND_SENDER_EMAIL

    def __send_mail(self, to_address: str, subject: str, content: str):
        params: resend.Emails.SendParams = {
            "from": self.sender_email,
            "to": [to_address],
            "subject": subject,
            "html": content,
        }
        email = resend.Emails.send(params)

        return email

    def send_user_invite(self, to_address: str, invite_link: str):
        """
        Send an invite email on sign up and invite with a generated link
        """
        subject = "Wellcome!"
        content = f"""
        <p>Welcome!</p>
        <p>Click the following link to complete your signup: <a href="{invite_link}">Activate your account</a></p>
        """
        return self.__send_mail(to_address, subject, content)

    def send_password_update_alert(self, to_address: str):
        """
        Send an password update alert email
        """
        subject = "Password Update Notification"
        content = """
        <p>Hello,</p>
        <p>This is to inform you that your password has been successfully updated.</p>
        """
        return self.__send_mail(to_address, subject, content)

    # 3. Send login alert event email
    def send_login_alert(self, to_address: str):
        """
        Send login alert event email
        """
        subject = "New Login Alert"
        content = """
        <p>Hello,</p>
        <p>We detected a new login to your account. </p>
        """
        return self.__send_mail(to_address, subject, content)


mail_manager = MailManager()
