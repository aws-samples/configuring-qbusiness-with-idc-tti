# Tutorial: Configuring sample web application with Okta

This tutorial will provide step-by-step instructions to deploy the sample
web application with Okta as external identity provider.

## 1/ Initial setup
1. Create/Register a web application provider in Okta.
    * Register for Okta account, if you do not already have an Okta account. Okta trial account can be used for this tutorial.
    * Sign-in to to Okta and navigate to `Admin` dashboard.
    * Add same sample users to Okta as needed.
    * Ensure the user email address attribute is configured for the user.
    * Follow the steps listed at [Register web application with Okta](./register-webapp-with-okta.md) to register your sample web application with Okta.
    * **Callback URL:** `http://localhost:8080/authorization-code/callback`
    * **Logout URL:** `http://localhost:8080/logout`
    * **Default Okta Issuer URL:** `https://<okta_domain>/oauth2/default`
        * For more info see: [How to find Okta Issuer URI](./find-okta-issuer-url.md)
    * Note `Client ID`, `Client Secret`, `Audience ID`, and `Issuer URL`
        * For most default deployments, `Audience ID` is same as `Client ID`
2. Enable AWS IAM Identity Center instance (Identity Center).
    * Add same sample users (email address) to Identity Center as added to Okta is _Step 1_.
        * Ensure the user email address in Okta matches Identity Center, including case.
    * **_Auto Sync Users:_** Alternatively, follow [Configure SAML and SCIM with Okta and IAM Identity Center](https://docs.aws.amazon.com/singlesignon/latest/userguide/gs-okta.html) to automatically sync users between Okta and Identity Center.
        * Ensure user email attribute is included in the synced attribute list.
    * From the Identity Center settings, note the `IDC Instance ARN`.
3. Create Amazon Q Business integrating with Identity Center instance above and use `File Upload` or `S3` connector to index few sample files for query.
    * Setup user subscription. Ensure the user is same as user created in _step 1_ above.
    * Try the built-in Amazon Q Business web experience and try asking information from indexed documents.
    * From the application details page note the `Application ID`
4. Clone this repo and setup the application environment using poetry.
    * Use your local development desktop. Okta must be able to call the sample web applications `Callback URL` running on `localhost:8080` from public network.
    * You will need AWS CLI, Python and Poetry is installed.
    * [Configure the AWS CLI](https://docs.aws.amazon.com/cli/v1/userguide/cli-chap-configure.html) for your environment and ensure you are able to run AWS CLI commands from command line/terminal.
    * Note the AWS `IAM User/Role ARN` that is used to execute AWS CLI commands above. The sample web application will use the same IAM User/Role.

## 2/ Deploying Trusted token issuer (TTI)
Use `<project_home>/cf/qb-api-idc-config.yaml` to configure TTI. For the template parameters:
* **IDCInstanceArn:** Use the `IDC instance ARN` from _step 2_ in initial setup above.
* **ClientAppExecutionArn:** Use the AWS `IAM User/Role ARN` from _step 4_ in initial setup above.
* **TokenIssuerUrl:** Use the Okta `Issuer URL` from _step 1_ in initial setup above.
* **AuthorizedAudiences:** Use the Okta `Audience ID` from _step 1_ in initial setup above.

Note the `IDC Application ARN` output of the stack creation step.

## 3/ Deploying IAM Roles required by sample web application
Use `<project_home>/cf/qb-api-idc-config.yaml` to configure IAM Roles and Policies required by web application. For the template parameters:
* **QBApplicationID:** Use the Amazon Q Business `Application ID` from _step 3_ in initial setup above.
* **IDCApiAppArn:** Use the `IDC Application ARN` output by Deploying Trusted token issuer (TTI) CFN.
* **ClientAppExecutionArn:** Use the AWS `IAM User/Role ARN` from _step 4_ in initial setup above.
* **KMSKeyId:** This is Optional. Leave the default value if the default AWS managed encryption key is used.

Note the `STS Assume Role` and `App Policy Add-On` output of the stack creation step.

> **_IMPORTANT:_** If your are using a non-admin `IAM User/Role` for executing web application, attach the `App Policy Add-On` to the `IAM User/Role` to enable access to `CreateTokenWithIAM` and `AssumeRole` API for your `IAM User/Role`.

## 4/ Configuring Web Application Environment
Make a copy of `<project_home>/webapp/config/.env.okta.dist` file and rename it to `<project_home>/webapp/config/.env`. Update the environment variables as described below.

#### OAuth client configuration
* **issuer_url:** Use the Okta `Issuer URL` from _step 1_ in initial setup above.
* **client_id:** Use the Okta `Client ID` from _step 1_ in initial setup above.
* **client_secret:** Use the Okta `Client Secret` from _step 1_ in initial setup above.

#### Application configuration
* **idc_provider_apl_arn:** Use the `IDC Application ARN` output by CFN for Deploying Trusted token issuer (TTI).
* **qb_sts_role:** Use the `STS Assume Role` output by CFN for Deploying IAM Roles required by sample web application CFN.
* **qb_apl_id:** Use the Amazon Q Business `Application ID` from _step 3_ in initial setup above.
* **app_domain:**  Use `localhost:8080`.
* **region_name:** Use the AWS Region where your Q Business application and Identity Center is deployed. Example, `us-east-1` or `us-west-2`.

## 5/ Launching sample web application
* From your command line interface change folder to `<project_home>`
* Install project libraries using Poetry. See `Repository Setup` section in [Project README](../../../README.md) for more information.
* Ensure your AWS CLI access is configured with `IAM User/Role` from _step 4_ in initial setup above.
* Ensure AWS CLI is working properly by executing any CLI command. Example, `aws qbusiness list-applications`.
* Launch web application using command: `poetry run python webapp/main.py`
* Open web browser in `InCognito` or `InPrivate` mode and navigate to http://localhost:8080/
* Click on `Login` button to start the sign-in process with Okta.

If successful, you should be able to see a list of active conversations for the signed-in user.

> Review the debug messages in the command line for OIDC/Identity Center JWT tokens and any error messages to trouble shoot issues.

## 6/ Cleanup
To avoid incurring additional charges, make sure you delete any resources and services created for this tutorial.
* Delete the CFN stack for Deploying IAM Roles required by sample web application
* Delete the CFN stack for Deploying Trusted token issuer (TTI)
* Delete Amazon Q Business Application
* Delete Identity Center instance
* Delete web application from Okta
* Delete samples users created in Okta.
* Delete/disable Okta account.
