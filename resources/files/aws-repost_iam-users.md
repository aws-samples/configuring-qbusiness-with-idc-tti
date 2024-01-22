# How do I use IAM to allow user access to resources?
I want to use AWS Identity and Access Management (IAM) to allow users or groups access to my AWS resources.

## Resolution
Create [IAM identities (users, groups, roles)](https://docs.aws.amazon.com/IAM/latest/UserGuide/id.html), and assign custom permissions sets (IAM policies) to the identities. IAM policies grant each user access to only the services, resources, and information that they need to perform tasks. You can also assign each user unique security credentials, access keys, and [multi-factor authentication (MFA)](https://aws.amazon.com/iam/details/mfa/) devices.

**_Note:_** It's a best practice to [apply least-privilege permissions](http://docs.aws.amazon.com/IAM/latest/UserGuide/id_roles_providers.html) for only the required permissions to perform a task.

You can also integrate IAM policies and permissions with directories that you already manage, such as an OpenID Connect provider. For more information, see [Identity providers and federation](http://docs.aws.amazon.com/IAM/latest/UserGuide/id_roles_providers.html).

You can interact with IAM through the web-based IAM console, the AWS Command Line Interface (AWS CLI), or the AWS API or SDKs. For more information, see [Getting started with IAM](https://docs.aws.amazon.com/IAM/latest/UserGuide/getting-started.html).

For a list of AWS services that support IAM, see [AWS services that work with IAM](http://docs.aws.amazon.com/IAM/latest/UserGuide/reference_aws-services-that-work-with-iam.html)
