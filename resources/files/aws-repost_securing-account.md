# What are some best practices for securing my AWS account and its resources?

I want to protect my AWS resources or account from unauthorized activity. I want some best practices for securing my AWS account and its resources

## Short description
AWS offers many tools to help secure your account. However, because many of these measures aren't active by default, you must take direct action to implement them. Here are some best practices to consider when securing your account and its resources:
* Safeguard your passwords and access keys
* [Activate multi-factor authentication (MFA) on the AWS account root user](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_root-user.html#id_root-user_manage_mfa) and any users with interactive access to AWS Identity and Access Management (IAM)
* Limit AWS account root user access to your resources
* Audit IAM users and their policies frequently
* Create Amazon Elastic Block Store (Amazon EBS) snapshots, Amazon Relational Database Service (Amazon RDS) snapshots, and Amazon Simple Storage Service (Amazon S3) object versions
* Use AWS Git projects to scan for evidence of unauthorized use
* Monitor your account and its resources

**_Note:_** If you're using AWS Identity Center or IAM federated users, the best practices for IAM users also apply to federated users.

## Resolution
### Safeguard your passwords and access keys
The two main types of credentials used for accessing your account are passwords and access keys. Passwords and access keys can be applied to the AWS root user account and individual IAM users. It's a best practice to safeguard passwords and access keys as securely as you would any other confidential personal data. Never embed them in publicly accessible code (for example, a public Git repository). For added security, frequently rotate and update all security credentials.

If you suspect that a password or access key pair was exposed, follow these steps:
1. [Rotate all access key pairs](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_credentials_access-keys.html#Using_RotateAccessKey).
2. [Change your AWS account root user password](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_credentials_passwords_change-root.html).
3. Follow the instructions in [What do I do if I notice unauthorized activity in my AWS account?](https://repost.aws/knowledge-center/potential-account-compromise)

### Activate MFA
Activating MFA can help secure the accounts and prevent unauthorized users from logging in to accounts without a security token.

For increased security, it's a best practice to configure MFA to help protect your AWS resources. You can [activate a virtual MFA for IAM users and the AWS account root user](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_credentials_mfa_enable_virtual.html#enable-virt-mfa-for-iam-user). Activating MFA for the root user affects only the root user credentials. IAM users in the account are distinct identities with their own credentials, and each identity has its own MFA configuration.

For more information, see [Activating MFA devices for users in AWS](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_credentials_mfa_enable.html).

### Limit root user access to your resources
Root user account credentials (the root password or root access keys) grant unlimited access to your account and its resources. It's a best practice to both secure and minimize root user access to your account.

Consider the following strategies to limit root user access to your account:
* Use IAM users for day-to-day access to your account. If you're the only person accessing the account, see Create an administrative user.
* Eliminate the use of root access keys. For more information see Best practices for managing AWS access keys.
* Use an MFA device for the root user of your account.

For more information, see Safeguard your root user credentials and don't use them for everyday tasks.

### Audit IAM users and their policies frequently
Consider the following best practices when working with IAM users:
* Be sure that the IAM users have the most restrictive policies possible, with only enough permissions to allow them to complete their intended tasks (least privilege).
* Use AWS IAM Access Analyzer to analyze your existing permissions. For more information, see IAM Access Analyzer makes it easier to implement least privilege permissions by generating IAM policies based on access activity.
* Create different IAM users for each set of tasks.
* When associating multiple policies with the same IAM user, keep in mind that the least restrictive policy takes precedence.
* Frequently audit your IAM users and their permissions, and find unused credentials.
* If your IAM user needs access to the console, you can set up a password to allow console access while limiting the user's permissions.
* Set up individual MFA devices for each IAM user who has access to the console.

You can use the visual editor in the IAM console to help you define secure policies. For examples of common business use cases and the policies you might use to address them, see Business use cases for IAM.

### Create Amazon EBS snapshots, Amazon RDS snapshots, and Amazon S3 object versions
To create a point-in-time snapshot of an EBS volume, see Create Amazon EBS snapshots.

To activate Amazon RDS automated snapshots and set the backup retention period, see Activating automated backups.

To create a standard S3 bucket for backup and archive, see Creating standard S3 buckets for backup and archive. To create S3 bucket versioning, see Using versioning in S3 buckets.

To create an AWS Backup plan using the console, see Create a scheduled backup. To create an AWS Backup plan using AWS Command Line Interface (AWS CLI), see [How can I use the AWS CLI to create an AWS Backup plan or run an on-demand job?](https://repost.aws/knowledge-center/aws-backup-cli-create-plan-run-job)

### Use AWS Git projects to protect against unauthorized use
AWS offers Git projects that you can install to help protect your account:
* Git Secrets can scan merges, commits, and commit messages for secret information (access keys). If Git Secrets detects prohibited regular expressions, it can reject those commits from being posted to public repositories.
* Use AWS Step Functions and AWS Lambda to generate Amazon CloudWatch Events from AWS Health or by AWS Trusted Advisor. If there's evidence that your access keys are exposed, the projects can help you to automatically detect, log, and mitigate the event.

### Monitor your account and its resources
It's a best practice to actively monitor your account and its resources to detect any unusual activity or access to your account. Consider
one or more of the following solutions:
* Create a billing alarm to monitor your estimated AWS charges to receive automated notifications when your bill exceeds thresholds you define. For more information, see Amazon CloudWatch FAQs.
* Create a trail for your AWS account to track what credentials are used to initiate particular API calls and when they're used. Doing so can help you to determine if the usage was accidental or unauthorized. You can then take the appropriate steps to mitigate the situation. For more information, see Security best practices in AWS CloudTrail.
* Use CloudTrail and CloudWatch in conjunction to monitor access key usage and receive alerts for unusual API calls.
* Activate resource-level logging (for example, at the instance or OS level) and Amazon S3 default bucket encryption.
* Activate Amazon GuardDuty for your AWS account in all supported Regions. After it's turned on, GuardDuty starts to analyze independent streams of data from AWS CloudTrail management and Amazon S3 data events, Amazon VPC Flow Logs, and DNS logs to generate security findings. The primary detection categories include account compromise, instance compromise, and malicious intrusions. For more information, see Amazon GuardDuty FAQs.

**_Note:_** It's a best practice to turn on logging for all Regions, not just the ones that you regularly use.