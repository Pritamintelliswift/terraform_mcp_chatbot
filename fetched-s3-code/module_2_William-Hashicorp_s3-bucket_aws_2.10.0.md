# Module: William-Hashicorp/s3-bucket/aws/2.10.0

# registry://modules/William-Hashicorp/s3-bucket

**Description:** Terraform module which creates S3 bucket resources on AWS

**Module Version:** 2.10.0

**Namespace:** William-Hashicorp

**Source:** https://github.com/William-Hashicorp/terraform-aws-s3-bucket

### Inputs

| Name | Type | Description | Default | Required |
|---|---|---|---|---|
| attach_elb_log_delivery_policy | bool | Controls if S3 bucket should have ELB log delivery policy attached | `false` | false |
| acl | string | (Optional) The canned ACL to apply. Defaults to 'private'. Conflicts with `grant` | `"private"` | false |
| cors_rule | any | List of maps containing rules for Cross-Origin Resource Sharing. | `[]` | false |
| attach_lb_log_delivery_policy | bool | Controls if S3 bucket should have ALB/NLB log delivery policy attached | `false` | false |
| attach_policy | bool | Controls if S3 bucket should have bucket policy attached (set to `true` to use value of `policy` as bucket policy) | `false` | false |
| request_payer | string | (Optional) Specifies who should bear the cost of Amazon S3 data transfer. Can be either BucketOwner or Requester. By default, the owner of the S3 bucket would incur the costs of any data transfer. See Requester Pays Buckets developer guide for more information. | `` | true |
| server_side_encryption_configuration | any | Map containing server-side encryption configuration. | `{}` | false |
| restrict_public_buckets | bool | Whether Amazon S3 should restrict public bucket policies for this bucket. | `false` | false |
| object_ownership | string | Object ownership. Valid values: BucketOwnerPreferred or ObjectWriter. 'BucketOwnerPreferred': Objects uploaded to the bucket change ownership to the bucket owner if the objects are uploaded with the bucket-owner-full-control canned ACL. 'ObjectWriter': The uploading account will own the object if the object is uploaded with the bucket-owner-full-control canned ACL. | `"ObjectWriter"` | false |
| attach_deny_insecure_transport_policy | bool | Controls if S3 bucket should have deny non-SSL transport policy attached | `false` | false |
| lifecycle_rule | any | List of maps containing configuration of object lifecycle management. | `[]` | false |
| block_public_policy | bool | Whether Amazon S3 should block public bucket policies for this bucket. | `false` | false |
| tags | map(string) | (Optional) A mapping of tags to assign to the bucket. | `{}` | false |
| website | map(string) | Map containing static web-site hosting or redirect configuration. | `{}` | false |
| logging | map(string) | Map containing access bucket logging configuration. | `{}` | false |
| grant | any | An ACL policy grant. Conflicts with `acl` | `[]` | false |
| replication_configuration | any | Map containing cross-region replication configuration. | `{}` | false |
| object_lock_configuration | any | Map containing S3 object locking configuration. | `{}` | false |
| create_bucket | bool | Controls if S3 bucket should be created | `true` | false |
| policy | string | (Optional) A valid bucket policy JSON document. Note that if the policy document is not specific enough (but still valid), Terraform may view the policy as constantly changing in a terraform plan. In this case, please make sure you use the verbose/specific version of the policy. For more information about building AWS IAM policy documents with Terraform, see the AWS IAM Policy Document Guide. | `` | true |
| block_public_acls | bool | Whether Amazon S3 should block public ACLs for this bucket. | `false` | false |
| control_object_ownership | bool | Whether to manage S3 Bucket Ownership Controls on this bucket. | `false` | false |
| attach_public_policy | bool | Controls if a user defined public bucket policy will be attached (set to `false` to allow upstream to apply defaults to the bucket) | `true` | false |
| bucket | string | (Optional, Forces new resource) The name of the bucket. If omitted, Terraform will assign a random, unique name. | `` | true |
| bucket_prefix | string | (Optional, Forces new resource) Creates a unique bucket name beginning with the specified prefix. Conflicts with bucket. | `` | true |
| force_destroy | bool | (Optional, Default:false ) A boolean that indicates all objects should be deleted from the bucket so that the bucket can be destroyed without error. These objects are not recoverable. | `false` | false |
| acceleration_status | string | (Optional) Sets the accelerate configuration of an existing bucket. Can be Enabled or Suspended. | `` | true |
| versioning | map(string) | Map containing versioning configuration. | `{}` | false |
| ignore_public_acls | bool | Whether Amazon S3 should ignore public ACLs for this bucket. | `false` | false |

