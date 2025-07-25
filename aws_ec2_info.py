#!/usr/bin/env python3
"""
Get AWS EC2 information using Terraform MCP server and AWS CLI/SDK.
"""

import asyncio
import json
import subprocess
import boto3
from pathlib import Path

async def get_ec2_terraform_docs():
    """Get EC2 documentation from Terraform MCP server."""
    print("🔍 Getting EC2 Terraform documentation...\n")
    
    server_path = Path("terraform-mcp-server.exe")
    
    init_request = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {"name": "ec2-client", "version": "1.0.0"}
        }
    }
    
    # Get EC2 resource documentation
    ec2_docs_request = {
        "jsonrpc": "2.0",
        "id": 2,
        "method": "tools/call",
        "params": {
            "name": "resolveProviderDocID",
            "arguments": {
                "providerName": "aws",
                "providerNamespace": "hashicorp",
                "serviceSlug": "ec2",
                "providerDataType": "resources"
            }
        }
    }
    
    try:
        process = subprocess.Popen([
            str(server_path), "stdio"
        ], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        input_data = json.dumps(init_request) + "\n" + json.dumps(ec2_docs_request) + "\n"
        stdout, stderr = process.communicate(input=input_data, timeout=30)
        
        if stdout:
            lines = stdout.strip().split('\n')
            for line in lines:
                if line.strip():
                    try:
                        response = json.loads(line)
                        if response.get('id') == 2 and 'result' in response:
                            print("✅ Found EC2 Terraform resources:")
                            content = response['result']['content'][0]['text']
                            # Extract key information
                            if 'aws_instance' in content:
                                print("   • aws_instance - EC2 instances")
                            if 'aws_security_group' in content:
                                print("   • aws_security_group - Security groups")
                            if 'aws_key_pair' in content:
                                print("   • aws_key_pair - Key pairs")
                            print("   • And more EC2-related resources...")
                            return True
                    except json.JSONDecodeError:
                        continue
        
        return False
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def get_ec2_details_boto3():
    """Get actual EC2 details using boto3."""
    print("\n🔍 Getting actual EC2 details from AWS...\n")
    
    try:
        # Initialize EC2 client
        ec2 = boto3.client('ec2')
        
        # Get all instances
        print("📊 EC2 Instances Summary:")
        instances_response = ec2.describe_instances()
        
        total_instances = 0
        running_instances = 0
        stopped_instances = 0
        instance_types = {}
        
        for reservation in instances_response['Reservations']:
            for instance in reservation['Instances']:
                total_instances += 1
                state = instance['State']['Name']
                instance_type = instance['InstanceType']
                
                if state == 'running':
                    running_instances += 1
                elif state == 'stopped':
                    stopped_instances += 1
                
                instance_types[instance_type] = instance_types.get(instance_type, 0) + 1
        
        print(f"   Total Instances: {total_instances}")
        print(f"   Running: {running_instances}")
        print(f"   Stopped: {stopped_instances}")
        print(f"   Other States: {total_instances - running_instances - stopped_instances}")
        
        print("\n📋 Instance Types:")
        for itype, count in sorted(instance_types.items()):
            print(f"   {itype}: {count}")
        
        # Get security groups
        print("\n🛡️ Security Groups:")
        sg_response = ec2.describe_security_groups()
        print(f"   Total Security Groups: {len(sg_response['SecurityGroups'])}")
        
        # Get key pairs
        print("\n🔑 Key Pairs:")
        kp_response = ec2.describe_key_pairs()
        print(f"   Total Key Pairs: {len(kp_response['KeyPairs'])}")
        
        # Get volumes
        print("\n💾 EBS Volumes:")
        vol_response = ec2.describe_volumes()
        total_size = sum(vol['Size'] for vol in vol_response['Volumes'])
        print(f"   Total Volumes: {len(vol_response['Volumes'])}")
        print(f"   Total Size: {total_size} GB")
        
        # Get AMIs (owned by you)
        print("\n🖼️ AMIs (Your Account):")
        ami_response = ec2.describe_images(Owners=['self'])
        print(f"   Your AMIs: {len(ami_response['Images'])}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error accessing AWS: {e}")
        print("\n💡 Make sure you have:")
        print("   1. AWS CLI configured: aws configure")
        print("   2. Valid AWS credentials")
        print("   3. Appropriate IAM permissions")
        return False

def get_ec2_details_cli():
    """Get EC2 details using AWS CLI."""
    print("\n🔍 Getting EC2 details via AWS CLI...\n")
    
    try:
        # Test AWS CLI access
        result = subprocess.run(['aws', 'sts', 'get-caller-identity'], 
                              capture_output=True, text=True, timeout=10)
        
        if result.returncode != 0:
            print("❌ AWS CLI not configured or accessible")
            return False
        
        print("✅ AWS CLI access confirmed")
        
        # Get instances summary
        cmd = [
            'aws', 'ec2', 'describe-instances',
            '--query', 'Reservations[].Instances[].[InstanceId,State.Name,InstanceType]',
            '--output', 'table'
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print("\n📊 EC2 Instances:")
            print(result.stdout)
        else:
            print(f"❌ Error getting instances: {result.stderr}")
        
        return True
        
    except FileNotFoundError:
        print("❌ AWS CLI not installed")
        print("   Install: https://aws.amazon.com/cli/")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

async def main():
    """Main function."""
    print("🚀 AWS EC2 Details Retrieval\n")
    
    # Get Terraform documentation first
    await get_ec2_terraform_docs()
    
    # Try boto3 first (more detailed)
    if not get_ec2_details_boto3():
        # Fall back to AWS CLI
        get_ec2_details_cli()
    
    print("\n🎉 EC2 details retrieval completed!")
    print("\n📋 Summary of what you can get:")
    print("✅ Instance counts and states")
    print("✅ Instance types distribution")
    print("✅ Security groups")
    print("✅ Key pairs")
    print("✅ EBS volumes and sizes")
    print("✅ AMIs in your account")

if __name__ == "__main__":
    asyncio.run(main())