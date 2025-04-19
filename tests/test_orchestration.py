import pytest
from unittest.mock import Mock, patch
from orchestrator.trigger_pipeline import PipelineOrchestrator

@pytest.fixture
def mock_config():
    return {
        'adf': {
            'subscription_id': 'test-subscription',
            'resource_group': 'test-resource-group',
            'factory_name': 'test-factory',
            'pipeline_name': 'test-pipeline'
        },
        'databricks': {
            'workspace_url': 'https://test-workspace.cloud.databricks.com',
            'cluster_id': 'test-cluster',
            'notebook_path': '/test/notebook'
        },
        'retry': {
            'max_attempts': 3,
            'initial_delay': 1,
            'max_delay': 60,
            'exponential_base': 2
        },
        'alerts': {
            'email': {
                'enabled': True,
                'recipients': ['test@example.com'],
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
        },
        'logging': {
            'level': 'INFO',
            'format': 'json',
            'output_file': 'logs/test.log'
        }
    }

@pytest.fixture
def mock_orchestrator(mock_config):
    with patch('yaml.safe_load', return_value=mock_config):
        return PipelineOrchestrator('test_config.yaml')

def test_trigger_adf_pipeline(mock_orchestrator):
    # Mock ADF client response
    mock_run_response = Mock()
    mock_run_response.run_id = 'test-run-id'
    mock_orchestrator.adf_client.pipelines.create_run.return_value = mock_run_response

    # Test pipeline trigger
    run_id = mock_orchestrator.trigger_adf_pipeline()
    
    assert run_id == 'test-run-id'
    mock_orchestrator.adf_client.pipelines.create_run.assert_called_once()

def test_run_databricks_notebook(mock_orchestrator):
    # Mock Databricks client response
    mock_job = Mock()
    mock_job.job_id = 'test-job-id'
    mock_orchestrator.databricks_client.jobs.create.return_value = mock_job

    # Test notebook execution
    job_id = mock_orchestrator.run_databricks_notebook()
    
    assert job_id == 'test-job-id'
    mock_orchestrator.databricks_client.jobs.create.assert_called_once()

def test_execute_pipeline_success(mock_orchestrator):
    # Mock successful pipeline execution
    mock_orchestrator.trigger_adf_pipeline = Mock(return_value='test-run-id')
    mock_orchestrator.run_databricks_notebook = Mock(return_value='test-job-id')

    # Test complete pipeline execution
    mock_orchestrator.execute_pipeline()
    
    mock_orchestrator.trigger_adf_pipeline.assert_called_once()
    mock_orchestrator.run_databricks_notebook.assert_called_once()

def test_execute_pipeline_failure(mock_orchestrator):
    # Mock pipeline failure
    mock_orchestrator.trigger_adf_pipeline = Mock(side_effect=Exception('Test error'))

    # Test pipeline failure handling
    with pytest.raises(Exception):
        mock_orchestrator.execute_pipeline()
    
    mock_orchestrator.trigger_adf_pipeline.assert_called_once()
    mock_orchestrator.run_databricks_notebook.assert_not_called() 