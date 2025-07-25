#!/usr/bin/env python3
"""
Generate S3 Terraform code using fetched module information from MCP server.
"""

import asyncio
import json
import os
from pathlib import Path
from datetime import datetime
import google.generativeai as genai

class S3CodeGenerator:
    """Generate S3 code using MCP-fetched module information."""
    
    def __init__(self):
        # Configure Gemini with your API key
        api_key = "AIzaSyC-66cCtIosU8pTPd6eLnlQMn0dg7ofW6Y"
        genai.configure(api_key=api_key)
        
        self.model = genai.GenerativeModel(
            "gemini-1.5-flash",  # Using flash model to avoid rate limits
            generation_config={
                "temperature": 0.1,
                "max_output_tokens": 2048,
            }
        )
        
        self.fetched_code_dir = Path("fetched-s3-code")
    
    def read_fetched_modules(self):
        """Read the fetched module information."""
        print("📖 Reading fetched S3 module information...")
        
        modules_info = []
        
        if not self.fetched_code_dir.exists():
            print("❌ No fetched code directory found. Run github_code_fetcher.py first.")
            return []
        
        for file_path in self.fetched_code_dir.glob("module_*.md"):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    modules_info.append({
                        'filename': file_path.name,
                        'content': content
                    })
                print(f"   ✅ Read {file_path.name}")
            except Exception as e:
                print(f"   ❌ Error reading {file_path.name}: {e}")
        
        return modules_info
    
    async def generate_s3_code(self, requirements, modules_info):
        """Generate S3 Terraform code using Gemini and module information."""
        print("🤖 Generating S3 Terraform code with Gemini...")
        
        # Create prompt with module information
        modules_context = "\n\n".join([
            f"## {module['filename']}\n{module['content'][:1000]}..."  # Truncate to avoid token limits
            for module in modules_info
        ])
        
        prompt = f"""You are a Terraform expert. Generate complete, production-ready Terraform code for AWS S3 buckets.

USER REQUIREMENTS:
{requirements}

AVAILABLE S3 MODULES FROM TERRAFORM REGISTRY:
{modules_context}

INSTRUCTIONS:
1. Create a complete Terraform configuration with these files:
   - main.tf (main S3 resources)
   - variables.tf (input variables)
   - outputs.tf (output values)
   - terraform.tf (provider requirements)

2. Use the module information provided to create the best S3 configuration

3. Include:
   - Proper AWS provider configuration
   - S3 bucket with security best practices
   - Appropriate variables for customization
   - Useful outputs
   - Comments explaining the configuration

4. Follow Terraform best practices:
   - Use latest AWS provider syntax
   - Include proper resource naming
   - Add appropriate tags
   - Configure security settings (encryption, public access block, etc.)

5. Make the code modular and reusable

Generate the complete Terraform files separated by "=== FILENAME ===" markers:

=== terraform.tf ===
[terraform.tf content here]

=== variables.tf ===
[variables.tf content here]

=== main.tf ===
[main.tf content here]

=== outputs.tf ===
[outputs.tf content here]"""

        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            print(f"❌ Error generating code: {e}")
            return None
    
    def parse_and_save_code(self, generated_code, output_dir="s3-terraform-generated"):
        """Parse generated code and save to files."""
        print(f"💾 Saving generated code to {output_dir}/...")
        
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        # Parse the generated code by file markers
        files = {}
        current_file = None
        current_content = []
        
        lines = generated_code.split('\n')
        
        for line in lines:
            if line.startswith('=== ') and line.endswith(' ==='):
                # Save previous file
                if current_file:
                    files[current_file] = '\n'.join(current_content)
                
                # Start new file
                current_file = line.replace('=== ', '').replace(' ===', '')
                current_content = []
            else:
                if current_file:
                    current_content.append(line)
        
        # Save last file
        if current_file:
            files[current_file] = '\n'.join(current_content)
        
        # Save files
        for filename, content in files.items():
            if content.strip():  # Only save non-empty files
                file_path = output_path / filename
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content.strip())
                print(f"   ✅ Created {filename}")
        
        # Create README
        readme_content = f"""# S3 Terraform Configuration

Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Generated using: Terraform MCP Server + Gemini LLM
Source modules: Terraform Registry via MCP Server

## Features

This configuration was generated using real Terraform modules from the registry:
- ✅ Production-ready S3 bucket configuration
- ✅ Security best practices included
- ✅ Customizable through variables
- ✅ Based on verified Terraform modules

## Usage

1. **Initialize Terraform:**
   ```bash
   terraform init
   ```

2. **Customize variables:**
   Edit `variables.tf` or create `terraform.tfvars`:
   ```hcl
   bucket_name = "my-app-bucket"
   environment = "production"
   ```

3. **Plan and apply:**
   ```bash
   terraform plan
   terraform apply
   ```

## Files

- `terraform.tf` - Provider requirements
- `variables.tf` - Input variables
- `main.tf` - S3 bucket resources
- `outputs.tf` - Output values

## Generated with MCP Server

This code was generated using:
1. Terraform MCP Server to fetch real module information
2. Gemini LLM to generate production-ready code
3. Best practices from Terraform registry modules

Repository: https://github.com/hashicorp/terraform-mcp-server
"""
        
        readme_path = output_path / "README.md"
        with open(readme_path, 'w', encoding='utf-8') as f:
            f.write(readme_content)
        print(f"   ✅ Created README.md")
        
        return output_path

async def main():
    """Main function."""
    print("🚀 S3 Terraform Code Generator using MCP-fetched Modules")
    print("=" * 60)
    
    try:
        generator = S3CodeGenerator()
        
        # Read fetched module information
        modules_info = generator.read_fetched_modules()
        
        if not modules_info:
            print("❌ No module information found.")
            print("💡 Run 'py github_code_fetcher.py' first to fetch module information.")
            return
        
        print(f"✅ Found {len(modules_info)} S3 modules from Terraform registry")
        
        # Get user requirements
        print("\n📝 What kind of S3 bucket do you want to create?")
        print("Examples:")
        print("- 'Simple S3 bucket with encryption'")
        print("- 'S3 bucket for static website hosting'")
        print("- 'S3 bucket with versioning and lifecycle policies'")
        print("- 'S3 bucket for application logs with retention'")
        print()
        
        requirements = input("Your requirements: ").strip()
        
        if not requirements:
            requirements = "Simple S3 bucket with encryption and versioning"
            print(f"Using default: {requirements}")
        
        # Generate code
        print(f"\n🔄 Generating Terraform code for: {requirements}")
        generated_code = await generator.generate_s3_code(requirements, modules_info)
        
        if generated_code:
            # Save the code
            output_dir = generator.parse_and_save_code(generated_code)
            
            print(f"\n🎉 Success! S3 Terraform code generated!")
            print(f"📁 Files saved to: {output_dir}")
            
            print(f"\n📋 What was generated:")
            print("   ✅ Complete Terraform configuration")
            print("   ✅ Based on real Terraform registry modules")
            print("   ✅ Security best practices included")
            print("   ✅ Customizable variables")
            
            print(f"\n🚀 Next steps:")
            print(f"   1. cd {output_dir}")
            print("   2. terraform init")
            print("   3. terraform plan")
            print("   4. terraform apply")
            
            # Show preview
            main_tf = output_dir / "main.tf"
            if main_tf.exists():
                print(f"\n📋 Preview of main.tf:")
                print("-" * 40)
                with open(main_tf, 'r') as f:
                    lines = f.readlines()[:10]
                    print(''.join(lines))
                    print("... (see full file for complete configuration)")
        else:
            print("❌ Failed to generate code")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())