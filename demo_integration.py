#!/usr/bin/env python3
"""
Demo of Terraform MCP server integration.
"""

import asyncio
import json
import subprocess
from pathlib import Path

async def demo_terraform_mcp():
    """Demonstrate the Terraform MCP server capabilities."""
    print("🚀 Terraform MCP Server Demo\n")
    
    server_path = Path("terraform-mcp-server.exe")
    
    # Initialize the server
    init_request = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {"name": "demo-client", "version": "1.0.0"}
        }
    }
    
    demos = [
        {
            "name": "Search for VPC modules",
            "request": {
                "jsonrpc": "2.0",
                "id": 2,
                "method": "tools/call",
                "params": {
                    "name": "searchModules",
                    "arguments": {
                        "moduleQuery": "vpc",
                        "currentOffset": 0
                    }
                }
            }
        },
        {
            "name": "Search for AWS provider documentation",
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
            }
        },
        {
            "name": "Search for security policies",
            "request": {
                "jsonrpc": "2.0",
                "id": 4,
                "method": "tools/call",
                "params": {
                    "name": "searchPolicies",
                    "arguments": {
                        "policyQuery": "security"
                    }
                }
            }
        }
    ]
    
    for demo in demos:
        print(f"🔍 {demo['name']}...")
        
        try:
            process = subprocess.Popen([
                str(server_path), "stdio"
            ], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            
            input_data = json.dumps(init_request) + "\n" + json.dumps(demo['request']) + "\n"
            stdout, stderr = process.communicate(input=input_data, timeout=30)
            
            if stdout:
                lines = stdout.strip().split('\n')
                for line in lines:
                    if line.strip():
                        try:
                            response = json.loads(line)
                            if response.get('id') == demo['request']['id']:
                                if 'result' in response:
                                    result = response['result']
                                    print("✅ Success!")
                                    
                                    # Pretty print the result based on the tool
                                    if demo['request']['params']['name'] == 'searchModules':
                                        if 'modules' in result:
                                            modules = result['modules'][:3]  # Show first 3
                                            print(f"   Found {len(result.get('modules', []))} modules (showing first 3):")
                                            for module in modules:
                                                print(f"   - {module.get('name', 'Unknown')}")
                                                print(f"     Description: {module.get('description', 'No description')[:80]}...")
                                                print(f"     Downloads: {module.get('downloads', 'Unknown')}")
                                    
                                    elif demo['request']['params']['name'] == 'resolveProviderDocID':
                                        if 'documents' in result:
                                            docs = result['documents'][:3]  # Show first 3
                                            print(f"   Found {len(result.get('documents', []))} documents (showing first 3):")
                                            for doc in docs:
                                                print(f"   - {doc.get('title', 'Unknown')}")
                                                print(f"     ID: {doc.get('providerDocID', 'Unknown')}")
                                                print(f"     Category: {doc.get('category', 'Unknown')}")
                                    
                                    elif demo['request']['params']['name'] == 'searchPolicies':
                                        if 'policies' in result:
                                            policies = result['policies'][:3]  # Show first 3
                                            print(f"   Found {len(result.get('policies', []))} policies (showing first 3):")
                                            for policy in policies:
                                                print(f"   - {policy.get('name', 'Unknown')}")
                                                print(f"     Description: {policy.get('description', 'No description')[:80]}...")
                                
                                elif 'error' in response:
                                    print(f"❌ Error: {response['error']['message']}")
                                
                                break
                        except json.JSONDecodeError:
                            continue
            
            print()  # Empty line between demos
            
        except Exception as e:
            print(f"❌ Error: {e}\n")
    
    print("🎉 Demo completed!")
    print("\nThe Terraform MCP server provides:")
    print("✅ Module search and documentation")
    print("✅ Provider documentation lookup")
    print("✅ Policy search and details")
    print("✅ Real-time Terraform registry integration")

if __name__ == "__main__":
    asyncio.run(demo_terraform_mcp())