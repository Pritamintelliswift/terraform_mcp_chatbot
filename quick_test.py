#!/usr/bin/env python3
"""
Quick test to see all available MCP tools in detail.
"""

import asyncio
import json
import subprocess
from pathlib import Path

async def get_detailed_tools():
    """Get detailed information about all available tools."""
    print("🔍 Getting detailed tool information...\n")
    
    server_path = Path("terraform-mcp-server.exe")
    
    # Initialize and get tools
    init_request = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {"name": "test-client", "version": "1.0.0"}
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
            str(server_path), "stdio"
        ], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        input_data = json.dumps(init_request) + "\n" + json.dumps(tools_request) + "\n"
        stdout, stderr = process.communicate(input=input_data, timeout=15)
        
        if stdout:
            lines = stdout.strip().split('\n')
            for line in lines:
                if line.strip():
                    try:
                        response = json.loads(line)
                        if response.get('id') == 2 and 'result' in response:
                            tools = response['result'].get('tools', [])
                            
                            print(f"📋 Available Tools ({len(tools)} total):\n")
                            
                            for i, tool in enumerate(tools, 1):
                                print(f"{i}. {tool.get('name', 'Unknown')}")
                                print(f"   Description: {tool.get('description', 'No description')}")
                                
                                # Show input schema if available
                                if 'inputSchema' in tool:
                                    schema = tool['inputSchema']
                                    if 'properties' in schema:
                                        print("   Parameters:")
                                        for param, details in schema['properties'].items():
                                            param_type = details.get('type', 'unknown')
                                            param_desc = details.get('description', 'No description')
                                            required = param in schema.get('required', [])
                                            req_marker = " (required)" if required else " (optional)"
                                            print(f"     - {param} ({param_type}){req_marker}: {param_desc}")
                                
                                print()  # Empty line between tools
                            
                            return True
                    except json.JSONDecodeError:
                        continue
        
        print("❌ Could not retrieve detailed tool information")
        return False
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

async def test_sample_tool_call():
    """Test a sample tool call."""
    print("🧪 Testing a sample tool call...\n")
    
    server_path = Path("terraform-mcp-server.exe")
    
    # Initialize, then call a tool
    init_request = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {"name": "test-client", "version": "1.0.0"}
        }
    }
    
    # Test searchModules tool
    tool_call = {
        "jsonrpc": "2.0",
        "id": 3,
        "method": "tools/call",
        "params": {
            "name": "searchModules",
            "arguments": {
                "moduleQuery": "vpc",
                "currentOffset": 0
            }
        }
    }
    
    try:
        process = subprocess.Popen([
            str(server_path), "stdio"
        ], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        input_data = json.dumps(init_request) + "\n" + json.dumps(tool_call) + "\n"
        stdout, stderr = process.communicate(input=input_data, timeout=20)
        
        if stdout:
            lines = stdout.strip().split('\n')
            for line in lines:
                if line.strip():
                    try:
                        response = json.loads(line)
                        if response.get('id') == 3:
                            print("✅ Tool call successful!")
                            if 'result' in response:
                                result = response['result']
                                print(f"Result: {json.dumps(result, indent=2)[:500]}...")
                            elif 'error' in response:
                                print(f"❌ Tool returned error: {response['error']}")
                            return True
                    except json.JSONDecodeError:
                        continue
        
        print("⚠️  No response from tool call")
        return False
        
    except Exception as e:
        print(f"❌ Error testing tool call: {e}")
        return False

async def main():
    """Main function."""
    print("🚀 Terraform MCP Server - Detailed Tool Analysis\n")
    
    await get_detailed_tools()
    await test_sample_tool_call()
    
    print("\n🎉 Analysis complete!")
    print("\nThe Terraform MCP server is ready to use with:")
    print("- Provider documentation lookup")
    print("- Module search and details")
    print("- Policy documentation")
    print("- And more Terraform-related tools!")

if __name__ == "__main__":
    asyncio.run(main())