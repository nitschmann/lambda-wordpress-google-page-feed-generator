# lambda-wordpress-google-page-feed-generator

AWS SAM template to generate Google page feed CSV file out of WordPress XML feeds once per day at midnight and upload the result to S3.
The code in the repo could be directly deployed with SAM AWS Cli and CloudFormation. CloudWatched scheduled events could be used as trigger, as well as any other trigger that fits your needs.
