"""
Opik Client - Centralized Opik SDK Integration
Handles project setup, datasets, and client management
"""

import opik
from opik import Opik
from typing import Optional
from src.core.config import settings
import logging

logger = logging.getLogger(__name__)


class OpikClient:
    """
    Centralized Opik client with full feature access
    
    Provides:
    - Project management
    - Dataset creation
    - Trace logging
    - Evaluation support
    """
    
    def __init__(self):
        self.enabled = False
        self.client: Optional[Opik] = None
        self.project_name = settings.opik_project_name
        
        # Check if API key is set
        if not settings.opik_api_key or settings.opik_api_key == "your_opik_api_key":
            logger.warning(
                "⚠️  Opik API key not configured. "
                "Running without observability. "
                "Get your free key at: https://www.comet.com/opik"
            )
            return
        
        try:
            # Configure Opik SDK
            opik.configure(
                api_key=settings.opik_api_key,
                workspace=settings.opik_workspace,
                url=settings.opik_url
            )
            
            # Initialize client
            self.client = Opik()
            self.enabled = True
            
            logger.info(f"✅ Opik SDK configured successfully")
            # Setup datasets (Project creation is automatic)
            self._ensure_datasets()
            
        except Exception as e:
            logger.error(f"❌ Failed to configure Opik: {e}")
            logger.warning("Continuing without Opik observability")
            self.enabled = False

    # _ensure_project removed
    
    def _ensure_datasets(self):
        """Create evaluation datasets for testing and optimization"""
        if not self.enabled:
            return
        
        datasets = [
            {
                "name": "sona_test_qa",
                "description": "Test Q&A pairs for evaluation validation"
            },
            {
                "name": "sona_training_samples",
                "description": "Sample sessions for agent optimization"
            },
            {
                "name": "sona_evaluation_benchmark",
                "description": "Benchmark dataset for evaluator performance"
            }
        ]
        
        for dataset_info in datasets:
            try:
                self.client.create_dataset(
                    name=dataset_info["name"],
                    description=dataset_info["description"]
                )
                logger.info(f"✅ Created dataset: {dataset_info['name']}")
            except:
                logger.debug(f"Dataset {dataset_info['name']} already exists")
    
    def log_trace(self, name: str, input_data: dict, output_data: dict, metadata: dict = None):
        """Log a trace to Opik"""
        if not self.enabled:
            return
        
        try:
            self.client.log_trace(
                name=name,
                project_name=self.project_name,
                input=input_data,
                output=output_data,
                metadata=metadata or {}
            )
        except Exception as e:
            logger.error(f"Failed to log trace: {e}")
    
    def log_feedback(self, trace_id: str, score: float, name: str, reason: str = None):
        """Log feedback/score for a trace"""
        if not self.enabled:
            return
        
        try:
            self.client.log_feedback_score(
                trace_id=trace_id,
                name=name,
                value=score,
                reason=reason
            )
        except Exception as e:
            logger.error(f"Failed to log feedback: {e}")
    
    def get_dataset(self, name: str):
        """Get dataset by name"""
        if not self.enabled:
            return None
        
        try:
            return self.client.get_dataset(name=name)
        except Exception as e:
            logger.error(f"Failed to get dataset: {e}")
            return None
    
    def create_experiment(self, name: str, dataset_name: str):
        """Create an experiment for A/B testing"""
        if not self.enabled:
            return None
        
        try:
            return self.client.create_experiment(
                name=name,
                dataset_name=dataset_name,
                project_name=self.project_name
            )
        except Exception as e:
            logger.error(f"Failed to create experiment: {e}")
            return None


# Global Opik client instance
opik_client = OpikClient()


# Convenience functions
def is_opik_enabled() -> bool:
    """Check if Opik is enabled and configured"""
    return opik_client.enabled


def get_opik_client() -> Optional[Opik]:
    """Get the Opik client instance"""
    return opik_client.client if opik_client.enabled else None
