#!/usr/bin/env python3
"""
Web-based Terraform Chatbot with UI.
"""

from flask import Flask, render_template, request, jsonify, send_from_directory
import asyncio
import json
import subprocess
import threading
from datetime import datetime
from pathlib import Path
import google.generativeai as genai

app = Flask(__name__)

class TerraformWebChatbot:
    """Web-based Terraform chatbot."""
    
    def __init__(self):
        # Configure Gemini
        api_key = "AIzaSyC-66cCtIosU8pTPd6eLnlQMn0dg7ofW6Y"
        genai.configure(api_key=api_key)
        
        self.model = genai.GenerativeModel(
            "gemini-1.5-flash",
            generation_config={
                "temperature": 0.3,
                "max_output_tokens": 1024,
            }
        )
        
        self.server_path = Path("terraform-mcp-server.exe")
        self.conversation_history = []
    
    async def call_mcp_tool(self, tool_name, arguments):
        """Call MCP server tool."""
        init_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "web-chatbot", "version": "1.0.0"}
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
            return f"MCP Error: {e}"
    
    async def chat(self, user_message):
        """Process user message and generate response."""
        # Check if user is asking about Terraform-specific things
        terraform_keywords = ['terraform', 'aws', 's3', 'ec2', 'module', 'provider', 'resource']
        needs_mcp = any(keyword in user_message.lower() for keyword in terraform_keywords)
        
        mcp_result = None
        if needs_mcp:
            if 's3' in user_message.lower():
                # Check if user wants code generation
                code_keywords = ['code', 'create', 'generate', 'terraform', 'script']
                wants_code = any(keyword in user_message.lower() for keyword in code_keywords)
                
                if wants_code:
                    # Get detailed S3 provider documentation for code generation
                    provider_result = await self.call_mcp_tool("resolveProviderDocID", {
                        "providerName": "aws",
                        "providerNamespace": "hashicorp",
                        "serviceSlug": "s3",
                        "providerDataType": "resources"
                    })
                    
                    # Try to get specific S3 bucket documentation
                    if provider_result and "s3_bucket" in provider_result:
                        # Extract a provider doc ID for s3_bucket if available
                        lines = provider_result.split('\n')
                        s3_bucket_id = None
                        for line in lines:
                            if 's3_bucket' in line and 'providerDocID:' in line:
                                parts = line.split('providerDocID:')
                                if len(parts) > 1:
                                    s3_bucket_id = parts[1].strip().split()[0]
                                    break
                        
                        if s3_bucket_id:
                            mcp_result = await self.call_mcp_tool("getProviderDocs", {
                                "providerDocID": s3_bucket_id
                            })
                        else:
                            mcp_result = provider_result
                    else:
                        mcp_result = provider_result
                else:
                    # Just search for modules for general information
                    mcp_result = await self.call_mcp_tool("searchModules", {
                        "moduleQuery": "s3 bucket",
                        "currentOffset": 0
                    })
            elif 'ec2' in user_message.lower():
                # First get the provider doc ID for EC2 instance
                provider_result = await self.call_mcp_tool("resolveProviderDocID", {
                    "providerName": "aws",
                    "providerNamespace": "hashicorp",
                    "serviceSlug": "instance",
                    "providerDataType": "resources"
                })
                
                # Then get the detailed documentation
                if provider_result and "providerDocID: 9503899" in provider_result:
                    mcp_result = await self.call_mcp_tool("getProviderDocs", {
                        "providerDocID": "9503899"
                    })
                else:
                    mcp_result = provider_result
            elif 'module' in user_message.lower():
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
        
        # Create prompt
        if mcp_result and "Error:" not in str(mcp_result):
            # Check if user is asking for code generation
            code_keywords = ['code', 'create', 'generate', 'terraform', 'script', 'configuration']
            wants_code = any(keyword in user_message.lower() for keyword in code_keywords)
            
            if wants_code:
                prompt = f"""You are a Terraform code generator. The user wants actual Terraform code, not just documentation or module information.

User Request: {user_message}

Available Terraform Information:
{mcp_result[:800]}...

IMPORTANT: Generate complete, working Terraform code that the user can copy and use immediately. Include:
1. Provider configuration
2. Resource definitions
3. Variables (if needed)
4. Outputs (if useful)
5. Comments explaining the code

Format the code in proper Terraform syntax with code blocks. Don't just describe modules - provide actual .tf file content."""
            else:
                prompt = f"""You are a helpful Terraform assistant. Answer the user's question using the real-time information provided.

User Question: {user_message}

Real-time Terraform Information:
{mcp_result[:800]}...

Provide a helpful, accurate response based on this information. Format your response nicely for web display."""
        else:
            prompt = f"""You are a helpful Terraform assistant. Answer the user's question about Terraform, AWS, or infrastructure as code.

User Question: {user_message}

Provide helpful information about Terraform best practices, AWS resources, or infrastructure management. Format your response nicely for web display."""
        
        try:
            response = self.model.generate_content(prompt)
            response_text = response.text
            
            # Store in conversation history
            self.conversation_history.append({
                'user': user_message,
                'assistant': response_text,
                'timestamp': datetime.now().strftime('%H:%M:%S'),
                'used_mcp': mcp_result is not None
            })
            
            return response_text
            
        except Exception as e:
            return f"I encountered an error: {e}. Please try again or ask a different question."

# Global chatbot instance
chatbot = TerraformWebChatbot()

@app.route('/')
def index():
    """Main chat interface."""
    return render_template('chat.html')

@app.route('/api/chat', methods=['POST'])
def chat_api():
    """Chat API endpoint."""
    data = request.get_json()
    user_message = data.get('message', '').strip()
    
    if not user_message:
        return jsonify({'error': 'Empty message'}), 400
    
    # Run async chat in thread
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    try:
        response = loop.run_until_complete(chatbot.chat(user_message))
        return jsonify({
            'response': response,
            'timestamp': datetime.now().strftime('%H:%M:%S')
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        loop.close()

@app.route('/api/history')
def get_history():
    """Get conversation history."""
    return jsonify({
        'history': chatbot.conversation_history[-10:]  # Last 10 messages
    })

@app.route('/api/clear')
def clear_history():
    """Clear conversation history."""
    chatbot.conversation_history.clear()
    return jsonify({'status': 'cleared'})

if __name__ == '__main__':
    print("🚀 Starting Terraform Chatbot Web UI...")
    print("📱 Access your chatbot at: http://localhost:3030")
    print("🛑 Press Ctrl+C to stop")
    
    app.run(debug=True, host='0.0.0.0', port=3030)