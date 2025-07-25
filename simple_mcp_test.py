#!/usr/bin/env python3
"""
Simple test for Terraform MCP server connection.
"""

import asyncio
import json
import subprocess
import sys
from pathlib import Path

async def test_mcp_server():
    """Test the MCP server by running it directly."""
    print("🔄 Testing Terraform MCP server...")
    
    # Check if the server binary exists
    server_path = Path("terraform-mcp-server.exe")
    if not server_path.exists():
        print("❌ terraform-mcp-server.exe not found")
        print("   Run: go build -o terraform-mcp-server.exe ./cmd/terraform-mcp-server")
        return False
    
    try:
        # Test server help command
        result = subprocess.run([
            str(server_path), "--help"
        ], capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            print("✅ Server binary is working")
            print(f"   Output preview: {result.stdout[:100]}...")
        else:
            print(f"❌ Server help failed: {result.stderr}")
            return False
        
        # Test stdio mode (this will start the server in stdio mode)
        print("\n🔄 Testing stdio mode...")
        
        # Create a simple test input for the MCP server
        test_input = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "roots": {
                        "listChanged": True
                    },
                    "sampling": {}
                },
                "clientInfo": {
                    "name": "test-client",
                    "version": "1.0.0"
                }
            }
        }
        
        # Start server in stdio mode
        process = subprocess.Popen([
            str(server_path), "stdio"
        ], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        # Send initialize request
        input_data = json.dumps(test_input) + "\n"
        stdout, stderr = process.communicate(input=input_data, timeout=10)
        
        if process.returncode == 0 or stdout:
            print("✅ Server responded to stdio communication")
            if stdout:
                try:
                    response = json.loads(stdout.strip())
                    print(f"   Response: {json.dumps(response, indent=2)[:200]}...")
                except json.JSONDecodeError:
                    print(f"   Raw response: {stdout[:200]}...")
        else:
            print(f"❌ Server stdio test failed")
            if stderr:
                print(f"   Error: {stderr}")
            return False
        
        return True
        
    except subprocess.TimeoutExpired:
        print("❌ Server test timed out")
        return False
    except Exception as e:
        print(f"❌ Error testing server: {e}")
        return False

async def test_server_tools():
    """Test listing available tools."""
    print("\n🔍 Testing available tools...")
    
    server_path = Path("terraform-mcp-server.exe")
    
    # Test tools list request
    test_input = {
        "jsonrpc": "2.0",
        "id": 2,
        "method": "tools/list",
        "params": {}
    }
    
    try:
        process = subprocess.Popen([
            str(server_path), "stdio"
        ], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        # Send initialize first, then tools/list
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
        
        input_data = json.dumps(init_request) + "\n" + json.dumps(test_input) + "\n"
        stdout, stderr = process.communicate(input=input_data, timeout=15)
        
        if stdout:
            lines = stdout.strip().split('\n')
            for line in lines:
                if line.strip():
                    try:
                        response = json.loads(line)
                        if response.get('id') == 2:  # tools/list response
                            print("✅ Tools list retrieved")
                            if 'result' in response and 'tools' in response['result']:
                                tools = response['result']['tools']
                                print(f"   Found {len(tools)} tools:")
                                for tool in tools[:5]:  # Show first 5 tools
                                    print(f"   - {tool.get('name', 'Unknown')}: {tool.get('description', 'No description')[:50]}...")
                            return True
                    except json.JSONDecodeError:
                        continue
        
        print("⚠️  Could not retrieve tools list")
        return False
        
    except Exception as e:
        print(f"❌ Error testing tools: {e}")
        return False

async def main():
    """Main test function."""
    print("🚀 Simple Terraform MCP Server Test\n")
    
    # Test basic server functionality
    if not await test_mcp_server():
        print("\n❌ Basic server test failed")
        sys.exit(1)
    
    # Test tools listing
    await test_server_tools()
    
    print("\n🎉 MCP server test completed!")
    print("\nNext steps:")
    print("1. The server is working and can communicate via stdio")
    print("2. You can now use it with MCP clients")
    print("3. Try running: py terraform_gemini_integration.py")

if __name__ == "__main__":
    asyncio.run(main())