#!/usr/bin/env python3
"""
Setup script for Terraform MCP + Gemini integration.
"""

import os
import subprocess
import sys
from pathlib import Path
import json

def check_python_version():
    """Check if Python version is compatible."""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        return False
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} detected")
    return True

def check_go_installation():
    """Check if Go is installed for building the MCP server."""
    try:
        result = subprocess.run(['go', 'version'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Go detected: {result.stdout.strip()}")
            return True
    except FileNotFoundError:
        pass
    
    print("❌ Go is not installed or not in PATH")
    print("   Please install Go from https://golang.org/dl/")
    return False

def install_python_dependencies():
    """Install required Python packages."""
    print("📦 Installing Python dependencies...")
    
    try:
        subprocess.run([
            sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'
        ], check=True)
        print("✅ Python dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install Python dependencies: {e}")
        return False

def build_terraform_mcp_server():
    """Build the Terraform MCP server."""
    print("🔨 Building Terraform MCP server...")
    
    try:
        # Build the server
        subprocess.run([
            'go', 'build', '-o', 'terraform-mcp-server', 
            './cmd/terraform-mcp-server'
        ], check=True, cwd='.')
        
        print("✅ Terraform MCP server built successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to build Terraform MCP server: {e}")
        return False

def setup_environment():
    """Setup environment variables and configuration."""
    print("⚙️  Setting up environment...")
    
    # Check for GEMINI_API_KEY
    if not os.getenv('GEMINI_API_KEY'):
        print("⚠️  GEMINI_API_KEY environment variable not set")
        print("   Please get your API key from: https://makersuite.google.com/app/apikey")
        print("   Then set it as an environment variable:")
        print("   export GEMINI_API_KEY='your-api-key-here'")
        return False
    
    print("✅ GEMINI_API_KEY found")
    return True

def create_sample_config():
    """Create a sample configuration file."""
    print("📝 Creating sample configuration...")
    
    config = {
        "gemini": {
            "api_key": "",
            "model_name": "gemini-1.5-pro",
            "temperature": 0.1,
            "max_tokens": 8192
        },
        "mcp_server": {
            "server_path": "./terraform-mcp-server",
            "server_args": ["stdio"],
            "timeout": 30,
            "retry_attempts": 3,
            "log_level": "INFO"
        },
        "conversation_history_limit": 50,
        "enable_analytics": True,
        "log_file": "terraform_gemini.log"
    }
    
    with open('terraform_gemini_config.json', 'w') as f:
        json.dump(config, f, indent=2)
    
    print("✅ Sample configuration created: terraform_gemini_config.json")
    return True

def run_tests():
    """Run basic tests to verify the setup."""
    print("🧪 Running basic tests...")
    
    try:
        # Test MCP connection
        result = subprocess.run([
            sys.executable, 'test_mcp_connection.py'
        ], capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print("✅ MCP server connection test passed")
            return True
        else:
            print(f"❌ MCP server connection test failed: {result.stderr}")
            return False
    except subprocess.TimeoutExpired:
        print("❌ MCP server connection test timed out")
        return False
    except Exception as e:
        print(f"❌ Error running tests: {e}")
        return False

def main():
    """Main setup function."""
    print("🚀 Setting up Terraform MCP + Gemini Integration\n")
    
    steps = [
        ("Checking Python version", check_python_version),
        ("Checking Go installation", check_go_installation),
        ("Installing Python dependencies", install_python_dependencies),
        ("Building Terraform MCP server", build_terraform_mcp_server),
        ("Setting up environment", setup_environment),
        ("Creating sample configuration", create_sample_config),
    ]
    
    for step_name, step_func in steps:
        print(f"\n{step_name}...")
        if not step_func():
            print(f"\n❌ Setup failed at: {step_name}")
            sys.exit(1)
    
    print("\n🎉 Setup completed successfully!")
    print("\nNext steps:")
    print("1. Set your GEMINI_API_KEY environment variable if not already set")
    print("2. Run the integration: python terraform_gemini_integration.py")
    print("3. Or run tests: python test_mcp_connection.py")
    print("\nFor help, check the README.md file.")

if __name__ == "__main__":
    main()