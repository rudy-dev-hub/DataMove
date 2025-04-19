import yaml
from azure.identity import DefaultAzureCredential
from azure.mgmt.datafactory import DataFactoryManagementClient
from databricks.sdk import WorkspaceClient
from databricks.sdk.service.jobs import CreateJob, JobSettings, NotebookTask
from .logger import setup_logger, get_logger
from .retry_logic import with_retry
from .alerting import AlertManager

class PipelineOrchestrator:
    def __init__(self, config_path):
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        self.logger = setup_logger(self.config)
        self.alert_manager = AlertManager(self.config)
        
        # Initialize Azure clients
        self.credential = DefaultAzureCredential()
        self.adf_client = DataFactoryManagementClient(
            credential=self.credential,
            subscription_id=self.config['adf']['subscription_id']
        )
        
        # Initialize Databricks client with authentication
        self.databricks_client = WorkspaceClient(
            host=self.config['databricks']['workspace_url'],
            token=self.config['databricks'].get('token'),  # Get token from config
            cluster_id=self.config['databricks']['cluster_id']
        )

    @with_retry
    def trigger_adf_pipeline(self):
        """Trigger Azure Data Factory pipeline."""
        try:
            self.logger.info("triggering_adf_pipeline", pipeline_name=self.config['adf']['pipeline_name'])
            
            # Create pipeline run
            run_response = self.adf_client.pipelines.create_run(
                resource_group_name=self.config['adf']['resource_group'],
                factory_name=self.config['adf']['factory_name'],
                pipeline_name=self.config['adf']['pipeline_name']
            )
            
            self.logger.info("adf_pipeline_triggered", run_id=run_response.run_id)
            return run_response.run_id
            
        except Exception as e:
            self.logger.error("adf_pipeline_trigger_failed", error=str(e))
            self.alert_manager.send_alert(
                "ADF Pipeline Trigger Failed",
                f"Failed to trigger ADF pipeline: {str(e)}",
                is_error=True
            )
            raise

    @with_retry
    def run_databricks_notebook(self):
        """Run Databricks notebook."""
        try:
            self.logger.info("running_databricks_notebook", notebook_path=self.config['databricks']['notebook_path'])
            
            # Create job settings
            job_settings = JobSettings(
                name="Data Processing Job",
                tasks=[NotebookTask(
                    notebook_path=self.config['databricks']['notebook_path'],
                    base_parameters={}
                )]
            )
            
            # Create and run job
            job = self.databricks_client.jobs.create(
                name=job_settings.name,
                tasks=job_settings.tasks
            )
            
            self.logger.info("databricks_job_created", job_id=job.job_id)
            return job.job_id
            
        except Exception as e:
            self.logger.error("databricks_job_failed", error=str(e))
            self.alert_manager.send_alert(
                "Databricks Job Failed",
                f"Failed to run Databricks notebook: {str(e)}",
                is_error=True
            )
            raise

    def execute_pipeline(self):
        """Execute the complete pipeline."""
        try:
            # Trigger ADF pipeline
            adf_run_id = self.trigger_adf_pipeline()
            
            # Run Databricks notebook
            databricks_job_id = self.run_databricks_notebook()
            
            self.logger.info("pipeline_execution_complete", 
                          adf_run_id=adf_run_id, 
                          databricks_job_id=databricks_job_id)
            
            self.alert_manager.send_alert(
                "Pipeline Execution Successful",
                f"ADF Run ID: {adf_run_id}\nDatabricks Job ID: {databricks_job_id}",
                is_error=False
            )
            
        except Exception as e:
            self.logger.error("pipeline_execution_failed", error=str(e))
            self.alert_manager.send_alert(
                "Pipeline Execution Failed",
                f"Pipeline execution failed: {str(e)}",
                is_error=True
            )
            raise 