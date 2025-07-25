#!/usr/bin/env python3
"""
Setup script for Gemini API key configuration.
"""

import os
import json
from pathlib import Path

def setup_gemini_api_key():
    """Setup Gemini API key interactively."""
    print("🔑 Gemini API Key Setup")
    print("=" * 30)
    
    print("\n📋 Steps to get your Gemini API key:")
    print("1. Go to: https://makersuite.google.com/app/apikey")
    print("2. Sign in with your Google account")
    print("3. Click 'Create API Key'")
    print("4. Copy the generated API key")
    
    print("\n💡 You can set the API key in two ways:")
    print("1. Environment variable (temporary)")
    print("2. Configuration file (persistent)")
    
    choice = input("\nChoose method (1 or 2): ").strip()
    
    if choice == "1":
        api_key = input("\nEnter your Gemini API key: ").strip()
        if api_key:
            print(f"\n📝 To set environment variable, run:")
            print(f"set GEMINI_API_KEY={api_key}")
            print("\nOr in PowerShell:")
            print(f"$env:GEMINI_API_KEY='{api_key}'")
            
            # Try to set it for current session
            os.environ['GEMINI_API_KEY'] = api_key
            print("✅ API key set for current session")
        else:
            print("❌ No API key provided")
    
    elif choice == "2":
        api_key = input("\nEnter your Gemini API key: ").strip()
        if api_key:
            # Update config file
            config_path = Path("terraform_gemini_config.json")
            
            if config_path.exists():
                with open(config_path, 'r') as f:
                    config = json.load(f)
            else:
                config = {
                    "gemini": {},
                    "mcp_server": {
                        "server_path": "./terraform-mcp-server.exe",
                        "server_args": ["stdio"],
                        "timeout": 30,
                        "retry_attempts": 3,
                        "log_level": "INFO"
                    },
                    "conversation_history_limit": 50,
                    "enable_analytics": True,
                    "log_file": "terraform_gemini.log"
                }
            
            config["gemini"]["api_key"] = api_key
            config["gemini"]["model_name"] = "gemini-1.5-pro"
            config["gemini"]["temperature"] = 0.1
            config["gemini"]["max_tokens"] = 8192
            
            with open(config_path, 'w') as f:
                json.dump(config, f, indent=2)
            
            print(f"✅ API key saved to {config_path}")
            print("✅ Configuration updated")
        else:
            print("❌ No API key provided")
    
    else:
        print("❌ Invalid choice")
    
    print("\n🎉 Setup complete! You can now run:")
    print("py s3_terraform_generator.py")

if __name__ == "__main__":
    setup_gemini_api_key()