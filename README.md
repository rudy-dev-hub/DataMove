# DataMove

A robust data pipeline orchestration system built with Azure Data Factory and Databricks.

## Overview

DataMove is a production-grade data pipeline orchestration system that combines the power of Azure Data Factory (ADF) and Databricks for reliable data processing and transformation. The system includes comprehensive error handling, retry mechanisms, and alerting capabilities.

## Project Structure

```
DataMove/
├── pipelines/              # Pipeline definitions and configurations
├── orchestrator/          # Pipeline orchestration and utilities
├── tests/                 # Test suite
├── notebooks/             # Databricks notebooks for development
└── docs/                  # Documentation and diagrams
```

## Features

- Azure Data Factory pipeline integration
- Databricks notebook execution
- Configurable retry logic with exponential backoff
- Multi-channel alerting (Email/Slack)
- Comprehensive logging
- Production-ready error handling

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Configure your Azure credentials:
- Set up Azure CLI authentication
- Configure Databricks workspace access

3. Update pipeline configuration in `pipelines/pipeline_config.yaml`

## Usage

Run the pipeline using the provided shell script:
```bash
./run_pipeline.sh
```

## Development

- Use `notebooks/databricks_pipeline_dev.ipynb` for prototyping
- Add new pipeline configurations in `pipelines/`
- Extend orchestration logic in `orchestrator/`

## Testing

Run the test suite:
```bash
python -m pytest tests/
```

## License

MIT License

---

Made with ❤️ by Rudresh Upadhyaya 