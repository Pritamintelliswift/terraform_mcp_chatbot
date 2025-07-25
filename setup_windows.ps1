# Windows PowerShell Setup Script for Terraform MCP + Gemini Integration

Write-Host "🚀 Setting up Terraform MCP + Gemini Integration on Windows" -ForegroundColor Green
Write-Host "=" * 60

# Function to check if a command exists
function Test-Command($cmdname) {
    return [bool](Get-Command -Name $cmdname -ErrorAction SilentlyContinue)
}

# Function to install using winget if available
function Install-WithWinget($package, $name) {
    if (Test-Command "winget") {
        Write-Host "📦 Installing $name using winget..." -ForegroundColor Yellow
        winget install $package
        return $true
    }
    return $false
}

# Check Python installation
Write-Host "`n🐍 Checking Python installation..." -ForegroundColor Cyan
if (Test-Command "python") {
    $pythonVersion = python --version 2>&1
    if ($pythonVersion -match "Python (\d+)\.(\d+)") {
        $major = [int]$matches[1]
        $minor = [int]$matches[2]
        if ($major -ge 3 -and $minor -ge 8) {
            Write-Host "✅ Python $pythonVersion found" -ForegroundColor Green
        } else {
            Write-Host "❌ Python version too old: $pythonVersion" -ForegroundColor Red
            Write-Host "   Please install Python 3.8 or later" -ForegroundColor Yellow
        }
    }
} else {
    Write-Host "❌ Python not found" -ForegroundColor Red
    Write-Host "📥 Attempting to install Python..." -ForegroundColor Yellow
    
    if (-not (Install-WithWinget "Python.Python.3.11" "Python")) {
        Write-Host "⚠️  Please install Python manually from https://www.python.org/downloads/" -ForegroundColor Yellow
        Write-Host "   Make sure to check 'Add Python to PATH' during installation" -ForegroundColor Yellow
        Read-Host "Press Enter after installing Python to continue"
    }
}

# Check Go installation
Write-Host "`n🔧 Checking Go installation..." -ForegroundColor Cyan
if (Test-Command "go") {
    $goVersion = go version
    Write-Host "✅ $goVersion found" -ForegroundColor Green
} else {
    Write-Host "❌ Go not found" -ForegroundColor Red
    Write-Host "📥 Attempting to install Go..." -ForegroundColor Yellow
    
    if (-not (Install-WithWinget "GoLang.Go" "Go")) {
        Write-Host "⚠️  Please install Go manually from https://golang.org/dl/" -ForegroundColor Yellow
        Read-Host "Press Enter after installing Go to continue"
    }
}

# Set Gemini API Key
Write-Host "`n🔑 Setting up Gemini API Key..." -ForegroundColor Cyan
$apiKey = "AIzaSyC-66cCtIosU8pTPd6eLnlQMn0dg7ofW6Y"
$env:GEMINI_API_KEY = $apiKey
Write-Host "✅ GEMINI_API_KEY set for this session" -ForegroundColor Green

# Ask if user wants to set it permanently
$setPermanent = Read-Host "Do you want to set GEMINI_API_KEY permanently? (y/n)"
if ($setPermanent -eq "y" -or $setPermanent -eq "Y") {
    [Environment]::SetEnvironmentVariable("GEMINI_API_KEY", $apiKey, "User")
    Write-Host "✅ GEMINI_API_KEY set permanently for current user" -ForegroundColor Green
}

# Install Python dependencies
Write-Host "`n📦 Installing Python dependencies..." -ForegroundColor Cyan
try {
    if (Test-Command "pip") {
        pip install -r requirements.txt
        Write-Host "✅ Python dependencies installed" -ForegroundColor Green
    } else {
        python -m pip install -r requirements.txt
        Write-Host "✅ Python dependencies installed" -ForegroundColor Green
    }
} catch {
    Write-Host "❌ Failed to install Python dependencies: $_" -ForegroundColor Red
    Write-Host "   Please run: pip install -r requirements.txt" -ForegroundColor Yellow
}

# Build Terraform MCP Server
Write-Host "`n🔨 Building Terraform MCP Server..." -ForegroundColor Cyan
try {
    if (Test-Command "go") {
        go build -o terraform-mcp-server.exe ./cmd/terraform-mcp-server
        if (Test-Path "terraform-mcp-server.exe") {
            Write-Host "✅ Terraform MCP Server built successfully" -ForegroundColor Green
        } else {
            Write-Host "❌ Failed to build Terraform MCP Server" -ForegroundColor Red
        }
    } else {
        Write-Host "❌ Go not available, cannot build MCP server" -ForegroundColor Red
    }
} catch {
    Write-Host "❌ Error building MCP server: $_" -ForegroundColor Red
}

# Run quick test
Write-Host "`n🧪 Running quick test..." -ForegroundColor Cyan
try {
    if (Test-Command "python") {
        python quick_test.py
    } else {
        Write-Host "❌ Python not available for testing" -ForegroundColor Red
    }
} catch {
    Write-Host "⚠️  Quick test encountered issues: $_" -ForegroundColor Yellow
}

Write-Host "`n🎉 Setup completed!" -ForegroundColor Green
Write-Host "`nNext steps:" -ForegroundColor Cyan
Write-Host "1. If any installations failed, please install manually" -ForegroundColor White
Write-Host "2. Restart your PowerShell/terminal if you installed new software" -ForegroundColor White
Write-Host "3. Run: python terraform_gemini_integration.py" -ForegroundColor White
Write-Host "4. Or run demo: python demo_integration.py" -ForegroundColor White

Write-Host "`nFor troubleshooting, see WINDOWS_SETUP.md" -ForegroundColor Yellow