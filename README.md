# 🚀 Terraform Chatbot

An intelligent chatbot that generates Terraform code using real-time data from the Terraform registry, powered by Google's Gemini LLM and Terraform MCP Server.

## ✨ Features

- 🤖 **AI-Powered Code Generation**: Generate complete Terraform configurations using Gemini LLM
- 📚 **Real-time Documentation**: Access up-to-date Terraform provider documentation via MCP server
- 🌐 **Web Interface**: Modern, responsive chat interface
- 🔍 **Module Search**: Find and explore Terraform modules from the registry
- 🛡️ **Security Best Practices**: Generated code includes security configurations
- 📊 **Multiple AWS Services**: Support for S3, EC2, VPC, and more

## 🏗️ Architecture

```
User Input → Web UI → Flask Backend → Gemini LLM
                                    ↓
                            Terraform MCP Server
                                    ↓
                            Terraform Registry API
```

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Go 1.19+ (for building MCP server)
- Google Gemini API key

### Installation

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd terraform-chatbot
   ```

2. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Build Terraform MCP Server**
   ```bash
   go build -o terraform-mcp-server.exe ./cmd/terraform-mcp-server
   ```

4. **Set up Gemini API Key**
   ```bash
   # Get your API key from: https://makersuite.google.com/app/apikey
   python setup_gemini_key.py
   ```

5. **Start the chatbot**
   ```bash
   python web_chatbot.py
   ```

6. **Access the interface**
   ```
   http://localhost:3030
   ```

## 🎯 Usage Examples

### Generate S3 Bucket Code
```
User: "Create S3 bucket code with encryption"
Bot: [Generates complete Terraform configuration]
```

### Generate EC2 Instance Code
```
User: "Create EC2 instance with security group"
Bot: [Generates EC2 instance with security configurations]
```

### Find Terraform Modules
```
User: "Show me VPC modules"
Bot: [Lists available VPC modules from registry]
```

## 📁 Project Structure

```
terraform-chatbot/
├── web_chatbot.py              # Flask web server
├── templates/
│   └── chat.html              # Web interface
├── terraform_gemini_integration.py  # Original CLI chatbot
├── config.py                  # Configuration management
├── requirements.txt           # Python dependencies
├── cmd/
│   └── terraform-mcp-server/  # MCP server source
├── go.mod                     # Go dependencies
└── README.md                  # This file
```

## 🔧 Configuration

### Gemini API Configuration
```json
{
  "gemini": {
    "api_key": "your-api-key-here",
    "model_name": "gemini-1.5-flash",
    "temperature": 0.3,
    "max_tokens": 1024
  }
}
```

### MCP Server Configuration
```json
{
  "mcp_server": {
    "server_path": "./terraform-mcp-server.exe",
    "server_args": ["stdio"],
    "timeout": 30
  }
}
```

## 🛠️ Available Tools

The MCP server provides these tools:

- **searchModules**: Find Terraform modules
- **moduleDetails**: Get detailed module information
- **resolveProviderDocID**: Get provider documentation IDs
- **getProviderDocs**: Get detailed provider documentation
- **searchPolicies**: Find security policies
- **policyDetails**: Get detailed policy information

## 🌟 Supported AWS Services

- ✅ **S3**: Buckets, policies, encryption
- ✅ **EC2**: Instances, security groups, key pairs
- ✅ **VPC**: Networks, subnets, routing
- ✅ **IAM**: Roles, policies, users
- ✅ **RDS**: Databases, clusters
- ✅ **Lambda**: Functions, triggers
- 🔄 **More services**: Continuously expanding

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Terraform MCP Server](https://github.com/hashicorp/terraform-mcp-server) by HashiCorp
- [Google Gemini](https://ai.google.dev/) for AI capabilities
- [Terraform Registry](https://registry.terraform.io/) for module data

## 🐛 Troubleshooting

### Common Issues

1. **MCP Server Connection Failed**
   ```bash
   # Rebuild the MCP server
   go build -o terraform-mcp-server.exe ./cmd/terraform-mcp-server
   ```

2. **Gemini API Rate Limits**
   - Use `gemini-1.5-flash` model for fewer rate limits
   - Implement request throttling

3. **Port Already in Use**
   ```bash
   # Change port in web_chatbot.py
   app.run(debug=True, host='0.0.0.0', port=3031)
   ```

## 📞 Support

If you encounter any issues or have questions:

1. Check the [Issues](../../issues) page
2. Create a new issue with detailed information
3. Include logs and error messages

---

**Made with ❤️ for the Terraform community**