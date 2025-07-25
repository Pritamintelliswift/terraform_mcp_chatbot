#!/usr/bin/env python3
"""
Configuration management for Terraform MCP + Gemini integration.
"""

import json
import os
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Dict, List, Optional


@dataclass
class GeminiConfig:
    """Configuration for Gemini LLM."""
    api_key: str = ""
    model_name: str = "gemini-1.5-pro"
    temperature: float = 0.1
    max_tokens: int = 8192
    safety_settings: Dict = None
    
    def __post_init__(self):
        if self.safety_settings is None:
            self.safety_settings = {
                "HARM_CATEGORY_HARASSMENT": "BLOCK_MEDIUM_AND_ABOVE",
                "HARM_CATEGORY_HATE_SPEECH": "BLOCK_MEDIUM_AND_ABOVE",
                "HARM_CATEGORY_SEXUALLY_EXPLICIT": "BLOCK_MEDIUM_AND_ABOVE",
                "HARM_CATEGORY_DANGEROUS_CONTENT": "BLOCK_MEDIUM_AND_ABOVE"
            }


@dataclass
class MCPServerConfig:
    """Configuration for MCP server connection."""
    server_path: str = "terraform-mcp-server"
    server_args: List[str] = None
    timeout: int = 30
    retry_attempts: int = 3
    log_level: str = "INFO"
    
    def __post_init__(self):
        if self.server_args is None:
            self.server_args = ["stdio"]


@dataclass
class IntegrationConfig:
    """Main configuration for the integration."""
    gemini: GeminiConfig
    mcp_server: MCPServerConfig
    conversation_history_limit: int = 50
    enable_analytics: bool = True
    log_file: str = "terraform_gemini.log"
    config_file: str = "terraform_gemini_config.json"


class ConfigManager:
    """Manages configuration loading and saving."""
    
    def __init__(self, config_path: str = "terraform_gemini_config.json"):
        self.config_path = Path(config_path)
        self.config: Optional[IntegrationConfig] = None
    
    def load_config(self) -> IntegrationConfig:
        """Load configuration from file or create default."""
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r') as f:
                    data = json.load(f)
                
                # Create config objects from loaded data
                gemini_config = GeminiConfig(**data.get('gemini', {}))
                mcp_config = MCPServerConfig(**data.get('mcp_server', {}))
                
                self.config = IntegrationConfig(
                    gemini=gemini_config,
                    mcp_server=mcp_config,
                    **{k: v for k, v in data.items() if k not in ['gemini', 'mcp_server']}
                )
            except Exception as e:
                print(f"Error loading config: {e}")
                self.config = self._create_default_config()
        else:
            self.config = self._create_default_config()
            self.save_config()
        
        # Override with environment variables
        self._apply_env_overrides()
        return self.config
    
    def save_config(self):
        """Save current configuration to file."""
        if not self.config:
            return
        
        config_dict = asdict(self.config)
        with open(self.config_path, 'w') as f:
            json.dump(config_dict, f, indent=2)
    
    def _create_default_config(self) -> IntegrationConfig:
        """Create default configuration."""
        return IntegrationConfig(
            gemini=GeminiConfig(),
            mcp_server=MCPServerConfig()
        )
    
    def _apply_env_overrides(self):
        """Apply environment variable overrides."""
        if not self.config:
            return
        
        # Gemini API key from environment
        if os.getenv("GEMINI_API_KEY"):
            self.config.gemini.api_key = os.getenv("GEMINI_API_KEY")
        
        # MCP server path from environment
        if os.getenv("TERRAFORM_MCP_SERVER_PATH"):
            self.config.mcp_server.server_path = os.getenv("TERRAFORM_MCP_SERVER_PATH")
        
        # Log level from environment
        if os.getenv("LOG_LEVEL"):
            self.config.mcp_server.log_level = os.getenv("LOG_LEVEL")


def get_config() -> IntegrationConfig:
    """Get the current configuration."""
    manager = ConfigManager()
    return manager.load_config()


if __name__ == "__main__":
    # Create and display default configuration
    config = get_config()
    print("Current configuration:")
    print(json.dumps(asdict(config), indent=2))