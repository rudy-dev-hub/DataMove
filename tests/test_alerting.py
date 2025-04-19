import pytest
from unittest.mock import Mock, patch
from orchestrator.alerting import AlertManager

@pytest.fixture
def mock_config():
    return {
        'alerts': {
            'email': {
                'enabled': True,
                'sender': 'test@example.com',
                'recipients': ['recipient@example.com'],
                'smtp_server': 'smtp.test.com',
                'smtp_port': 587,
                'username': 'test_user',
                'password': 'test_pass',
                'on_failure': True,
                'on_success': False
            },
            'slack': {
                'enabled': True,
                'webhook_url': 'https://hooks.slack.com/services/test',
                'channel': '#test-channel',
                'on_failure': True,
                'on_success': False
            }
        }
    }

@pytest.fixture
def alert_manager(mock_config):
    return AlertManager(mock_config)

def test_send_email_alert_success(alert_manager):
    with patch('smtplib.SMTP') as mock_smtp:
        # Configure mock
        mock_smtp_instance = Mock()
        mock_smtp.return_value.__enter__.return_value = mock_smtp_instance
        
        # Test email alert
        alert_manager.send_email_alert(
            subject="Test Subject",
            message="Test Message",
            is_error=True
        )
        
        # Verify SMTP calls
        mock_smtp_instance.starttls.assert_called_once()
        mock_smtp_instance.login.assert_called_once_with(
            alert_manager.config['alerts']['email']['username'],
            alert_manager.config['alerts']['email']['password']
        )
        mock_smtp_instance.send_message.assert_called_once()

def test_send_email_alert_disabled(alert_manager):
    alert_manager.config['alerts']['email']['enabled'] = False
    
    with patch('smtplib.SMTP') as mock_smtp:
        alert_manager.send_email_alert(
            subject="Test Subject",
            message="Test Message",
            is_error=True
        )
        mock_smtp.assert_not_called()

def test_send_slack_alert_success(alert_manager):
    with patch('slack_sdk.WebClient') as mock_client:
        # Configure mock
        mock_client_instance = Mock()
        mock_client.return_value = mock_client_instance
        
        # Test Slack alert
        alert_manager.send_slack_alert(
            message="Test Message",
            is_error=True
        )
        
        # Verify Slack API call
        mock_client_instance.chat_postMessage.assert_called_once_with(
            channel=alert_manager.config['alerts']['slack']['channel'],
            text="[ERROR] Test Message"
        )

def test_send_slack_alert_disabled(alert_manager):
    alert_manager.config['alerts']['slack']['enabled'] = False
    
    with patch('slack_sdk.WebClient') as mock_client:
        alert_manager.send_slack_alert(
            message="Test Message",
            is_error=True
        )
        mock_client.assert_not_called()

def test_send_alert_all_channels(alert_manager):
    with patch('smtplib.SMTP') as mock_smtp, \
         patch('slack_sdk.WebClient') as mock_client:
        # Configure mocks
        mock_smtp_instance = Mock()
        mock_smtp.return_value.__enter__.return_value = mock_smtp_instance
        
        mock_client_instance = Mock()
        mock_client.return_value = mock_client_instance
        
        # Test sending to all channels
        alert_manager.send_alert(
            subject="Test Subject",
            message="Test Message",
            is_error=True
        )
        
        # Verify both channels were used
        mock_smtp_instance.send_message.assert_called_once()
        mock_client_instance.chat_postMessage.assert_called_once() 