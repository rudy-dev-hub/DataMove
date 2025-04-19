#!/bin/bash

# Set environment variables
export PYTHONPATH=$PYTHONPATH:$(pwd)

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the pipeline
python -c "
from orchestrator.trigger_pipeline import PipelineOrchestrator

orchestrator = PipelineOrchestrator('pipelines/pipeline_config.yaml')
orchestrator.execute_pipeline()
" 