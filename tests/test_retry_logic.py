import pytest
import time
from unittest.mock import Mock, patch
from orchestrator.retry_logic import with_retry

@pytest.fixture
def mock_config():
    return {
        'retry': {
            'max_attempts': 3,
            'initial_delay': 0.1,
            'max_delay': 1,
            'exponential_base': 2
        }
    }

def test_successful_execution(mock_config):
    mock_func = Mock(return_value="success")
    
    decorated_func = with_retry(mock_config)(mock_func)
    result = decorated_func()
    
    assert result == "success"
    assert mock_func.call_count == 1

def test_retry_on_failure(mock_config):
    mock_func = Mock(side_effect=[Exception("Test error"), "success"])
    
    decorated_func = with_retry(mock_config)(mock_func)
    result = decorated_func()
    
    assert result == "success"
    assert mock_func.call_count == 2

def test_max_retries_exceeded(mock_config):
    mock_func = Mock(side_effect=Exception("Test error"))
    
    decorated_func = with_retry(mock_config)(mock_func)
    
    with pytest.raises(Exception) as exc_info:
        decorated_func()
    
    assert str(exc_info.value) == "Test error"
    assert mock_func.call_count == mock_config['retry']['max_attempts']

def test_exponential_backoff(mock_config):
    mock_func = Mock(side_effect=[Exception("Test error"), "success"])
    start_time = time.time()
    
    decorated_func = with_retry(mock_config)(mock_func)
    decorated_func()
    
    elapsed_time = time.time() - start_time
    
    # With initial_delay=0.1 and exponential_base=2,
    # the first retry should wait approximately 0.1 seconds
    assert 0.1 <= elapsed_time <= 0.2

def test_retry_with_different_config(mock_config):
    # Modify config for this test
    mock_config['retry']['max_attempts'] = 2
    mock_config['retry']['initial_delay'] = 0.05
    
    mock_func = Mock(side_effect=[Exception("Test error"), "success"])
    
    decorated_func = with_retry(mock_config)(mock_func)
    result = decorated_func()
    
    assert result == "success"
    assert mock_func.call_count == 2

def test_retry_with_logging(mock_config):
    with patch('orchestrator.retry_logic.logger') as mock_logger:
        mock_func = Mock(side_effect=[Exception("Test error"), "success"])
        
        decorated_func = with_retry(mock_config)(mock_func)
        result = decorated_func()
        
        assert result == "success"
        assert mock_func.call_count == 2
        assert mock_logger.error.call_count == 1 