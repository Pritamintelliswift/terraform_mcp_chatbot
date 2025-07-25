#!/usr/bin/env python3
"""
Test utility for Terraform MCP server connection.
"""

import asyncio
import json
import logging
import sys
from pathlib import Path

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from config import get_config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MCPConnectionTester:
    """Test MCP server connection and available tools."""
    
    def __init__(self):
        self.config = get_config()
        self.session = None
    
    async def test_connection(self) -> bool:
        """Test basic connection to MCP server."""
        try:
            print("🔄 Testing MCP server connection...")
            
            # Start the MCP server process
            server_params = StdioServerParameters(
                command=self.config.mcp_server.server_path,
                args=self.config.mcp_server.server_args,
                env=None
            )
            
            # Create stdio client
            stdio_transport = await stdio_client(server_params)
            self.session = ClientSession(stdio_transport[0], stdio_transport[1])
            
            # Initialize the session
            await self.session.initialize()
            print("✅ Successfully connected to MCP server")
            return True
            
        except Exception as e:
            print(f"❌ Failed to connect to MCP server: {e}")
            return False
    
    async def list_available_tools(self) -> bool:
        """List all available tools from the MCP server."""
        if not self.session:
            print("❌ No active session")
            return False
        
        try:
            print("\n🔍 Listing available tools...")
            tools_result = await self.session.list_tools()
            
            if not tools_result.tools:
                print("⚠️  No tools available")
                return False
            
            print(f"✅ Found {len(tools_result.tools)} tools:")
            for i, tool in enumerate(tools_result.tools, 1):
                print(f"\n{i}. {tool.name}")
                print(f"   Description: {tool.description}")
                
                if hasattr(tool, 'inputSchema') and tool.inputSchema:
                    schema = tool.inputSchema
                    if 'properties' in schema:
                        params = list(schema['properties'].keys())
                        print(f"   Parameters: {', '.join(params)}")
            
            return True
            
        except Exception as e:
            print(f"❌ Failed to list tools: {e}")
            return False
    
    async def test_tool_call(self, tool_name: str, arguments: dict) -> bool:
        """Test calling a specific tool."""
        if not self.session:
            print("❌ No active session")
            return False
        
        try:
            print(f"\n🧪 Testing tool: {tool_name}")
            print(f"   Arguments: {json.dumps(arguments, indent=2)}")
            
            result = await self.session.call_tool(tool_name, arguments)
            
            print("✅ Tool call successful")
            print(f"   Result: {result.content}")
            
            if hasattr(result, 'isError') and result.isError:
                print("⚠️  Tool returned an error")
            
            return True
            
        except Exception as e:
            print(f"❌ Tool call failed: {e}")
            return False
    
    async def run_comprehensive_test(self):
        """Run a comprehensive test of the MCP server."""
        print("🚀 Starting comprehensive MCP server test\n")
        
        # Test connection
        if not await self.test_connection():
            return False
        
        # List tools
        if not await self.list_available_tools():
            return False
        
        # Test some common tool calls
        test_cases = [
            {
                "tool_name": "resolveProviderDocID",
                "arguments": {
                    "providerName": "aws",
                    "providerNamespace": "hashicorp",
                    "serviceSlug": "ec2",
                    "providerDataType": "resources"
                }
            },
            {
                "tool_name": "searchModules",
                "arguments": {
                    "query": "vpc",
                    "limit": 5
                }
            }
        ]
        
        for test_case in test_cases:
            await self.test_tool_call(
                test_case["tool_name"],
                test_case["arguments"]
            )
        
        print("\n🎉 Comprehensive test completed!")
        return True
    
    async def cleanup(self):
        """Clean up resources."""
        if self.session:
            await self.session.close()


async def main():
    """Main test function."""
    tester = MCPConnectionTester()
    
    try:
        success = await tester.run_comprehensive_test()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n⏹️  Test interrupted by user")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)
    finally:
        await tester.cleanup()


if __name__ == "__main__":
    asyncio.run(main())