#!/usr/bin/env python3
"""
Setup script for Terraform Chatbot.
"""

import os
import subprocess
import sys
import json
from pathlib import Path

def check_python_version():
    """Check if Python version is compatible."""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        print(f"   Current version: {sys.version_info.major}.{sys.version_info.minor}")
        return False
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} detected")
    return True

def check_go_installation():
    """Check if Go is installed."""
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
    """Install Python dependencies."""
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

def build_mcp_server():
    """Build the Terraform MCP server."""
    print("🔨 Building Terraform MCP server...")
    
    try:
        # Determine the correct binary name for the platform
        binary_name = "terraform-mcp-server.exe" if os.name == 'nt' else "terraform-mcp-server"
        
        subprocess.run([
            'go', 'build', '-o', binary_name, './cmd/terraform-mcp-server'
        ], check=True)
        
        print(f"✅ Terraform MCP server built successfully: {binary_name}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to build Terraform MCP server: {e}")
        return False

def setup_configuration():
    """Setup configuration file."""
    print("⚙️  Setting up configuration...")
    
    config_file = Path("terraform_gemini_config.json")
    example_config = Path("config.example.json")
    
    if config_file.exists():
        print("✅ Configuration file already exists")
        return True
    
    if example_config.exists():
        # Copy example config
        with open(example_config, 'r') as f:
            config_data = json.load(f)
        
        # Get API key from user
        api_key = input("\n🔑 Enter your Gemini API key (or press Enter to skip): ").strip()
        if api_key:
            config_data["gemini"]["api_key"] = api_key
        
        # Save configuration
        with open(config_file, 'w') as f:
            json.dump(config_data, f, indent=2)
        
        print(f"✅ Configuration saved to {config_file}")
        
        if not api_key:
            print("⚠️  Remember to set your GEMINI_API_KEY in the config file")
            print("   Get your API key from: https://makersuite.google.com/app/apikey")
        
        return True
    else:
        print("❌ Example configuration file not found")
        return False

def test_setup():
    """Test the setup."""
    print("🧪 Testing setup...")
    
    # Check if MCP server binary exists
    binary_name = "terraform-mcp-server.exe" if os.name == 'nt' else "terraform-mcp-server"
    if not Path(binary_name).exists():
        print(f"❌ MCP server binary not found: {binary_name}")
        return False
    
    # Test MCP server
    try:
        result = subprocess.run([f"./{binary_name}", "--help"], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print("✅ MCP server is working")
        else:
            print("❌ MCP server test failed")
            return False
    except Exception as e:
        print(f"❌ Error testing MCP server: {e}")
        return False
    
    print("✅ Setup test completed successfully")
    return True

def main():
    """Main setup function."""
    print("🚀 Terraform Chatbot Setup")
    print("=" * 40)
    
    steps = [
        ("Checking Python version", check_python_version),
        ("Checking Go installation", check_go_installation),
        ("Installing Python dependencies", install_python_dependencies),
        ("Building Terraform MCP server", build_mcp_server),
        ("Setting up configuration", setup_configuration),
        ("Testing setup", test_setup),
    ]
    
    for step_name, step_func in steps:
        print(f"\n{step_name}...")
        if not step_func():
            print(f"\n❌ Setup failed at: {step_name}")
            sys.exit(1)
    
    print("\n🎉 Setup completed successfully!")
    print("\n📋 Next steps:")
    print("1. Set your GEMINI_API_KEY in terraform_gemini_config.json")
    print("2. Run the web chatbot: python web_chatbot.py")
    print("3. Access the interface: http://localhost:3030")
    print("\n💡 For help, check the README.md file.")

if __name__ == "__main__":
    main()