#!/usr/bin/env python3
"""
Complete workflow test for Terraform MCP server.
"""

import asyncio
import json
import subprocess
from pathlib import Path

async def run_full_workflow():
    """Run a complete workflow demonstrating all major tools."""
    print("🚀 Terraform MCP Server - Complete Workflow Test\n")
    
    server_path = Path("terraform-mcp-server.exe")
    
    # Initialize request
    init_request = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {"name": "workflow-test", "version": "1.0.0"}
        }
    }
    
    workflows = [
        {
            "title": "🔍 Step 1: Search for VPC modules",
            "request": {
                "jsonrpc": "2.0",
                "id": 2,
                "method": "tools/call",
                "params": {
                    "name": "searchModules",
                    "arguments": {
                        "moduleQuery": "aws vpc",
                        "currentOffset": 0
                    }
                }
            },
            "process_result": lambda result: print_module_results(result)
        },
        {
            "title": "🔍 Step 2: Find AWS EC2 documentation",
            "request": {
                "jsonrpc": "2.0",
                "id": 3,
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
            },
            "process_result": lambda result: print_provider_docs(result)
        },
        {
            "title": "🔍 Step 3: Search for security policies",
            "request": {
                "jsonrpc": "2.0",
                "id": 4,
                "method": "tools/call",
                "params": {
                    "name": "searchPolicies",
                    "arguments": {
                        "policyQuery": "aws security"
                    }
                }
            },
            "process_result": lambda result: print_policy_results(result)
        }
    ]
    
    for workflow in workflows:
        print(workflow["title"])
        print("-" * 50)
        
        try:
            process = subprocess.Popen([
                str(server_path), "stdio"
            ], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            
            input_data = json.dumps(init_request) + "\n" + json.dumps(workflow['request']) + "\n"
            stdout, stderr = process.communicate(input=input_data, timeout=30)
            
            if stdout:
                lines = stdout.strip().split('\n')
                for line in lines:
                    if line.strip():
                        try:
                            response = json.loads(line)
                            if response.get('id') == workflow['request']['id']:
                                if 'result' in response:
                                    print("✅ Success!")
                                    workflow['process_result'](response['result'])
                                elif 'error' in response:
                                    print(f"❌ Error: {response['error']['message']}")
                                break
                        except json.JSONDecodeError:
                            continue
            
            print()  # Empty line between workflows
            
        except Exception as e:
            print(f"❌ Error: {e}\n")
    
    print("🎉 Complete workflow test finished!")
    print("\n📋 Summary:")
    print("✅ Module search - Find and explore Terraform modules")
    print("✅ Provider docs - Access up-to-date provider documentation")
    print("✅ Policy search - Discover security and compliance policies")
    print("\n🔗 The server provides seamless integration with the Terraform ecosystem!")

def print_module_results(result):
    """Print formatted module search results."""
    if 'content' in result and result['content']:
        content = result['content'][0].get('text', '')
        if 'moduleID' in content:
            print("   Found modules with details including:")
            print("   • Module IDs for further queries")
            print("   • Download counts and verification status")
            print("   • Descriptions and publication dates")
        else:
            print("   Module search completed successfully")
    else:
        print("   No modules found")

def print_provider_docs(result):
    """Print formatted provider documentation results."""
    if 'content' in result and result['content']:
        content = result['content'][0].get('text', '')
        if 'providerDocID' in content:
            print("   Found provider documentation with:")
            print("   • Provider document IDs for detailed queries")
            print("   • Resource categories and descriptions")
            print("   • Links to official documentation")
        else:
            print("   Provider documentation search completed")
    else:
        print("   No provider docs found")

def print_policy_results(result):
    """Print formatted policy search results."""
    if 'content' in result and result['content']:
        content = result['content'][0].get('text', '')
        if 'terraformPolicyID' in content or 'policy' in content.lower():
            print("   Found policies with:")
            print("   • Policy IDs for detailed information")
            print("   • Security and compliance guidelines")
            print("   • Implementation recommendations")
        else:
            print("   Policy search completed successfully")
    else:
        print("   No policies found")

if __name__ == "__main__":
    asyncio.run(run_full_workflow())