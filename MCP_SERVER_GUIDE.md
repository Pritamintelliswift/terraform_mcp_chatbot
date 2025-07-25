# Terraform MCP Server - Testing and Usage Guide

## Overview
The Terraform MCP (Model Context Protocol) server provides AI assistants with access to Terraform documentation, modules, and policies through a standardized interface.

## Quick Status Check

### 1. Check if Server is Built
```bash
# Check if the binary exists
ls terraform-mcp-server.exe

# If not built, build it:
go build -o terraform-mcp-server.exe ./cmd/terraform-mcp-server
```

### 2. Test Server Functionality
```bash
# Test help command
.\terraform-mcp-server.exe --help

# Test version
.\terraform-mcp-server.exe --version
```

### 3. Run Comprehensive Tests
```bash
# Simple connection test
py simple_mcp_test.py

# Detailed tool analysis
py quick_test.py

# Demo integration
py demo_integration.py
```

## Available Tools

The server provides 6 main tools:

### 1. `searchModules`
- **Purpose**: Search for Terraform modules
- **Parameters**: 
  - `moduleQuery` (required): Search query
  - `currentOffset` (optional): Pagination offset
- **Example**: Search for "vpc" modules

### 2. `moduleDetails`
- **Purpose**: Get detailed module documentation
- **Parameters**: 
  - `moduleID` (required): Module ID from searchModules
- **Note**: Must call `searchModules` first

### 3. `resolveProviderDocID`
- **Purpose**: Find provider documentation IDs
- **Parameters**:
  - `providerName` (required): e.g., "aws"
  - `providerNamespace` (required): e.g., "hashicorp"
  - `serviceSlug` (required): e.g., "ec2"
  - `providerDataType` (optional): "resources", "data-sources", "guides", etc.

### 4. `getProviderDocs`
- **Purpose**: Get provider documentation
- **Parameters**:
  - `providerDocID` (required): ID from resolveProviderDocID
- **Note**: Must call `resolveProviderDocID` first

### 5. `searchPolicies`
- **Purpose**: Search for Terraform policies
- **Parameters**:
  - `policyQuery` (required): Search query

### 6. `policyDetails`
- **Purpose**: Get detailed policy documentation
- **Parameters**:
  - `terraformPolicyID` (required): Policy ID from searchPolicies
- **Note**: Must call `searchPolicies` first

## Usage Patterns

### Typical Workflow for Modules:
1. `searchModules` → Get list of modules
2. `moduleDetails` → Get specific module documentation

### Typical Workflow for Providers:
1. `resolveProviderDocID` → Find documentation IDs
2. `getProviderDocs` → Get specific documentation

### Typical Workflow for Policies:
1. `searchPolicies` → Find policies
2. `policyDetails` → Get policy documentation

## Integration with AI Assistants

The server communicates via JSON-RPC over stdio, making it compatible with:
- MCP-compatible AI assistants
- Custom integrations
- Direct API calls

## Example JSON-RPC Requests

### Initialize Connection:
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "initialize",
  "params": {
    "protocolVersion": "2024-11-05",
    "capabilities": {},
    "clientInfo": {"name": "client", "version": "1.0.0"}
  }
}
```

### Search Modules:
```json
{
  "jsonrpc": "2.0",
  "id": 2,
  "method": "tools/call",
  "params": {
    "name": "searchModules",
    "arguments": {
      "moduleQuery": "vpc",
      "currentOffset": 0
    }
  }
}
```

## Troubleshooting

### Common Issues:
1. **Server not found**: Build with `go build -o terraform-mcp-server.exe ./cmd/terraform-mcp-server`
2. **Connection timeout**: Check if server starts with `.\terraform-mcp-server.exe stdio`
3. **Tool errors**: Ensure required parameters are provided
4. **Missing dependencies**: Run `py -m pip install -r requirements.txt`

### Debug Commands:
```bash
# Test server startup
.\terraform-mcp-server.exe stdio

# Check server logs
.\terraform-mcp-server.exe --log-file debug.log stdio

# Test with verbose output
.\terraform-mcp-server.exe stdio --verbose
```

## Status: ✅ WORKING

The Terraform MCP server is fully functional and ready for integration with AI assistants and other MCP clients.