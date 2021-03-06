# Media Services Application Mapper (MSAM)

MSAM is installed into an AWS account using several CloudFormation templates.

## Requirements for MSAM

* Amazon Web Services account
* Signed-in to the AWS console as an IAM user with AdministratorAccess role, or [sufficient permissions](#installation-permissions) to install the tool
* Google Chrome, Mozilla Firefox, Safari or another current browser with JavaScript enabled


## Important Notes

**CloudFront:** MSAM v1.5.0 and up installs a CloudFront distribution with the web application while the S3 bucket that hosts the content remains private. The first time installing the web application may take as long as **15-25 minutes** for the CloudFront distribution to complete the deployment process.

**DNS Temporary Redirect:** You may receive DNS redirects from CloudFront **if you install into a region other an us-east-1.** This is normal and may take from several minutes to an hour for DNS changes to propagate throughout the network. You may see the following message in your browser, which is normal while DNS changes settle. You will not need to take any other action aside from waiting. Read [this](https://docs.aws.amazon.com/AmazonS3/latest/dev/Redirects.html#TemporaryRedirection) at AWS for more information about this case.

![Image of IAM Ackowlegement](images/cloudfront-dns-error.png)

## Finding Installation Content

### dist/ folder in GitHub

This folder in the repository contains files you can use to install MSAM into your AWS account. 

The CloudFormation templates located in this folder that end with `-release.json` are ready to use to install the latest release of MSAM.

```
msam-all-resources-release.json
msam-browser-app-release.json
msam-core-release.json
msam-dynamodb-release.json
msam-events-release.json
msam-iam-roles-release.json
```

### md5.txt, sha1.txt, sha256.txt

These files contain digest values for the templates and packaged code contained in this folder and hosted on S3 by the project sponsors.

### release.txt

The hosted templates listed in this file always point to the latest release of MSAM. These links can be used directly in the CloudFormation console to install MSAM into any supported AWS region. Templates in this file have an epoch timestamp embedded in the template description. You will see the timestamp after the template is loaded by CloudFormation. These template URLs should never change name.

```
https://rodeolabz-us-west-2.s3.amazonaws.com/msam/msam-all-resources-release.json
https://rodeolabz-us-west-2.s3.amazonaws.com/msam/msam-browser-app-release.json
https://rodeolabz-us-west-2.s3.amazonaws.com/msam/msam-core-release.json
https://rodeolabz-us-west-2.s3.amazonaws.com/msam/msam-dynamodb-release.json
https://rodeolabz-us-west-2.s3.amazonaws.com/msam/msam-events-release.json
https://rodeolabz-us-west-2.s3.amazonaws.com/msam/msam-iam-roles-release.json
```

### current.txt

The templates listed in this file point to a build of MSAM under development or test. Templates in this file have an epoch timestamp in the file name and embedded in the template description. The template URLs below are example only. This file is regenerated by MSAM's deployment scripts when testing a new build.

```
https://rodeolabz-us-west-2.s3.amazonaws.com/msam/msam-all-resources-release-1587154970.template
https://rodeolabz-us-west-2.s3.amazonaws.com/msam/msam-browser-app-release-1587154970.template
https://rodeolabz-us-west-2.s3.amazonaws.com/msam/msam-core-release-1587154970.template
https://rodeolabz-us-west-2.s3.amazonaws.com/msam/msam-dynamodb-release-1587154970.template
https://rodeolabz-us-west-2.s3.amazonaws.com/msam/msam-events-release-1587154970.template
https://rodeolabz-us-west-2.s3.amazonaws.com/msam/msam-iam-roles-release-1587154970.template
```

## CloudFormation Stack Creation

* Login to CloudFormation using the same account used for creating and managing the Media Services
* Click on Create Stack

During the installation of the CloudFormation stacks you may be prompted to acknowledge creation of IAM resources, as seen in the sample screenshot below. Click the check-box next to each entry. Finally, click the "Create Change Set" button where applicable, then press the Execute button.
 
![Image of IAM Ackowlegement](images/ack-iam-resources.png)

When you are installing a CloudFormation template listed below, from Choose a Template select "Specify an Amazon S3 template URL" and paste in the URL below exactly as provided for any MSAM-supported region. Do not change the region name in the URL path or bucket name.

### Master Template: All Resources

As of release v1.5.0, the CloudFormation templates distributed for MSAM include a master template that installs the complete solution into a single region. The master template nests and deploys the existing five templates automatically.

If you need to upgrade your installation from the individual templates to the master template, see this note below about migrating your DynamoDB tables.

`https://rodeolabz-us-west-2.s3.amazonaws.com/msam/msam-all-resources-release.json`

#### Input Parameters

1. Provide a stack name
2. Provide an alternate bucket base name (leave at `rodeolabz` unless you are installing custom builds)
2. Specify the time-to-live in seconds for all cached data, alarms, and events; see the examples next to the input for common values

#### Outputs

Go to the Outputs section of the stack, and copy and save the URL value for EndpointURL and MSAMBrowserURL. Open the link for the APIKeyID, click the Show link in the main compartment for the API key, copy the API Key and save it with the other two URL values.

![Master Template Outputs](images/master-template-outputs.png)

After the template installation finishes and you've recorded the outputs from the template, skip forward to [Template 4: CloudWatch Event Handler](INSTALL.md#template-4-cloudwatch-event-handler) if you need to collect events and monitor alarms across multiple regions, and then to [Multiple Users and Access Control](INSTALL.md#multiple-users-and-access-control) and complete the final steps in this guide.

### Individual Templates

You still have the option to install CloudFormation templates separately. This may be an option for you if you are performing a customized installation that requires special handling between stacks, or if you have distributed responsibilities within your organization for managing your AWS accounts.

The order in which to create the stacks are as follows:

1. Create the IAM stack
2. Create the DynamoDB stack
1. Create the Core stack
1. Create the Event Handler stack
1. Create the MSAM Web stack 

Install the IAM, DynamoDB, Core and Web stacks in your main, or most accessed region only. The IAM resources installed by CloudFormation are global, although the stack you use to install them should be run in the same region as the DynamoDB, Core and other stacks. **The Event Handler stack is installed in each region Media Services are configured.**

### Template 1: IAM Resources

This template will create a stack for the IAM roles needed by MSAM and a group needed by operators for installing the stacks. 

`https://rodeolabz-us-west-2.s3.amazonaws.com/msam/msam-iam-roles-release.json`

#### Input Parameters

1. Provide a stack name

#### Outputs

Go to the Outputs section of the stack and copy the four role ARNs to a notepad. You will need these as input parameters for the next templates. Also, notice the link named `InstallationGroupLink`. This link will take you to IAM to review the group created for granting installation permissions to IAM users. See the following image.

![IAM Template Outputs](images/iam-template-outputs.png)


### Template 2: DynamoDB Tables

This template will create a stack for the tables, indices, and on demand capacity settings. The first time a stack is created from this template, defaults are added to scan and display cloud resources in the current region only. These settings can be updated in the tool to expand the inventory coverage to other regions.

**After installing the DynamoDB stack (Template 1), you can install the remaining stacks (Templates 2, 3, and 4) concurrently. There is no need to wait for each to finish before starting the next.**

`https://rodeolabz-us-west-2.s3.amazonaws.com/msam/msam-dynamodb-release.json`

#### Input Parameters

1. Provide a stack name
2. Provide an alternate bucket base name (leave at `rodeolabz` unless you are installing custom builds)
3. Provide the ARN for the DynamoDB IAM role created by the IAM Resources template

#### Outputs

Go to the Outputs section of the stack and copy the seven table names to a notepad. You will need these as input parameters for the next templates. See the following image.

![DynamoDB Tables](images/cfn-dynamodb-tables.png)

### Template 3: Core API and Periodic Tasks

This template will create a stack for the MSAM REST API, and periodic tasks used to refresh the content cache and discover logical resource connections.

`https://rodeolabz-us-west-2.s3.amazonaws.com/msam/msam-core-release.json`

#### Input Parameters

1. Provide a stack name
1. Provide an alternate bucket base name (leave at `rodeolabz` unless you are installing custom builds)
1. Provide the ARN for the Core IAM role created by the IAM Resources template
1. Paste each of the table names that were generated from the DynamoDB stack
1. Specify the time-to-live for the content, event and alarm tables; content not refreshed before this time will be removed from the cache

#### Outputs

Go to the Outputs section after the stack if created and copy the EndpointURL to a notepad. See the following image for the location of the URL.

![Core API Endpoint](images/cfn-core-endpoint.png)

### Template 4: CloudWatch Event Handler

This template creates a stack responsible for receiving events from Media Services and CloudWatch Alarm state changes. This includes MediaLive pipeline alerts or other service state changes. Create a stack for this template in every region you will be creating and monitoring Media Services resources using Events, Aleets, and Alarms.

`https://rodeolabz-us-west-2.s3.amazonaws.com/msam/msam-events-release.json`

#### Input Parameters

1. Provide a stack name
1. Provide an alternate bucket base name (leave at `rodeolabz` unless you are installing custom builds)
1. Provide the ARN for the Events IAM role created by the IAM Resources template
1. Paste the requested table names generated from the DynamoDB stack
1. Specify the region of the DynamoDB stack (such as us-west-2, us-east-1, or eu-west-1, for example)
1. Specify the time-to-live in seconds all recorded events; see the examples next to the input

#### Outputs

None

### Template 5: Browser Application

This template will install a copy of the MSAM browser application into an S3 bucket. Files added by the CloudFormation template will have their ACL set to `public-read` to allow access over HTTPS.

`https://rodeolabz-us-west-2.s3.amazonaws.com/msam/msam-browser-app-release.json`

### Input Parameters

1. Provide a stack name
2. Provide an alternate bucket base name (leave at `rodeolabz` unless you are installing custom builds)
3. Provide the ARN for the Web IAM role created by the IAM Resources template

### Outputs

Go to the Outputs section of the created stack and copy the MSAMBrowserURL to a notepad, which is the root of a CloudFront distribution. This is the URL to start the application on your workstation. See the following image for the location of the URL.

![Browser URL](images/cfn-browser-url.png)

## Retrieve the API Key for the REST API

The MSAM back-end requires an API key to access any of the REST endpoints. The Core API CloudFormation template creates a default API key automatically. The key is not displayed in Outputs section of the created stack. You can retrieve the key from the AWS console. **By default, no access is possible until the following steps are performed.**

1. Change to the Resources tab of the Core API stack
2. Click the link for the API Key in the Physical ID column of the Resources listing
3. Click the Show link in the main compartment for the API key
6. Copy the API Key and keep it with the Endpoint URL
  
![API Key Value](images/api-key.jpeg)

### Multiple Users and Access Control

**You can create multiple API keys, each with different names that are provided to separate groups.**

Note that if you want to share the UI with a colleague you can do so easily by providing the browser application URL, core endpoint URL and an API key. If an API key is stolen or lost, create a new API key and delete the previous one. All users that require access can be sent the updated API key that they will have to update in the browser application. MSAM will prompt the user to update the endpoint and key if the previously used settings are unable to access the back-end.

## Start the MSAM UI 

**Wait about 5-10 minutes for the first data gathering of the services and connection mapping to complete. This is needed only the first time after creation of the MSAM instance.**

Continue to the [Usage](USAGE.md) guide to start using the tool.

### Optional Parameters

As of 1.5.0, the MSAM browser URL can be the root of the CloudFront distribution URL or with `index.html` added. These two URLs are equivalent:

`https://d1c8z4f93zrlmx.cloudfront.net/`

`https://d1c8z4f93zrlmx.cloudfront.net/index.html`

The following parameters can be used with the second form of the URL with `index.html` to customize the start-up of the browser tool.

1. **diagram** - The name of a diagram to show right after start-up
2. **endpoint** - The endpoint URL to use for the connection
3. **key** - The API key to use with the chosen endpoint URL

#### Examples

Show a default diagram named Livestream on start-up

`https://d1c8z4f93zrlmx.cloudfront.net/index.html?diagram=Livestream`

Automatically connect to an endpoint with an API key

`https://d1c8z4f93zrlmx.cloudfront.net/index.html?endpoint=https://oplfnxzh7l.execute-api.us-east-1.amazonaws.com/msam/&key=69ZSAV3tBX7YYfh1XTcsq2fLcE7Z0ETY4JXclqJJ`

**NOTE: This above parameters should only be used for secure or demonstration environments. Anyone with this URL can connect and use MSAM.**

## Installation Permissions

The CloudFormation templates provided for MSAM installation require permissions to create and configure several different types of cloud resources. The user launching the CloudFormation templates must have permissions to create the resources defined in the templates. CloudFormation will assume that user's permissions temporarily during installation to complete the steps. 

There are several options for the user installing the templates to have the correct permissions:

1. An IAM user with AdministratorAccess role attached
2. An IAM user with the provided [group](#msam-iam-resources) attached to it, or the policy file attached inline from [distribution files](dist/iam-install-policy.json)
1. Use the root user if no other options are available; using the root user is [generally discouraged](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_root-user.html)

### MSAM IAM Resources

MSAM's IAM template will install a Group with an inline policy with permissions sufficient to install all the templates of the solution. The IAM Group is named `<stackname>-installationGroup-<ID>` and includes the same policy as [this file](dist/iam-install-policy.json). Add the users to this group who will be installing the solution if your organization has strict requirements about the AdministratorAccess managed policy.

[This file](dist/iam-install-policy.json) is a policy that can be added inline to a user or role and defines sufficient permissions to install all the templates included with MSAM.

## DynamoDB Considerations

There are seven DynamoDB tables used by MSAM. They are:

* [StackName]-Alarms-[ID]
* [StackName]-Channels-[ID]
* [StackName]-CloudWatchEvents-[ID]
* [StackName]-Content-[ID]
* [StackName]-Events-[ID]
* [StackName]-Layout-[ID]
* [StackName]-Settings-[ID]

Each table is configured for on-demand capacity by the CloudFormation template. This allows MSAM to automatically scale it's data handling capacity from small to very large Media Services installations.


## Versions and Updates

Each template includes a timestamp that indicates it's revision level. The timestamp is shown in the description of each template.

```
Media Services Application Mapper (MSAM) browser application (ID: 1537396573)
Media Services Application Mapper (MSAM) cloud API (ID: 1537396573)
```

You can also view the build timestamp in the tool by selecting the Tools menu and MSAM Build Numbers menu item. A dialog box will show the timestamps of each component and show a warning if they are seven or more days apart.

Any updates provided will be done via updates to the CloudFormation template files. In the CloudFormation console, click on the specific stack to be updated. From the top-right select Update Stack and point it to the stack link, check the IAM resource check boxes (if they are applicable to this specific update), and update the stack. 

### Upgrading Template Installation

There is not a direct upgrade path from the multiple template installation process to the new master and nested template installation process. The recommended approach for moving from the old to new process is to install a new copy of MSAM using the master template and then use our DynamoDB tool to migrate all data from the old tables to the new tables.

The advantage of this approach is that both systems can be running side-by-side after the data migration to verify everything has copied successfully. See the next section on the Migration Tool to learn more.

## DynamoDB Table Migration Tool

The Migration Tool is a Python program designed to copy data from one DynamoDB table to another. You can use this tool to copy the contents of each MSAM DynamoDB table from one installation to another. There are several reasons you might want to do this:

* Setting up a duplicate system for production and test, with the same diagrams, alarms, and layout for both
* Moving from an old to new installation of MSAM that cannot be upgraded with the templates

### Requirements

* Python 3.x installed and available from the command line
* boto3 package is installed and accessible by the above Python
* AWS CLI profile name that is configured to access the account and DynamoDB tables used by MSAM
* Source and destination DynamoDB tables are located in the same account and same region


### Usage

```
$ python copy_table.py -h

usage: copy_table.py [-h] --source SOURCE --destination DESTINATION
                     [--region REGION] [--profile PROFILE]

Copy database items from one DynamoDB table to another.

optional arguments:
  -h, --help            show this help message and exit
  --source SOURCE       source table name
  --destination DESTINATION
                        destination table name
  --region REGION       the region where the tables reside (if not provided,
                        default is us-west-2)
  --profile PROFILE     the AWS profile to use (if not provided, default
                        profile is used)
```


### Example: Duplicating Tables Between Two Stacks

1. Sign-in to the AWS Console
2. Navigate to the CloudFormation console
3. Find the DynamoDB stack for the old and new stacks
4. Record the table names for each stack
5. Copy the tables from the old to new stack, skipping the Content table
6. Start the new installation of MSAM and verify tiles, diagrams, layout, alarms, etc.

#### Source Table Names

```
oldinstall-DynamoDBModuleStack-1BL5SHLW7QL8P-Alarms-1VM2MNB13D37Y
oldinstall-DynamoDBModuleStack-1BL5SHLW7QL8P-Channels-OJ059JTCKFVL
oldinstall-DynamoDBModuleStack-1BL5SHLW7QL8P-CloudWatchEvents-1LA5KI02ULY10
oldinstall-DynamoDBModuleStack-1BL5SHLW7QL8P-Content-JLLPFGYMS2LW
oldinstall-DynamoDBModuleStack-1BL5SHLW7QL8P-Events-UB108ABQTFK
oldinstall-DynamoDBModuleStack-1BL5SHLW7QL8P-Layout-SJVH87QY4VPM
oldinstall-DynamoDBModuleStack-1BL5SHLW7QL8P-Settings-1IZ5B60KHU0IL
```


#### Destination Table Names

```
freshinstall-DynamoDBModuleStack-47U9UHHXPWO0-Alarms-EXEGD9CBBRVT
freshinstall-DynamoDBModuleStack-47U9UHHXPWO0-Channels-S7H7V3GU06L8
freshinstall-DynamoDBModuleStack-47U9UHHXPWO0-CloudWatchEvents-18BSF813RQWLU
freshinstall-DynamoDBModuleStack-47U9UHHXPWO0-Content-5ZTZ0BYLED9M
freshinstall-DynamoDBModuleStack-47U9UHHXPWO0-Events-VK1R6QJ3HAL5
freshinstall-DynamoDBModuleStack-47U9UHHXPWO0-Layout-1HQ6C00JC60ZJ
freshinstall-DynamoDBModuleStack-47U9UHHXPWO0-Settings-HF5BF72M35KH
```

#### Commands

**Note:** Skip the Content table because that is populated automatically with the inventory of the selected regions in the account. If your source stack is missing a table, such as CloudWatchEvents, you can safely skip it.

```
python copy_table.py --source oldinstall-DynamoDBModuleStack-1BL5SHLW7QL8P-Alarms-1VM2MNB13D37Y --destination freshinstall-DynamoDBModuleStack-47U9UHHXPWO0-Alarms-EXEGD9CBBRVT --profile personal --region us-east-1
python copy_table.py --source oldinstall-DynamoDBModuleStack-1BL5SHLW7QL8P-Channels-OJ059JTCKFVL --destination freshinstall-DynamoDBModuleStack-47U9UHHXPWO0-Channels-S7H7V3GU06L8 --profile personal --region us-east-1
python copy_table.py --source oldinstall-DynamoDBModuleStack-1BL5SHLW7QL8P-CloudWatchEvents-1LA5KI02ULY10 --destination freshinstall-DynamoDBModuleStack-47U9UHHXPWO0-CloudWatchEvents-18BSF813RQWLU --profile personal --region us-east-1
python copy_table.py --source oldinstall-DynamoDBModuleStack-1BL5SHLW7QL8P-Events-UB108ABQTFK --destination freshinstall-DynamoDBModuleStack-47U9UHHXPWO0-Events-VK1R6QJ3HAL5 --profile personal --region us-east-1
python copy_table.py --source oldinstall-DynamoDBModuleStack-1BL5SHLW7QL8P-Layout-SJVH87QY4VPM --destination freshinstall-DynamoDBModuleStack-47U9UHHXPWO0-Layout-1HQ6C00JC60ZJ --profile personal --region us-east-1
python copy_table.py --source oldinstall-DynamoDBModuleStack-1BL5SHLW7QL8P-Settings-1IZ5B60KHU0IL --destination freshinstall-DynamoDBModuleStack-47U9UHHXPWO0-Settings-HF5BF72M35KH --profile personal --region us-east-1
```



## Raw Web Content

The MSAM browser application in zipped form is available from the following URL. The numeric value at the end of this file is the same as other files from the same build.

`https://s3-us-west-2.amazonaws.com/rodeolabz-us-west-2/msam/msam-web-NNNNNNNNNN.zip`

This file can be extracted into a web server or another type of hosting environment. Take this approach if you prefer not to use the CloudFormation template to host the application in an S3 bucket.

## Navigate

Navigate to [README](README.md) | [Workshop](WORKSHOP.md) | [Install](INSTALL.md) | [Usage](USAGE.md) | [Uninstall](UNINSTALL.md) | [Rest API](REST_API.md)