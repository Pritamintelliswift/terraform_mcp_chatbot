# Module: cloudposse/kops-vault-backend/aws/0.1.3

# registry://modules/cloudposse/kops-vault-backend

**Description:** Terraform module to provision an S3 bucket for HashiCorp Vault secrets storage, and an IAM role and policy with permissions for Kops nodes to access the bucket

**Module Version:** 0.1.3

**Namespace:** cloudposse

**Source:** https://github.com/cloudposse-archives/terraform-aws-kops-vault-backend

### Inputs

| Name | Type | Description | Default | Required |
|---|---|---|---|---|
| namespace | string | Namespace (e.g. `cp` or `cloudposse`) | `` | true |
| stage | string | Stage (e.g. `prod`, `dev`, `staging`) | `` | true |
| name | string | Name (e.g. `vault-backend`) | `"vault-backend"` | false |
| delimiter | string | Delimiter to be used between `namespace`, `stage`, `name` and `attributes` | `"-"` | false |
| attributes | list | Additional attributes (e.g. `1`) | `[]` | false |
| tags | map | Additional tags (e.g. map(`BusinessUnit`,`XYZ`) | `{}` | false |
| cluster_name | string | Kops cluster name (e.g. `us-east-1.cloudposse.com` or `cluster-1.cloudposse.com`) | `` | true |
| nodes_name | string | Kops nodes subdomain name in the cluster DNS zone | `"nodes"` | false |

### Outputs

| Name | Description |
|---|---|
| bucket_domain_name | S3 bucket domain name |
| bucket_arn | S3 bucket ARN |
| policy_name | IAM policy name |
| policy_id | IAM policy ID |
| policy_arn | IAM policy ARN |
| bucket_id | S3 bucket ID |
| role_name | IAM role name |
| role_unique_id | IAM role unique ID |
| role_arn | IAM role ARN |

### Provider Dependencies

| Name | Namespace | Source | Version |
|---|---|---|---|
| aws | hashicorp |  |  |

