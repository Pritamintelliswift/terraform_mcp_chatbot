@echo off
REM Windows Batch Setup Script for Terraform MCP + Gemini Integration

echo 🚀 Setting up Terraform MCP + Gemini Integration on Windows
echo ============================================================

REM Check Python installation
echo.
echo 🐍 Checking Python installation...
python --version >nul 2>&1
if %errorlevel% == 0 (
    echo ✅ Python found
    python --version
) else (
    echo ❌ Python not found
    echo Please install Python from https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation
    pause
    goto :eof
)

REM Check Go installation
echo.
echo 🔧 Checking Go installation...
go version >nul 2>&1
if %errorlevel% == 0 (
    echo ✅ Go found
    go version
) else (
    echo ❌ Go not found
    echo Please install Go from https://golang.org/dl/
    pause
    goto :eof
)

REM Set Gemini API Key
echo.
echo 🔑 Setting up Gemini API Key...
set GEMINI_API_KEY=AIzaSyC-66cCtIosU8pTPd6eLnlQMn0dg7ofW6Y
echo ✅ GEMINI_API_KEY set for this session

REM Install Python dependencies
echo.
echo 📦 Installing Python dependencies...
pip install -r requirements.txt
if %errorlevel% == 0 (
    echo ✅ Python dependencies installed
) else (
    echo ❌ Failed to install Python dependencies
    echo Please run: pip install -r requirements.txt
    pause
)

REM Build Terraform MCP Server
echo.
echo 🔨 Building Terraform MCP Server...
go build -o terraform-mcp-server.exe ./cmd/terraform-mcp-server
if exist terraform-mcp-server.exe (
    echo ✅ Terraform MCP Server built successfully
) else (
    echo ❌ Failed to build Terraform MCP Server
    pause
)

REM Run quick test
echo.
echo 🧪 Running quick test...
python quick_test.py

echo.
echo 🎉 Setup completed!
echo.
echo Next steps:
echo 1. Run: python terraform_gemini_integration.py
echo 2. Or run demo: python demo_integration.py
echo.
echo For troubleshooting, see WINDOWS_SETUP.md
pause