### Outputs

| Name | Description |
|---|---|
| s3_bucket_id | The name of the bucket. |
| s3_bucket_arn | The ARN of the bucket. Will be of format arn:aws:s3:::bucketname. |
| s3_bucket_bucket_domain_name | The bucket domain name. Will be of format bucketname.s3.amazonaws.com. |
| s3_bucket_bucket_regional_domain_name | The bucket region-specific domain name. The bucket domain name including the region name, please refer here for format. Note: The AWS CloudFront allows specifying S3 region-specific endpoint when creating S3 origin, it will prevent redirect issues from CloudFront to S3 Origin URL. |
| s3_bucket_hosted_zone_id | The Route 53 Hosted Zone ID for this bucket's region. |
| s3_bucket_region | The AWS region this bucket resides in. |
| s3_bucket_website_endpoint | The website endpoint, if the bucket is configured with a website. If not, this will be an empty string. |
| s3_bucket_website_domain | The domain of the website endpoint, if the bucket is configured with a website. If not, this will be an empty string. This is used to create Route 53 alias records.  |

### Provider Dependencies

| Name | Namespace | Source | Version |
|---|---|---|---|
| aws | hashicorp |  | >= 3.50 |

### Examples

#### complete

**Readme:**

# Complete S3 bucket with most of supported features enabled

Configuration in this directory creates S3 bucket which demos such capabilities:
- static web-site hosting
- access logging (for S3, ELB and ALB/NLB)
- versioning
- CORS
- lifecycle rules
- server-side encryption
- object locking
- grants (required for CloudFront logs)

