# Windows Setup Guide for Terraform MCP + Gemini Integration

This guide will help you set up the Terraform MCP server with Gemini LLM integration on Windows.

## Prerequisites Installation

### 1. Install Python 3.8+

**Option A: Download from Python.org (Recommended)**
1. Go to https://www.python.org/downloads/
2. Download Python 3.11 or later
3. **Important**: During installation, check "Add Python to PATH"
4. Verify installation:
   ```cmd
   python --version
   pip --version
   ```

**Option B: Using Windows Package Manager (winget)**
```powershell
winget install Python.Python.3.11
```

**Option C: Using Chocolatey**
```powershell
choco install python
```

### 2. Install Go 1.19+

**Option A: Download from Go.dev (Recommended)**
1. Go to https://golang.org/dl/
2. Download the Windows installer
3. Run the installer (it will automatically add Go to PATH)
4. Verify installation:
   ```cmd
   go version
   ```

**Option B: Using Windows Package Manager (winget)**
```powershell
winget install GoLang.Go
```

**Option C: Using Chocolatey**
```powershell
choco install golang
```

### 3. Get Gemini API Key

1. Go to https://makersuite.google.com/app/apikey
2. Sign in with your Google account
3. Create a new API key
4. Copy the API key (you already have: `AIzaSyC-66cCtIosU8pTPd6eLnlQMn0dg7ofW6Y`)

## Setup Steps

### 1. Set Environment Variables

**PowerShell:**
```powershell
$env:GEMINI_API_KEY="AIzaSyC-66cCtIosU8pTPd6eLnlQMn0dg7ofW6Y"
```

**Command Prompt:**
```cmd
set GEMINI_API_KEY=AIzaSyC-66cCtIosU8pTPd6eLnlQMn0dg7ofW6Y
```

**Permanent (System Environment Variables):**
1. Press `Win + R`, type `sysdm.cpl`, press Enter
2. Click "Environment Variables"
3. Under "User variables", click "New"
4. Variable name: `GEMINI_API_KEY`
5. Variable value: `AIzaSyC-66cCtIosU8pTPd6eLnlQMn0dg7ofW6Y`

### 2. Install Python Dependencies

```powershell
pip install -r requirements.txt
```

### 3. Build the Terraform MCP Server

```powershell
go build -o terraform-mcp-server.exe ./cmd/terraform-mcp-server
```

### 4. Test the Setup

```powershell
python quick_test.py
```

### 5. Run the Integration

```powershell
python terraform_gemini_integration.py
```

## Troubleshooting

### Python Issues

**"Python was not found"**
- Reinstall Python and ensure "Add Python to PATH" is checked
- Or manually add Python to PATH:
  1. Find Python installation (usually `C:\Users\[username]\AppData\Local\Programs\Python\Python311\`)
  2. Add to PATH environment variable

**"pip is not recognized"**
- Python installation issue, reinstall Python
- Or use: `python -m pip install -r requirements.txt`

### Go Issues

**"go is not recognized"**
- Reinstall Go from https://golang.org/dl/
- Restart your terminal/PowerShell after installation
- Check PATH includes Go bin directory

### MCP Server Issues

**"Failed to connect to MCP server"**
- Ensure the server is built: `go build -o terraform-mcp-server.exe ./cmd/terraform-mcp-server`
- Check if the executable exists: `ls terraform-mcp-server.exe`
- Try running the server directly: `.\terraform-mcp-server.exe stdio`

### Gemini API Issues

**"GEMINI_API_KEY not configured"**
- Verify the environment variable is set: `echo $env:GEMINI_API_KEY`
- Check the API key is valid at https://makersuite.google.com/app/apikey

## Alternative: Using Windows Subsystem for Linux (WSL)

If you prefer a Linux environment:

1. Install WSL2:
   ```powershell
   wsl --install
   ```

2. Install Ubuntu from Microsoft Store

3. In WSL Ubuntu terminal:
   ```bash
   # Install Python
   sudo apt update
   sudo apt install python3 python3-pip
   
   # Install Go
   sudo apt install golang-go
   
   # Set environment variable
   export GEMINI_API_KEY="AIzaSyC-66cCtIosU8pTPd6eLnlQMn0dg7ofW6Y"
   
   # Install dependencies and build
   pip3 install -r requirements.txt
   go build -o terraform-mcp-server ./cmd/terraform-mcp-server
   
   # Run the integration
   python3 terraform_gemini_integration.py
   ```

## Next Steps

Once everything is installed and working:

1. **Test the connection**: `python test_mcp_connection.py`
2. **Run the demo**: `python demo_integration.py`
3. **Start chatting**: `python terraform_gemini_integration.py`

## Example Usage

Once running, you can ask questions like:

- "Show me AWS EC2 documentation"
- "Find Terraform modules for creating a VPC"
- "What are security policies for AWS resources?"
- "How do I configure an Azure storage account?"

The integration will use your Terraform MCP server to fetch real-time information and provide helpful responses through Gemini LLM.