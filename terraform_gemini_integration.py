#!/usr/bin/env python3
"""
Terraform MCP Server + Gemini LLM Integration

This script integrates the Terraform MCP server with Google's Gemini LLM,
allowing Gemini to use Terraform tools for infrastructure management tasks.

Features:
- Automatic MCP server discovery and connection
- Enhanced error handling and retry logic
- Structured conversation history
- Tool usage analytics
- Configuration management
"""

import asyncio
import json
import logging
import os
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime

import google.generativeai as genai
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# Import our configuration
from config import IntegrationConfig, get_config

# Configure logging with better formatting
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('terraform_gemini.log')
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class ConversationContext:
    """Tracks conversation context and tool usage."""
    user_message: str
    timestamp: datetime
    tools_used: List[str]
    response: str
    success: bool
    
@dataclass
class MCPServerConfig:
    """Configuration for MCP server connection."""
    server_path: str = "terraform-mcp-server"
    server_args: List[str] = None
    timeout: int = 30
    retry_attempts: int = 3
    
    def __post_init__(self):
        if self.server_args is None:
            self.server_args = ["stdio"]


class TerraformMCPClient:
    """Enhanced client for communicating with the Terraform MCP server."""
    
    def __init__(self, config: MCPServerConfig = None):
        self.config = config or MCPServerConfig()
        self.session: Optional[ClientSession] = None
        self.available_tools: List[Dict[str, Any]] = []
        self.connection_attempts = 0
        self.last_connection_time = None
        
    async def connect(self):
        """Connect to the Terraform MCP server with retry logic."""
        for attempt in range(self.config.retry_attempts):
            try:
                self.connection_attempts += 1
                logger.info(f"Attempting to connect to MCP server (attempt {attempt + 1}/{self.config.retry_attempts})")
                
                # Start the MCP server process
                server_params = StdioServerParameters(
                    command=self.config.server_path,
                    args=self.config.server_args,
                    env=None
                )
                
                # Create stdio client
                stdio_transport = await stdio_client(server_params)
                self.session = ClientSession(stdio_transport[0], stdio_transport[1])
                
                # Initialize the session
                await self.session.initialize()
                
                # Get available tools
                tools_result = await self.session.list_tools()
                self.available_tools = tools_result.tools
                self.last_connection_time = time.time()
                
                logger.info(f"Connected to Terraform MCP server with {len(self.available_tools)} tools")
                for tool in self.available_tools:
                    logger.info(f"  - {tool.name}: {tool.description}")
                return
                
            except Exception as e:
                logger.error(f"Connection attempt {attempt + 1} failed: {e}")
                if attempt < self.config.retry_attempts - 1:
                    await asyncio.sleep(2 ** attempt)  # Exponential backoff
                else:
                    logger.error(f"Failed to connect to Terraform MCP server after {self.config.retry_attempts} attempts")
                    raise
    
    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Call a tool on the MCP server."""
        if not self.session:
            raise RuntimeError("Not connected to MCP server")
            
        try:
            result = await self.session.call_tool(tool_name, arguments)
            return {
                "success": True,
                "content": result.content,
                "is_error": result.isError if hasattr(result, 'isError') else False
            }
        except Exception as e:
            logger.error(f"Error calling tool {tool_name}: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def disconnect(self):
        """Disconnect from the MCP server."""
        if self.session:
            await self.session.close()
            self.session = None


class GeminiTerraformAgent:
    """Enhanced Gemini LLM agent with Terraform MCP capabilities."""
    
    def __init__(self, config: IntegrationConfig):
        self.config = config
        self.mcp_client = TerraformMCPClient(config.mcp_server)
        self.conversation_history: List[ConversationContext] = []
        self.tool_usage_stats = {}
        
        # Configure Gemini
        genai.configure(api_key=config.gemini.api_key)
        
        # Create model with enhanced configuration
        generation_config = {
            "temperature": config.gemini.temperature,
            "max_output_tokens": config.gemini.max_tokens,
        }
        
        self.model = genai.GenerativeModel(
            config.gemini.model_name,
            generation_config=generation_config
        )
        
    async def initialize(self):
        """Initialize the agent by connecting to MCP server."""
        await self.mcp_client.connect()
        
    async def shutdown(self):
        """Shutdown the agent."""
        await self.mcp_client.disconnect()
    
    def _create_tool_descriptions(self) -> str:
        """Create a description of available Terraform tools for the LLM."""
        if not self.mcp_client.available_tools:
            return "No Terraform tools available."
            
        descriptions = ["Available Terraform tools:"]
        for tool in self.mcp_client.available_tools:
            desc = f"- {tool.name}: {tool.description}"
            if hasattr(tool, 'inputSchema') and tool.inputSchema:
                schema = tool.inputSchema
                if 'properties' in schema:
                    params = list(schema['properties'].keys())
                    desc += f" (Parameters: {', '.join(params)})"
            descriptions.append(desc)
            
        return "\n".join(descriptions)
    
    async def _execute_terraform_tool(self, tool_name: str, arguments: Dict[str, Any]) -> str:
        """Execute a Terraform tool and return formatted results."""
        result = await self.mcp_client.call_tool(tool_name, arguments)
        
        if result["success"]:
            if result.get("is_error", False):
                return f"Tool execution completed with error: {result['content']}"
            else:
                # Format the content nicely
                content = result["content"]
                if isinstance(content, list):
                    formatted_content = []
                    for item in content:
                        if hasattr(item, 'text'):
                            formatted_content.append(item.text)
                        else:
                            formatted_content.append(str(item))
                    return "\n".join(formatted_content)
                else:
                    return str(content)
        else:
            return f"Tool execution failed: {result['error']}"
    
    async def chat(self, user_message: str) -> str:
        """Enhanced chat with Gemini, allowing it to use Terraform tools."""
        
        # Record conversation start
        start_time = datetime.now()
        tools_used = []
        
        try:
            # Create system prompt with tool information
            system_prompt = f"""You are a helpful AI assistant with access to Terraform tools through an MCP server.

