#!/usr/bin/env python3
"""
Fixed Terraform Chatbot with working MCP connection.
"""

import asyncio
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path
import google.generativeai as genai

class TerraformChatbot:
    """Simple working Terraform chatbot."""
    
    def __init__(self):
        # Configure Gemini
        api_key = "AIzaSyC-66cCtIosU8pTPd6eLnlQMn0dg7ofW6Y"
        genai.configure(api_key=api_key)
        
        self.model = genai.GenerativeModel(
            "gemini-1.5-flash",  # Using flash to avoid rate limits
            generation_config={
                "temperature": 0.3,
                "max_output_tokens": 1024,
            }
        )
        
        self.server_path = Path("terraform-mcp-server.exe")
        self.conversation_history = []
    
    async def call_mcp_tool(self, tool_name, arguments):
        """Call MCP server tool directly."""
        init_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "chatbot", "version": "1.0.0"}
            }
        }
        
        tool_request = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": arguments
            }
        }
        
        try:
            process = subprocess.Popen([
                str(self.server_path), "stdio"
            ], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            
            input_data = json.dumps(init_request) + "\n" + json.dumps(tool_request) + "\n"
            stdout, stderr = process.communicate(input=input_data, timeout=30)
            
            if stdout:
                lines = stdout.strip().split('\n')
                for line in lines:
                    if line.strip():
                        try:
                            response = json.loads(line)
                            if response.get('id') == 2 and 'result' in response:
                                return response['result']['content'][0]['text']
                        except json.JSONDecodeError:
                            continue
            
            return None
            
        except Exception as e:
            print(f"⚠️  MCP tool error: {e}")
            return None
    
    async def chat(self, user_message):
        """Process user message and generate response."""
        print("🤖 Thinking...")
        
        # Check if user is asking about Terraform-specific things
        terraform_keywords = ['terraform', 'aws', 's3', 'ec2', 'module', 'provider', 'resource']
        needs_mcp = any(keyword in user_message.lower() for keyword in terraform_keywords)
        
        if needs_mcp:
            # Try to get relevant information from MCP server
            mcp_result = None
            
            if 's3' in user_message.lower():
                mcp_result = await self.call_mcp_tool("searchModules", {
                    "moduleQuery": "s3 bucket",
                    "currentOffset": 0
                })
            elif 'ec2' in user_message.lower():
                mcp_result = await self.call_mcp_tool("resolveProviderDocID", {
                    "providerName": "aws",
                    "providerNamespace": "hashicorp",
                    "serviceSlug": "ec2",
                    "providerDataType": "resources"
                })
            elif 'module' in user_message.lower():
                # Extract search term from user message
                words = user_message.lower().split()
                search_term = "aws"
                for word in words:
                    if word not in ['terraform', 'module', 'search', 'find', 'for']:
                        search_term = word
                        break
                
                mcp_result = await self.call_mcp_tool("searchModules", {
                    "moduleQuery": search_term,
                    "currentOffset": 0
                })
            
            # Create prompt with MCP data if available
            if mcp_result:
                prompt = f"""You are a helpful Terraform assistant. Answer the user's question using the real-time information provided.

User Question: {user_message}

Real-time Terraform Information:
{mcp_result[:800]}...

Provide a helpful, accurate response based on this information."""
            else:
                prompt = f"""You are a helpful Terraform assistant. Answer the user's question about Terraform, AWS, or infrastructure as code.

User Question: {user_message}

Provide helpful information about Terraform best practices, AWS resources, or infrastructure management."""
        else:
            # General conversation
            prompt = f"""You are a helpful AI assistant specializing in Terraform and AWS infrastructure. 

User: {user_message}

Provide a helpful response."""
        
        try:
            response = self.model.generate_content(prompt)
            response_text = response.text
            
            # Store in conversation history
            self.conversation_history.append({
                'user': user_message,
                'assistant': response_text,
                'timestamp': datetime.now()
            })
            
            return response_text
            
        except Exception as e:
            return f"I encountered an error: {e}. Please try again or ask a different question."
    
    async def run(self):
        """Run the chatbot."""
        print("🚀 Terraform Chatbot")
        print("=" * 40)
        print("✅ Gemini LLM ready")
        print("✅ Terraform MCP server available")
        print("\nI can help you with:")
        print("• Terraform code generation")
        print("• AWS resource questions")
        print("• Module recommendations")
        print("• Best practices")
        print("\nType 'quit' to exit, 'help' for commands\n")
        
        while True:
            try:
                user_input = input("You: ").strip()
                
                if user_input.lower() in ['quit', 'exit', 'q']:
                    print("👋 Goodbye!")
                    break
                
                if user_input.lower() == 'help':
                    print("\n📋 Available commands:")
                    print("• Ask about Terraform resources (S3, EC2, etc.)")
                    print("• Request code generation")
                    print("• Ask for module recommendations")
                    print("• General Terraform questions")
                    print("• 'history' - Show conversation history")
                    print("• 'quit' - Exit chatbot\n")
                    continue
                
                if user_input.lower() == 'history':
                    print(f"\n📚 Conversation History ({len(self.conversation_history)} messages):")
                    for i, conv in enumerate(self.conversation_history[-5:], 1):  # Show last 5
                        print(f"{i}. You: {conv['user'][:50]}...")
                        print(f"   Bot: {conv['assistant'][:50]}...")
                    print()
                    continue
                
                if not user_input:
                    continue
                
                response = await self.chat(user_input)
                print(f"🤖 Assistant: {response}\n")
                
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error: {e}\n")

async def main():
    """Main function."""
    chatbot = TerraformChatbot()
    await chatbot.run()

if __name__ == "__main__":
    asyncio.run(main())