Please check [S3 replication example](https://github.com/terraform-aws-modules/terraform-aws-s3-bucket/tree/master/examples/s3-replication) to see Cross-Region Replication (CRR) supported by this module.

## Usage

To run this example you need to execute:

```bash
$ terraform init
$ terraform plan
$ terraform apply
```

Note that this example may create resources which cost money. Run `terraform destroy` when you don't need these resources.

<!-- BEGINNING OF PRE-COMMIT-TERRAFORM DOCS HOOK -->
## Requirements

| Name | Version |
|------|---------|
| <a name="requirement_terraform"></a> [terraform](#requirement\_terraform) | >= 0.13.1 |
| <a name="requirement_aws"></a> [aws](#requirement\_aws) | >= 3.60 |
| <a name="requirement_random"></a> [random](#requirement\_random) | >= 2.0 |

## Providers

| Name | Version |
|------|---------|
| <a name="provider_aws"></a> [aws](#provider\_aws) | >= 3.60 |
| <a name="provider_random"></a> [random](#provider\_random) | >= 2.0 |

## Modules

| Name | Source | Version |
|------|--------|---------|
| <a name="module_cloudfront_log_bucket"></a> [cloudfront\_log\_bucket](#module\_cloudfront\_log\_bucket) | ../../ |  |
| <a name="module_log_bucket"></a> [log\_bucket](#module\_log\_bucket) | ../../ |  |
| <a name="module_s3_bucket"></a> [s3\_bucket](#module\_s3\_bucket) | ../../ |  |

## Resources

| Name | Type |
|------|------|
| [aws_iam_role.this](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/iam_role) | resource |
| [aws_kms_key.objects](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/kms_key) | resource |
| [random_pet.this](https://registry.terraform.io/providers/hashicorp/random/latest/docs/resources/pet) | resource |
| [aws_canonical_user_id.current](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/data-sources/canonical_user_id) | data source |
| [aws_cloudfront_log_delivery_canonical_user_id.cloudfront](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/data-sources/cloudfront_log_delivery_canonical_user_id) | data source |
| [aws_iam_policy_document.bucket_policy](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/data-sources/iam_policy_document) | data source |

## Inputs

No inputs.

## Outputs

| Name | Description |
|------|-------------|
| <a name="output_s3_bucket_arn"></a> [s3\_bucket\_arn](#output\_s3\_bucket\_arn) | The ARN of the bucket. Will be of format arn:aws:s3:::bucketname. |
| <a name="output_s3_bucket_bucket_domain_name"></a> [s3\_bucket\_bucket\_domain\_name](#output\_s3\_bucket\_bucket\_domain\_name) | The bucket domain name. Will be of format bucketname.s3.amazonaws.com. |
| <a name="output_s3_bucket_bucket_regional_domain_name"></a> [s3\_bucket\_bucket\_regional\_domain\_name](#output\_s3\_bucket\_bucket\_regional\_domain\_name) | The bucket region-specific domain name. The bucket domain name including the region name, please refer here for format. Note: The AWS CloudFront allows specifying S3 region-specific endpoint when creating S3 origin, it will prevent redirect issues from CloudFront to S3 Origin URL. |
| <a name="output_s3_bucket_hosted_zone_id"></a> [s3\_bucket\_hosted\_zone\_id](#output\_s3\_bucket\_hosted\_zone\_id) | The Route 53 Hosted Zone ID for this bucket's region. |
| <a name="output_s3_bucket_id"></a> [s3\_bucket\_id](#output\_s3\_bucket\_id) | The name of the bucket. |
| <a name="output_s3_bucket_region"></a> [s3\_bucket\_region](#output\_s3\_bucket\_region) | The AWS region this bucket resides in. |
| <a name="output_s3_bucket_website_domain"></a> [s3\_bucket\_website\_domain](#output\_s3\_bucket\_website\_domain) | The domain of the website endpoint, if the bucket is configured with a website. If not, this will be an empty string. This is used to create Route 53 alias records. |
| <a name="output_s3_bucket_website_endpoint"></a> [s3\_bucket\_website\_endpoint](#output\_s3\_bucket\_website\_endpoint) | The website endpoint, if the bucket is configured with a website. If not, this will be an empty string. |
<!-- END OF PRE-COMMIT-TERRAFORM DOCS HOOK -->


#### s3-replication

**Readme:**

# S3 bucket with Cross-Region Replication (CRR) enabled

Configuration in this directory creates S3 bucket in one region and configures CRR to another bucket in another region.

Please check [complete example](https://github.com/terraform-aws-modules/terraform-aws-s3-bucket/tree/master/examples/complete) to see all other features supported by this module.

## Usage

To run this example you need to execute:

```bash
$ terraform init
$ terraform plan
$ terraform apply
```

Note that this example may create resources which cost money. Run `terraform destroy` when you don't need these resources.

<!-- BEGINNING OF PRE-COMMIT-TERRAFORM DOCS HOOK -->
## Requirements

| Name | Version |
|------|---------|
| <a name="requirement_terraform"></a> [terraform](#requirement\_terraform) | >= 0.13.1 |
| <a name="requirement_aws"></a> [aws](#requirement\_aws) | >= 3.50 |
| <a name="requirement_random"></a> [random](#requirement\_random) | >= 2.0 |

## Providers

| Name | Version |
|------|---------|
| <a name="provider_aws"></a> [aws](#provider\_aws) | >= 3.50 |
| <a name="provider_aws.replica"></a> [aws.replica](#provider\_aws.replica) | >= 3.50 |
| <a name="provider_random"></a> [random](#provider\_random) | >= 2.0 |

## Modules

| Name | Source | Version |
|------|--------|---------|
| <a name="module_replica_bucket"></a> [replica\_bucket](#module\_replica\_bucket) | ../../ |  |
| <a name="module_s3_bucket"></a> [s3\_bucket](#module\_s3\_bucket) | ../../ |  |

## Resources

| Name | Type |
|------|------|
| [aws_iam_policy.replication](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/iam_policy) | resource |
| [aws_iam_policy_attachment.replication](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/iam_policy_attachment) | resource |
| [aws_iam_role.replication](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/iam_role) | resource |
| [aws_kms_key.replica](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/kms_key) | resource |
| [random_pet.this](https://registry.terraform.io/providers/hashicorp/random/latest/docs/resources/pet) | resource |
| [aws_caller_identity.current](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/data-sources/caller_identity) | data source |

## Inputs

No inputs.

## Outputs

| Name | Description |
|------|-------------|
| <a name="output_s3_bucket_arn"></a> [s3\_bucket\_arn](#output\_s3\_bucket\_arn) | The ARN of the bucket. Will be of format arn:aws:s3:::bucketname. |
| <a name="output_s3_bucket_bucket_domain_name"></a> [s3\_bucket\_bucket\_domain\_name](#output\_s3\_bucket\_bucket\_domain\_name) | The bucket domain name. Will be of format bucketname.s3.amazonaws.com. |
| <a name="output_s3_bucket_bucket_regional_domain_name"></a> [s3\_bucket\_bucket\_regional\_domain\_name](#output\_s3\_bucket\_bucket\_regional\_domain\_name) | The bucket region-specific domain name. The bucket domain name including the region name, please refer here for format. Note: The AWS CloudFront allows specifying S3 region-specific endpoint when creating S3 origin, it will prevent redirect issues from CloudFront to S3 Origin URL. |
| <a name="output_s3_bucket_hosted_zone_id"></a> [s3\_bucket\_hosted\_zone\_id](#output\_s3\_bucket\_hosted\_zone\_id) | The Route 53 Hosted Zone ID for this bucket's region. |
| <a name="output_s3_bucket_id"></a> [s3\_bucket\_id](#output\_s3\_bucket\_id) | The name of the bucket. |
| <a name="output_s3_bucket_region"></a> [s3\_bucket\_region](#output\_s3\_bucket\_region) | The AWS region this bucket resides in. |
| <a name="output_s3_bucket_website_domain"></a> [s3\_bucket\_website\_domain](#output\_s3\_bucket\_website\_domain) | The domain of the website endpoint, if the bucket is configured with a website. If not, this will be an empty string. This is used to create Route 53 alias records. |
| <a name="output_s3_bucket_website_endpoint"></a> [s3\_bucket\_website\_endpoint](#output\_s3\_bucket\_website\_endpoint) | The website endpoint, if the bucket is configured with a website. If not, this will be an empty string. |
<!-- END OF PRE-COMMIT-TERRAFORM DOCS HOOK -->


#### notification

**Readme:**

# S3 bucket notifications to Lambda functions, SQS queues, and SNS topics

Configuration in this directory creates S3 bucket notifications to all supported destinations.

## Usage

To run this example you need to execute:

```bash
$ terraform init
$ terraform plan
$ terraform apply
```

Note that this example may create resources which cost money. Run `terraform destroy` when you don't need these resources.

<!-- BEGINNING OF PRE-COMMIT-TERRAFORM DOCS HOOK -->
## Requirements

| Name | Version |
|------|---------|
| <a name="requirement_terraform"></a> [terraform](#requirement\_terraform) | >= 0.13.1 |
| <a name="requirement_aws"></a> [aws](#requirement\_aws) | >= 3.50 |
| <a name="requirement_null"></a> [null](#requirement\_null) | >= 2.0 |
| <a name="requirement_random"></a> [random](#requirement\_random) | >= 2.0 |

## Providers

| Name | Version |
|------|---------|
| <a name="provider_aws"></a> [aws](#provider\_aws) | >= 3.50 |
| <a name="provider_null"></a> [null](#provider\_null) | >= 2.0 |
| <a name="provider_random"></a> [random](#provider\_random) | >= 2.0 |

## Modules

| Name | Source | Version |
|------|--------|---------|
| <a name="module_all_notifications"></a> [all\_notifications](#module\_all\_notifications) | ../../modules/notification |  |
| <a name="module_lambda_function1"></a> [lambda\_function1](#module\_lambda\_function1) | terraform-aws-modules/lambda/aws | ~> 2.0 |
| <a name="module_lambda_function2"></a> [lambda\_function2](#module\_lambda\_function2) | terraform-aws-modules/lambda/aws | ~> 2.0 |
| <a name="module_s3_bucket"></a> [s3\_bucket](#module\_s3\_bucket) | ../../ |  |
| <a name="module_sns_topic1"></a> [sns\_topic1](#module\_sns\_topic1) | terraform-aws-modules/sns/aws | ~> 3.0 |
| <a name="module_sns_topic2"></a> [sns\_topic2](#module\_sns\_topic2) | terraform-aws-modules/sns/aws | ~> 3.0 |

## Resources

| Name | Type |
|------|------|
| [aws_sqs_queue.this](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/sqs_queue) | resource |
| [aws_sqs_queue_policy.allow_external](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/sqs_queue_policy) | resource |
| [null_resource.download_package](https://registry.terraform.io/providers/hashicorp/null/latest/docs/resources/resource) | resource |
| [random_pet.this](https://registry.terraform.io/providers/hashicorp/random/latest/docs/resources/pet) | resource |
| [aws_iam_policy_document.sqs_external](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/data-sources/iam_policy_document) | data source |

## Inputs

No inputs.

## Outputs

| Name | Description |
|------|-------------|
| <a name="output_s3_bucket_arn"></a> [s3\_bucket\_arn](#output\_s3\_bucket\_arn) | The ARN of the bucket. Will be of format arn:aws:s3:::bucketname. |
| <a name="output_s3_bucket_bucket_domain_name"></a> [s3\_bucket\_bucket\_domain\_name](#output\_s3\_bucket\_bucket\_domain\_name) | The bucket domain name. Will be of format bucketname.s3.amazonaws.com. |
| <a name="output_s3_bucket_bucket_regional_domain_name"></a> [s3\_bucket\_bucket\_regional\_domain\_name](#output\_s3\_bucket\_bucket\_regional\_domain\_name) | The bucket region-specific domain name. The bucket domain name including the region name, please refer here for format. Note: The AWS CloudFront allows specifying S3 region-specific endpoint when creating S3 origin, it will prevent redirect issues from CloudFront to S3 Origin URL. |
| <a name="output_s3_bucket_hosted_zone_id"></a> [s3\_bucket\_hosted\_zone\_id](#output\_s3\_bucket\_hosted\_zone\_id) | The Route 53 Hosted Zone ID for this bucket's region. |
| <a name="output_s3_bucket_id"></a> [s3\_bucket\_id](#output\_s3\_bucket\_id) | The name of the bucket. |
| <a name="output_s3_bucket_region"></a> [s3\_bucket\_region](#output\_s3\_bucket\_region) | The AWS region this bucket resides in. |
| <a name="output_s3_bucket_website_domain"></a> [s3\_bucket\_website\_domain](#output\_s3\_bucket\_website\_domain) | The domain of the website endpoint, if the bucket is configured with a website. If not, this will be an empty string. This is used to create Route 53 alias records. |
| <a name="output_s3_bucket_website_endpoint"></a> [s3\_bucket\_website\_endpoint](#output\_s3\_bucket\_website\_endpoint) | The website endpoint, if the bucket is configured with a website. If not, this will be an empty string. |
<!-- END OF PRE-COMMIT-TERRAFORM DOCS HOOK -->


#### object

**Readme:**

# S3 bucket object

Configuration in this directory creates S3 bucket objects with different configurations.

## Usage

To run this example you need to execute:

```bash
$ terraform init
$ terraform plan
$ terraform apply
```

Note that this example may create resources which cost money. Run `terraform destroy` when you don't need these resources.

<!-- BEGINNING OF PRE-COMMIT-TERRAFORM DOCS HOOK -->
## Requirements

| Name | Version |
|------|---------|
| <a name="requirement_terraform"></a> [terraform](#requirement\_terraform) | >= 0.13.1 |
| <a name="requirement_aws"></a> [aws](#requirement\_aws) | >= 3.50 |
| <a name="requirement_random"></a> [random](#requirement\_random) | >= 2.0 |

## Providers

| Name | Version |
|------|---------|
| <a name="provider_aws"></a> [aws](#provider\_aws) | >= 3.50 |
| <a name="provider_random"></a> [random](#provider\_random) | >= 2.0 |

## Modules

| Name | Source | Version |
|------|--------|---------|
| <a name="module_object"></a> [object](#module\_object) | ../../modules/object |  |
| <a name="module_object_complete"></a> [object\_complete](#module\_object\_complete) | ../../modules/object |  |
| <a name="module_object_locked"></a> [object\_locked](#module\_object\_locked) | ../../modules/object |  |
| <a name="module_s3_bucket"></a> [s3\_bucket](#module\_s3\_bucket) | ../../ |  |
| <a name="module_s3_bucket_with_object_lock"></a> [s3\_bucket\_with\_object\_lock](#module\_s3\_bucket\_with\_object\_lock) | ../../ |  |

## Resources

| Name | Type |
|------|------|
| [aws_kms_key.this](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/kms_key) | resource |
| [random_pet.this](https://registry.terraform.io/providers/hashicorp/random/latest/docs/resources/pet) | resource |

## Inputs

No inputs.

## Outputs

| Name | Description |
|------|-------------|
| <a name="output_s3_bucket_arn"></a> [s3\_bucket\_arn](#output\_s3\_bucket\_arn) | The ARN of the bucket. Will be of format arn:aws:s3:::bucketname. |
| <a name="output_s3_bucket_id"></a> [s3\_bucket\_id](#output\_s3\_bucket\_id) | The name of the bucket. |
| <a name="output_s3_bucket_object_etag"></a> [s3\_bucket\_object\_etag](#output\_s3\_bucket\_object\_etag) | The ETag generated for the object (an MD5 sum of the object content). |
| <a name="output_s3_bucket_object_id"></a> [s3\_bucket\_object\_id](#output\_s3\_bucket\_object\_id) | The key of S3 object |
| <a name="output_s3_bucket_object_version_id"></a> [s3\_bucket\_object\_version\_id](#output\_s3\_bucket\_object\_version\_id) | A unique version ID value for the object, if bucket versioning is enabled. |
<!-- END OF PRE-COMMIT-TERRAFORM DOCS HOOK -->