{self._create_tool_descriptions()}

When a user asks about Terraform providers, modules, or policies, you can use these tools to get current information.

To use a tool, respond with a JSON object in this format:
{{
    "action": "use_tool",
    "tool_name": "tool_name_here",
    "arguments": {{
        "param1": "value1",
        "param2": "value2"
    }}
}}

If you don't need to use a tool, just respond normally with helpful information.

User message: {user_message}"""

            # Generate initial response
            response = self.model.generate_content(system_prompt)
            response_text = response.text.strip()
            
            # Check if the response contains a tool call
            if response_text.startswith('{') and '"action": "use_tool"' in response_text:
                try:
                    tool_call = json.loads(response_text)
                    tool_name = tool_call["tool_name"]
                    arguments = tool_call["arguments"]
                    
                    logger.info(f"Executing tool: {tool_name} with args: {arguments}")
                    tools_used.append(tool_name)
                    
                    # Update tool usage stats
                    self.tool_usage_stats[tool_name] = self.tool_usage_stats.get(tool_name, 0) + 1
                    
                    # Execute the tool
                    tool_result = await self._execute_terraform_tool(tool_name, arguments)
                    
                    # Generate final response with tool results
                    final_prompt = f"""Based on the tool execution results below, provide a helpful response to the user.

User's original question: {user_message}

Tool used: {tool_name}
Tool results:
{tool_result}

Please provide a clear, helpful response based on these results."""

                    final_response = self.model.generate_content(final_prompt)
                    final_text = final_response.text
                    
                    # Record successful conversation
                    self._record_conversation(user_message, start_time, tools_used, final_text, True)
                    return final_text
                    
                except json.JSONDecodeError:
                    # If JSON parsing fails, return the original response
                    self._record_conversation(user_message, start_time, tools_used, response_text, True)
                    return response_text
            else:
                self._record_conversation(user_message, start_time, tools_used, response_text, True)
                return response_text
                
        except Exception as e:
            error_msg = f"I encountered an error: {e}"
            logger.error(f"Error in chat: {e}")
            self._record_conversation(user_message, start_time, tools_used, error_msg, False)
            return error_msg
    
    def _record_conversation(self, user_message: str, timestamp: datetime, tools_used: List[str], response: str, success: bool):
        """Record conversation in history."""
        context = ConversationContext(
            user_message=user_message,
            timestamp=timestamp,
            tools_used=tools_used,
            response=response,
            success=success
        )
        
        self.conversation_history.append(context)
        
        # Limit conversation history
        if len(self.conversation_history) > self.config.conversation_history_limit:
            self.conversation_history = self.conversation_history[-self.config.conversation_history_limit:]


async def main():
    """Main function to run the Terraform-Gemini integration."""
    
    # Load configuration
    config = get_config()
    
    # Check for required API key
    if not config.gemini.api_key:
        print("Error: GEMINI_API_KEY environment variable is required")
        print("Get your API key from: https://makersuite.google.com/app/apikey")
        print("You can set it as an environment variable or in the config file.")
        sys.exit(1)
    
    # Initialize the agent
    agent = GeminiTerraformAgent(config)
    
    try:
        print("Initializing Terraform-Gemini integration...")
        await agent.initialize()
        print("✅ Connected to Terraform MCP server")
        print("✅ Gemini LLM ready")
        print("\nYou can now ask questions about Terraform providers, modules, and policies!")
        print("Type 'quit' to exit.\n")
        
        # Interactive chat loop
        while True:
            try:
                user_input = input("You: ").strip()
                if user_input.lower() in ['quit', 'exit', 'q']:
                    break
                    
                if not user_input:
                    continue
                    
                print("🤖 Thinking...")
                response = await agent.chat(user_input)
                print(f"Assistant: {response}\n")
                
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"Error: {e}\n")
                
    except Exception as e:
        print(f"Failed to initialize: {e}")
    finally:
        await agent.shutdown()
        print("Goodbye!")


if __name__ == "__main__":
    asyncio.run(main())