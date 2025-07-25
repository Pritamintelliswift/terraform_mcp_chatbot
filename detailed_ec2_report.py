#!/usr/bin/env python3
"""
Detailed AWS EC2 report with comprehensive information.
"""

import boto3
import json
from datetime import datetime
from botocore.exceptions import ClientError, NoCredentialsError

def get_detailed_ec2_report():
    """Generate a comprehensive EC2 report."""
    print("🚀 AWS EC2 Detailed Report")
    print("=" * 50)
    
    try:
        ec2 = boto3.client('ec2')
        
        # Get account info
        sts = boto3.client('sts')
        identity = sts.get_caller_identity()
        print(f"📋 Account ID: {identity['Account']}")
        print(f"🌍 Region: {ec2.meta.region_name}")
        print(f"⏰ Report Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        # Detailed instance information
        print("🖥️ EC2 INSTANCES")
        print("-" * 30)
        
        instances_response = ec2.describe_instances()
        
        if not instances_response['Reservations']:
            print("   No instances found")
        else:
            instance_count = 0
            for reservation in instances_response['Reservations']:
                for instance in reservation['Instances']:
                    instance_count += 1
                    print(f"\n   Instance #{instance_count}:")
                    print(f"   • ID: {instance['InstanceId']}")
                    print(f"   • Type: {instance['InstanceType']}")
                    print(f"   • State: {instance['State']['Name']}")
                    print(f"   • Launch Time: {instance.get('LaunchTime', 'N/A')}")
                    
                    if 'PublicIpAddress' in instance:
                        print(f"   • Public IP: {instance['PublicIpAddress']}")
                    if 'PrivateIpAddress' in instance:
                        print(f"   • Private IP: {instance['PrivateIpAddress']}")
                    
                    # Tags
                    if 'Tags' in instance:
                        tags = {tag['Key']: tag['Value'] for tag in instance['Tags']}
                        if 'Name' in tags:
                            print(f"   • Name: {tags['Name']}")
                        if tags:
                            print(f"   • Tags: {len(tags)} total")
                    
                    # Security Groups
                    if 'SecurityGroups' in instance:
                        sg_names = [sg['GroupName'] for sg in instance['SecurityGroups']]
                        print(f"   • Security Groups: {', '.join(sg_names)}")
        
        # Security Groups Details
        print(f"\n🛡️ SECURITY GROUPS")
        print("-" * 30)
        
        sg_response = ec2.describe_security_groups()
        for sg in sg_response['SecurityGroups'][:5]:  # Show first 5
            print(f"\n   • {sg['GroupName']} ({sg['GroupId']})")
            print(f"     Description: {sg['Description']}")
            print(f"     VPC: {sg.get('VpcId', 'EC2-Classic')}")
            print(f"     Inbound Rules: {len(sg['IpPermissions'])}")
            print(f"     Outbound Rules: {len(sg['IpPermissionsEgress'])}")
        
        if len(sg_response['SecurityGroups']) > 5:
            print(f"\n   ... and {len(sg_response['SecurityGroups']) - 5} more")
        
        # EBS Volumes
        print(f"\n💾 EBS VOLUMES")
        print("-" * 30)
        
        vol_response = ec2.describe_volumes()
        total_size = 0
        for vol in vol_response['Volumes']:
            total_size += vol['Size']
            print(f"\n   • {vol['VolumeId']}")
            print(f"     Size: {vol['Size']} GB")
            print(f"     Type: {vol['VolumeType']}")
            print(f"     State: {vol['State']}")
            print(f"     Encrypted: {vol['Encrypted']}")
            
            if vol['Attachments']:
                att = vol['Attachments'][0]
                print(f"     Attached to: {att['InstanceId']} as {att['Device']}")
        
        print(f"\n   📊 Total Storage: {total_size} GB")
        
        # Key Pairs
        print(f"\n🔑 KEY PAIRS")
        print("-" * 30)
        
        kp_response = ec2.describe_key_pairs()
        for kp in kp_response['KeyPairs'][:10]:  # Show first 10
            print(f"   • {kp['KeyName']}")
            if 'CreateTime' in kp:
                print(f"     Created: {kp['CreateTime']}")
        
        if len(kp_response['KeyPairs']) > 10:
            print(f"   ... and {len(kp_response['KeyPairs']) - 10} more")
        
        # VPCs
        print(f"\n🌐 VPCs")
        print("-" * 30)
        
        vpc_response = ec2.describe_vpcs()
        for vpc in vpc_response['Vpcs']:
            is_default = vpc.get('IsDefault', False)
            default_text = " (Default)" if is_default else ""
            print(f"   • {vpc['VpcId']}{default_text}")
            print(f"     CIDR: {vpc['CidrBlock']}")
            print(f"     State: {vpc['State']}")
        
        # Subnets
        print(f"\n🏠 SUBNETS")
        print("-" * 30)
        
        subnet_response = ec2.describe_subnets()
        subnet_count = len(subnet_response['Subnets'])
        print(f"   Total Subnets: {subnet_count}")
        
        # Group by VPC
        vpc_subnets = {}
        for subnet in subnet_response['Subnets']:
            vpc_id = subnet['VpcId']
            if vpc_id not in vpc_subnets:
                vpc_subnets[vpc_id] = []
            vpc_subnets[vpc_id].append(subnet)
        
        for vpc_id, subnets in vpc_subnets.items():
            print(f"\n   VPC {vpc_id}: {len(subnets)} subnets")
            for subnet in subnets[:3]:  # Show first 3 per VPC
                print(f"     • {subnet['SubnetId']} ({subnet['CidrBlock']})")
                print(f"       AZ: {subnet['AvailabilityZone']}")
        
        # Cost estimation (rough)
        print(f"\n💰 ESTIMATED MONTHLY COSTS")
        print("-" * 30)
        
        running_instances = 0
        stopped_instances = 0
        instance_costs = 0
        
        for reservation in instances_response['Reservations']:
            for instance in reservation['Instances']:
                if instance['State']['Name'] == 'running':
                    running_instances += 1
                    # Rough cost estimation (varies by region)
                    if instance['InstanceType'] == 't2.micro':
                        instance_costs += 8.5  # ~$8.5/month
                    elif instance['InstanceType'] == 't2.small':
                        instance_costs += 17
                    elif instance['InstanceType'] == 't3.micro':
                        instance_costs += 7.5
                elif instance['State']['Name'] == 'stopped':
                    stopped_instances += 1
        
        storage_cost = total_size * 0.10  # ~$0.10/GB/month for gp2
        
        print(f"   Running Instances: ~${instance_costs:.2f}/month")
        print(f"   EBS Storage: ~${storage_cost:.2f}/month")
        print(f"   Total Estimate: ~${instance_costs + storage_cost:.2f}/month")
        print("   ⚠️  This is a rough estimate - actual costs may vary")
        
        print(f"\n🎉 Report completed successfully!")
        
    except NoCredentialsError:
        print("❌ AWS credentials not configured")
        print("   Run: aws configure")
    except ClientError as e:
        print(f"❌ AWS API Error: {e}")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    get_detailed_ec2_report()