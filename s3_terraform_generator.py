#!/usr/bin/env python3
"""
S3 Terraform Code Generator using Gemini LLM + Terraform MCP Server

This script uses Gemini LLM to generate Terraform code for S3 buckets
by fetching real Terraform modules and provider documentation.
"""

import asyncio
import json
import logging
import os
import sys
from pathlib import Path
from datetime import datetime

import google.generativeai as genai
from config import get_config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class S3TerraformGenerator:
    """Generate S3 Terraform code using Gemini LLM and MCP server."""
    
    def __init__(self):
        self.config = get_config()
        self.server_path = Path("terraform-mcp-server.exe")
        
        # Configure Gemini
        if not self.config.gemini.api_key:
            raise ValueError("GEMINI_API_KEY is required")
        
        genai.configure(api_key=self.config.gemini.api_key)
        self.model = genai.GenerativeModel(
            self.config.gemini.model_name,
            generation_config={
                "temperature": 0.1,  # Lower temperature for more consistent code
                "max_output_tokens": 4096,
            }
        )
    
    async def get_s3_provider_docs(self):
        """Get S3 provider documentation from MCP server."""
        print("🔍 Fetching S3 provider documentation...")
        
        import subprocess
        
        # Initialize and get S3 docs
        init_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "s3-generator", "version": "1.0.0"}
            }
        }
        
        s3_docs_request = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/call",
            "params": {
                "name": "resolveProviderDocID",
                "arguments": {
                    "providerName": "aws",
                    "providerNamespace": "hashicorp",
                    "serviceSlug": "s3",
                    "providerDataType": "resources"
                }
            }
        }
        
        try:
            process = subprocess.Popen([
                str(self.server_path), "stdio"
            ], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            
            input_data = json.dumps(init_request) + "\n" + json.dumps(s3_docs_request) + "\n"
            stdout, stderr = process.communicate(input=input_data, timeout=30)
            
            if stdout:
                lines = stdout.strip().split('\n')
                for line in lines:
                    if line.strip():
                        try:
                            response = json.loads(line)
                            if response.get('id') == 2 and 'result' in response:
                                content = response['result']['content'][0]['text']
                                print("✅ Retrieved S3 provider documentation")
                                return content
                        except json.JSONDecodeError:
                            continue
            
            return None
            
        except Exception as e:
            print(f"❌ Error getting S3 docs: {e}")
            return None
    
    async def search_s3_modules(self):
        """Search for S3 modules from MCP server."""
        print("🔍 Searching for S3 Terraform modules...")
        
        import subprocess
        
        init_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "s3-generator", "version": "1.0.0"}
            }
        }
        
        s3_modules_request = {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {
                "name": "searchModules",
                "arguments": {
                    "moduleQuery": "aws s3 bucket",
                    "currentOffset": 0
                }
            }
        }
        
        try:
            process = subprocess.Popen([
                str(self.server_path), "stdio"
            ], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            
            input_data = json.dumps(init_request) + "\n" + json.dumps(s3_modules_request) + "\n"
            stdout, stderr = process.communicate(input=input_data, timeout=30)
            
            if stdout:
                lines = stdout.strip().split('\n')
                for line in lines:
                    if line.strip():
                        try:
                            response = json.loads(line)
                            if response.get('id') == 3 and 'result' in response:
                                content = response['result']['content'][0]['text']
                                print("✅ Retrieved S3 module information")
                                return content
                        except json.JSONDecodeError:
                            continue
            
            return None
            
        except Exception as e:
            print(f"❌ Error searching S3 modules: {e}")
            return None
    
    async def generate_s3_terraform_code(self, requirements):
        """Generate S3 Terraform code based on requirements."""
        print("🤖 Generating Terraform code with Gemini LLM...")
        
        # Get provider docs and modules
        provider_docs = await self.get_s3_provider_docs()
        module_info = await self.search_s3_modules()
        
        # Create comprehensive prompt
        prompt = f"""You are a Terraform expert. Generate complete, production-ready Terraform code for AWS S3 buckets based on the user requirements.

USER REQUIREMENTS:
{requirements}

AVAILABLE S3 PROVIDER DOCUMENTATION:
{provider_docs or "Use standard AWS provider S3 resources"}

AVAILABLE S3 MODULES:
{module_info or "Use standard aws_s3_bucket resources"}

INSTRUCTIONS:
1. Generate complete Terraform code including:
   - Provider configuration
   - S3 bucket resource(s)
   - Appropriate bucket policies and configurations
   - Security best practices (encryption, versioning, etc.)
   - Output values

2. Include comments explaining each section

3. Follow Terraform best practices:
   - Use latest AWS provider syntax
   - Include proper resource naming
   - Add appropriate tags
   - Configure security settings

4. Structure the code with:
   - main.tf (main resources)
   - variables.tf (input variables)
   - outputs.tf (output values)
   - terraform.tf (provider requirements)

5. Make the code modular and reusable

Generate the complete Terraform configuration files:"""

        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            print(f"❌ Error generating code: {e}")
            return None
    
    def save_terraform_files(self, generated_code, output_dir="s3-terraform"):
        """Save generated Terraform code to files."""
        print(f"💾 Saving Terraform files to {output_dir}/...")
        
        # Create output directory
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        # Parse the generated code and save to appropriate files
        files_content = self.parse_terraform_files(generated_code)
        
        for filename, content in files_content.items():
            file_path = output_path / filename
            with open(file_path, 'w') as f:
                f.write(content)
            print(f"   ✅ Created {filename}")
        
        # Create a README
        readme_content = f"""# S3 Terraform Configuration

Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Usage

1. Initialize Terraform:
   ```bash
   terraform init
   ```

2. Plan the deployment:
   ```bash
   terraform plan
   ```

3. Apply the configuration:
   ```bash
   terraform apply
   ```

## Files

- `main.tf` - Main S3 bucket resources
- `variables.tf` - Input variables
- `outputs.tf` - Output values
- `terraform.tf` - Provider requirements

## Customization

Edit the variables in `variables.tf` or create a `terraform.tfvars` file to customize the configuration.
"""
        
        readme_path = output_path / "README.md"
        with open(readme_path, 'w') as f:
            f.write(readme_content)
        print(f"   ✅ Created README.md")
        
        return output_path
    
    def parse_terraform_files(self, generated_code):
        """Parse generated code into separate files."""
        files = {
            "main.tf": "",
            "variables.tf": "",
            "outputs.tf": "",
            "terraform.tf": ""
        }
        
        # Simple parsing - look for file markers or split by common patterns
        lines = generated_code.split('\n')
        current_file = "main.tf"
        
        for line in lines:
            # Check for file indicators
            if "# terraform.tf" in line.lower() or "terraform {" in line:
                current_file = "terraform.tf"
            elif "# variables.tf" in line.lower() or line.startswith("variable "):
                current_file = "variables.tf"
            elif "# outputs.tf" in line.lower() or line.startswith("output "):
                current_file = "outputs.tf"
            elif "# main.tf" in line.lower() or "resource " in line:
                current_file = "main.tf"
            
            files[current_file] += line + "\n"
        
        # Clean up empty files and ensure main.tf has content
        files = {k: v.strip() for k, v in files.items() if v.strip()}
        
        if not files.get("main.tf"):
            files["main.tf"] = generated_code
        
        return files

async def main():
    """Main function."""
    print("🚀 S3 Terraform Code Generator")
    print("=" * 50)
    
    try:
        generator = S3TerraformGenerator()
        
        # Get user requirements
        print("\n📝 Please describe your S3 bucket requirements:")
        print("Examples:")
        print("- 'Create a simple S3 bucket for static website hosting'")
        print("- 'Create multiple S3 buckets with encryption and versioning'")
        print("- 'Create S3 bucket with lifecycle policies and cross-region replication'")
        print()
        
        requirements = input("Your requirements: ").strip()
        
        if not requirements:
            requirements = "Create a basic S3 bucket with encryption and versioning enabled"
            print(f"Using default: {requirements}")
        
        # Generate the code
        print(f"\n🔄 Processing requirements: {requirements}")
        generated_code = await generator.generate_s3_terraform_code(requirements)
        
        if generated_code:
            print("\n✅ Terraform code generated successfully!")
            
            # Save to files
            output_dir = generator.save_terraform_files(generated_code)
            
            print(f"\n🎉 Complete! Your Terraform files are ready in: {output_dir}")
            print("\nNext steps:")
            print(f"1. cd {output_dir}")
            print("2. terraform init")
            print("3. terraform plan")
            print("4. terraform apply")
            
            # Show a preview
            print(f"\n📋 Preview of main.tf:")
            print("-" * 40)
            main_tf_path = output_dir / "main.tf"
            if main_tf_path.exists():
                with open(main_tf_path, 'r') as f:
                    preview = f.read()[:500]
                    print(preview)
                    if len(preview) >= 500:
                        print("... (truncated)")
        else:
            print("❌ Failed to generate Terraform code")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        if "GEMINI_API_KEY" in str(e):
            print("\n💡 To fix this:")
            print("1. Get your API key from: https://makersuite.google.com/app/apikey")
            print("2. Set it as environment variable: set GEMINI_API_KEY=your-key-here")

if __name__ == "__main__":
    asyncio.run(main())