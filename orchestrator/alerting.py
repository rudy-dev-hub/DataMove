import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from .logger import get_logger

logger = get_logger()

class AlertManager:
    def __init__(self, config):
        self.config = config
        self.slack_client = WebClient(token=config['alerts']['slack']['webhook_url']) if config['alerts']['slack']['enabled'] else None

    def send_email_alert(self, subject, message, is_error=False):
        """Send email alert if enabled and conditions are met."""
        if not self.config['alerts']['email']['enabled']:
            return
        
        if (is_error and not self.config['alerts']['email']['on_failure']) or \
           (not is_error and not self.config['alerts']['email']['on_success']):
            return

        try:
            msg = MIMEMultipart()
            msg['From'] = self.config['alerts']['email']['sender']
            msg['To'] = ', '.join(self.config['alerts']['email']['recipients'])
            msg['Subject'] = f"[{'ERROR' if is_error else 'SUCCESS'}] {subject}"

            msg.attach(MIMEText(message, 'plain'))

            with smtplib.SMTP(self.config['alerts']['email']['smtp_server'], self.config['alerts']['email']['smtp_port']) as server:
                server.starttls()
                server.login(self.config['alerts']['email']['username'], self.config['alerts']['email']['password'])
                server.send_message(msg)

            logger.info("email_alert_sent", subject=subject, recipients=self.config['alerts']['email']['recipients'])
        except Exception as e:
            logger.error("email_alert_failed", error=str(e), subject=subject)

    def send_slack_alert(self, message, is_error=False):
        """Send Slack alert if enabled and conditions are met."""
        if not self.config['alerts']['slack']['enabled']:
            return
        
        if (is_error and not self.config['alerts']['slack']['on_failure']) or \
           (not is_error and not self.config['alerts']['slack']['on_success']):
            return

        try:
            response = self.slack_client.chat_postMessage(
                channel=self.config['alerts']['slack']['channel'],
                text=f"[{'ERROR' if is_error else 'SUCCESS'}] {message}"
            )
            logger.info("slack_alert_sent", message=message, channel=self.config['alerts']['slack']['channel'])
        except SlackApiError as e:
            logger.error("slack_alert_failed", error=str(e), message=message)

    def send_alert(self, subject, message, is_error=False):
        """Send alerts through all configured channels."""
        self.send_email_alert(subject, message, is_error)
        self.send_slack_alert(message, is_error) 