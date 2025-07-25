#!/usr/bin/env python3
"""
Generate EC2 Terraform code using MCP server and Gemini LLM.
"""

import asyncio
import json
import subprocess
from pathlib import Path
import google.generativeai as genai

class EC2CodeGenerator:
    """Generate EC2 Terraform code using MCP server and Gemini."""
    
    def __init__(self):
        self.server_path = Path("terraform-mcp-server.exe")
        
        # Configure Gemini
        api_key = "AIzaSyC-66cCtIosU8pTPd6eLnlQMn0dg7ofW6Y"
        genai.configure(api_key=api_key)
        
        self.model = genai.GenerativeModel(
            "gemini-1.5-flash",
            generation_config={
                "temperature": 0.1,
                "max_output_tokens": 2048,
            }
        )
    
    async def fetch_ec2_provider_docs(self):
        """Fetch EC2 provider documentation."""
        print("🔍 Fetching EC2 provider documentation...")
        
        init_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "ec2-generator", "version": "1.0.0"}
            }
        }
        
        ec2_docs_request = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/call",
            "params": {
                "name": "resolveProviderDocID",
                "arguments": {
                    "providerName": "aws",
                    "providerNamespace": "hashicorp",
                    "serviceSlug": "ec2",
                    "providerDataType": "resources"
                }
            }
        }
        
        try:
            process = subprocess.Popen([
                str(self.server_path), "stdio"
            ], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            
            input_data = json.dumps(init_request) + "\n" + json.dumps(ec2_docs_request) + "\n"
            stdout, stderr = process.communicate(input=input_data, timeout=30)
            
            if stdout:
                lines = stdout.strip().split('\n')
                for line in lines:
                    if line.strip():
                        try:
                            response = json.loads(line)
                            if response.get('id') == 2 and 'result' in response:
                                print("✅ Retrieved EC2 provider documentation")
                                return response['result']['content'][0]['text']
                        except json.JSONDecodeError:
                            continue
            
            return "EC2 provider documentation available"
            
        except Exception as e:
            print(f"❌ Error fetching EC2 docs: {e}")
            return "Standard AWS EC2 resources available"
    
    async def fetch_ec2_modules(self):
        """Fetch EC2 modules from registry."""
        print("🔍 Searching for EC2 modules...")
        
        init_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "ec2-modules", "version": "1.0.0"}
            }
        }
        
        ec2_modules_request = {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {
                "name": "searchModules",
                "arguments": {
                    "moduleQuery": "aws ec2 instance",
                    "currentOffset": 0
                }
            }
        }
        
        try:
            process = subprocess.Popen([
                str(self.server_path), "stdio"
            ], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            
            input_data = json.dumps(init_request) + "\n" + json.dumps(ec2_modules_request) + "\n"
            stdout, stderr = process.communicate(input=input_data, timeout=30)
            
            if stdout:
                lines = stdout.strip().split('\n')
                for line in lines:
                    if line.strip():
                        try:
                            response = json.loads(line)
                            if response.get('id') == 3 and 'result' in response:
                                print("✅ Retrieved EC2 module information")
                                return response['result']['content'][0]['text']
                        except json.JSONDecodeError:
                            continue
            
            return "EC2 modules available"
            
        except Exception as e:
            print(f"❌ Error searching EC2 modules: {e}")
            return "Standard EC2 modules available"
    
    async def generate_ec2_code(self, requirements):
        """Generate EC2 Terraform code."""
        print("🤖 Generating EC2 Terraform code...")
        
        # Get provider docs and modules
        provider_docs = await self.fetch_ec2_provider_docs()
        module_info = await self.fetch_ec2_modules()
        
        prompt = f"""You are a Terraform expert. Generate complete, production-ready Terraform code for AWS EC2 instances.

USER REQUIREMENTS:
{requirements}

EC2 PROVIDER DOCUMENTATION:
{provider_docs[:800]}...

EC2 MODULES AVAILABLE:
{module_info[:800]}...

INSTRUCTIONS:
Generate complete Terraform code with these sections separated by "=== SECTION ===" markers:

1. Provider configuration (terraform block and aws provider)
2. Variables for customization
3. Main EC2 resources with security best practices
4. Outputs for important values

Include:
- Latest AWS provider syntax
- Security groups with proper rules
- Key pair configuration
- Instance configuration with appropriate instance type
- Tags for resource management
- User data if needed
- Proper networking (VPC, subnet)

Generate the code in this format:

=== PROVIDER ===
[Provider configuration]

=== VARIABLES ===
[Variable definitions]

=== MAIN ===
[Main EC2 resources]

=== OUTPUTS ===
[Output values]"""

        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            print(f"❌ Error generating code: {e}")
            return None

async def main():
    """Main function."""
    print("🚀 EC2 Terraform Code Generator")
    print("=" * 40)
    
    try:
        generator = EC2CodeGenerator()
        
        # Get user requirements
        print("\n📝 What kind of EC2 instance do you want to create?")
        print("Examples:")
        print("- 'Simple web server with security group'")
        print("- 'EC2 instance for development with SSH access'")
        print("- 'Production EC2 with load balancer'")
        print()
        
        requirements = input("Your requirements: ").strip()
        
        if not requirements:
            requirements = "Simple web server with security group and SSH access"
            print(f"Using default: {requirements}")
        
        # Generate code
        print(f"\n🔄 Generating EC2 code for: {requirements}")
        generated_code = await generator.generate_ec2_code(requirements)
        
        if generated_code:
            print("\n" + "="*60)
            print("🎯 COMPLETE EC2 TERRAFORM CODE")
            print("="*60)
            print(generated_code)
            print("="*60)
        else:
            print("❌ Failed to generate code")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())