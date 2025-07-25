#!/usr/bin/env python3
"""
Fetch S3 Terraform code from GitHub using Terraform MCP server.
"""

import asyncio
import json
import subprocess
from pathlib import Path

class GitHubCodeFetcher:
    """Fetch code from GitHub repository using MCP server."""
    
    def __init__(self):
        self.server_path = Path("terraform-mcp-server.exe")
    
    async def search_github_s3_examples(self):
        """Search for S3 examples in the terraform-mcp-server repository."""
        print("🔍 Searching for S3 examples in terraform-mcp-server repository...")
        
        # The MCP server might have tools to access GitHub or code repositories
        # Let's first check what tools are available
        await self.list_available_tools()
        
        # Try to use any GitHub-related tools if available
        return await self.fetch_s3_examples()
    
    async def list_available_tools(self):
        """List all available tools from MCP server."""
        print("📋 Checking available MCP tools...")
        
        init_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "github-fetcher", "version": "1.0.0"}
            }
        }
        
        tools_request = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/list",
            "params": {}
        }
        
        try:
            process = subprocess.Popen([
                str(self.server_path), "stdio"
            ], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            
            input_data = json.dumps(init_request) + "\n" + json.dumps(tools_request) + "\n"
            stdout, stderr = process.communicate(input=input_data, timeout=30)
            
            if stdout:
                lines = stdout.strip().split('\n')
                for line in lines:
                    if line.strip():
                        try:
                            response = json.loads(line)
                            if response.get('id') == 2 and 'result' in response:
                                tools = response['result'].get('tools', [])
                                print(f"✅ Found {len(tools)} available tools:")
                                for tool in tools:
                                    print(f"   • {tool.get('name', 'Unknown')}: {tool.get('description', 'No description')[:60]}...")
                                return tools
                        except json.JSONDecodeError:
                            continue
            
            return []
            
        except Exception as e:
            print(f"❌ Error listing tools: {e}")
            return []
    
    async def fetch_s3_examples(self):
        """Try to fetch S3 examples using available tools."""
        print("\n🔍 Looking for S3 bucket examples...")
        
        # Since the MCP server focuses on Terraform registry, let's search for S3 modules
        # that might contain example code
        
        init_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "s3-fetcher", "version": "1.0.0"}
            }
        }
        
        # Search for S3 modules
        s3_search_request = {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {
                "name": "searchModules",
                "arguments": {
                    "moduleQuery": "s3 bucket terraform hashicorp",
                    "currentOffset": 0
                }
            }
        }
        
        try:
            process = subprocess.Popen([
                str(self.server_path), "stdio"
            ], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            
            input_data = json.dumps(init_request) + "\n" + json.dumps(s3_search_request) + "\n"
            stdout, stderr = process.communicate(input=input_data, timeout=30)
            
            if stdout:
                lines = stdout.strip().split('\n')
                for line in lines:
                    if line.strip():
                        try:
                            response = json.loads(line)
                            if response.get('id') == 3 and 'result' in response:
                                content = response['result']['content'][0]['text']
                                print("✅ Found S3 modules from Terraform registry:")
                                
                                # Extract module IDs for detailed information
                                module_ids = self.extract_module_ids(content)
                                return await self.get_module_details(module_ids[:3])  # Get first 3
                                
                        except json.JSONDecodeError:
                            continue
            
            return None
            
        except Exception as e:
            print(f"❌ Error searching modules: {e}")
            return None
    
    def extract_module_ids(self, content):
        """Extract module IDs from search results."""
        module_ids = []
        lines = content.split('\n')
        
        for line in lines:
            if 'moduleID:' in line:
                # Extract module ID
                parts = line.split('moduleID:')
                if len(parts) > 1:
                    module_id = parts[1].strip()
                    module_ids.append(module_id)
        
        return module_ids
    
    async def get_module_details(self, module_ids):
        """Get detailed information for specific modules."""
        print(f"\n📖 Getting details for {len(module_ids)} S3 modules...")
        
        module_details = []
        
        for i, module_id in enumerate(module_ids):
            print(f"   Fetching details for module {i+1}: {module_id}")
            
            init_request = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize",
                "params": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {},
                    "clientInfo": {"name": "module-details", "version": "1.0.0"}
                }
            }
            
            details_request = {
                "jsonrpc": "2.0",
                "id": 4,
                "method": "tools/call",
                "params": {
                    "name": "moduleDetails",
                    "arguments": {
                        "moduleID": module_id
                    }
                }
            }
            
            try:
                process = subprocess.Popen([
                    str(self.server_path), "stdio"
                ], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                
                input_data = json.dumps(init_request) + "\n" + json.dumps(details_request) + "\n"
                stdout, stderr = process.communicate(input=input_data, timeout=30)
                
                if stdout:
                    lines = stdout.strip().split('\n')
                    for line in lines:
                        if line.strip():
                            try:
                                response = json.loads(line)
                                if response.get('id') == 4 and 'result' in response:
                                    content = response['result']['content'][0]['text']
                                    module_details.append({
                                        'module_id': module_id,
                                        'content': content
                                    })
                                    print(f"   ✅ Retrieved details for {module_id}")
                                    break
                            except json.JSONDecodeError:
                                continue
                
            except Exception as e:
                print(f"   ❌ Error getting details for {module_id}: {e}")
        
        return module_details
    
    def save_fetched_code(self, module_details, output_dir="fetched-s3-code"):
        """Save the fetched code to files."""
        print(f"\n💾 Saving fetched S3 code to {output_dir}/...")
        
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        # Create a summary file
        summary_content = "# S3 Terraform Code from Terraform Registry\n\n"
        summary_content += f"Fetched on: {asyncio.get_event_loop().time()}\n"
        summary_content += f"Source: Terraform MCP Server\n\n"
        
        for i, module in enumerate(module_details, 1):
            module_id = module['module_id']
            content = module['content']
            
            # Save individual module details
            module_file = output_path / f"module_{i}_{module_id.replace('/', '_')}.md"
            with open(module_file, 'w', encoding='utf-8') as f:
                f.write(f"# Module: {module_id}\n\n")
                f.write(content)
            
            print(f"   ✅ Saved {module_file.name}")
            
            # Add to summary
            summary_content += f"## Module {i}: {module_id}\n\n"
            summary_content += f"Details saved in: {module_file.name}\n\n"
            
            # Extract any code examples from the content
            if "```" in content:
                summary_content += "Contains code examples ✅\n\n"
            
            summary_content += "---\n\n"
        
        # Save summary
        summary_file = output_path / "README.md"
        with open(summary_file, 'w', encoding='utf-8') as f:
            f.write(summary_content)
        print(f"   ✅ Created README.md")
        
        return output_path

async def main():
    """Main function."""
    print("🚀 GitHub S3 Code Fetcher using Terraform MCP Server")
    print("=" * 60)
    print("Repository: https://github.com/hashicorp/terraform-mcp-server")
    print()
    
    try:
        fetcher = GitHubCodeFetcher()
        
        # Search for S3 examples
        module_details = await fetcher.search_github_s3_examples()
        
        if module_details:
            # Save the fetched code
            output_dir = fetcher.save_fetched_code(module_details)
            
            print(f"\n🎉 Successfully fetched S3 Terraform code!")
            print(f"📁 Files saved to: {output_dir}")
            print("\n📋 What was fetched:")
            print("   ✅ S3 module documentation from Terraform registry")
            print("   ✅ Usage examples and code snippets")
            print("   ✅ Module configurations and variables")
            
            print(f"\n💡 Next steps:")
            print(f"   1. Check the files in {output_dir}/")
            print("   2. Look for code examples in the module documentation")
            print("   3. Use the examples as templates for your S3 buckets")
            
        else:
            print("❌ No S3 modules found")
            print("\n💡 Alternative approach:")
            print("   The MCP server provides access to Terraform registry modules")
            print("   You can use the module details to create your own S3 configurations")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())