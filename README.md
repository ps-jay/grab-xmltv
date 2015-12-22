# grab-xmltv
Grab XMLTV data and store in S3 - Python AWS Lambda function

# AWS Setup

## Lambda role

Role "lambda_xmltv_role" has the following customer managed policies attached:

*lambda_s3_get_put*

```
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "s3:GetObject",
                "s3:PutObject"
            ],
            "Resource": [
                "arn:aws:s3:::*"
            ]
        }
    ]
}
```

*lambda_logs*

```
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "logs:CreateLogGroup",
                "logs:CreateLogStream",
                "logs:PutLogEvents"
            ],
            "Resource": "arn:aws:logs:*:*:*"
        }
    ]
}
```

*lambda_kms_decrypt*

```
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "kms:Decrypt",
                "kms:DescribeKey"
            ],
            "Resource": [
                "arn:aws:iam:::*"
            ]
        }
    ]
}
```

## KMS Key

```
aws kms create-key \
  --policy '
{
  "Id": "xmltv",
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "Enable IAM User Permissions",
      "Effect": "Allow",
      "Principal": {
        "AWS": [
          "arn:aws:iam::100000000000:root"
        ]
      },
      "Action": "kms:*",
      "Resource": "*"
    },
    {
      "Sid": "Allow access for Key Administrators",
      "Effect": "Allow",
      "Principal": {
        "AWS": [
          "arn:aws:iam::100000000000:user/foo"
        ]
      },
      "Action": [
        "kms:Create*",
        "kms:Describe*",
        "kms:Enable*",
        "kms:List*",
        "kms:Put*",
        "kms:Update*",
        "kms:Revoke*",
        "kms:Disable*",
        "kms:Get*",
        "kms:Delete*",
        "kms:ScheduleKeyDeletion",
        "kms:CancelKeyDeletion"
      ],
      "Resource": "*"
    },
    {
      "Sid": "Allow encrypt use of the key",
      "Effect": "Allow",
      "Principal": {
        "AWS": [
          "arn:aws:iam::100000000000:user/foo"
        ]
      },
      "Action": [
        "kms:Encrypt",
        "kms:ReEncrypt*"
      ],
      "Resource": "*"
    },
    {
      "Sid": "Allow decrypt use of the key",
      "Effect": "Allow",
      "Principal": {
        "AWS": [
          "arn:aws:iam::100000000000:role/lambda_xmltv_role",
          "arn:aws:iam::100000000000:user/foo"
        ]
      },
      "Action": [
        "kms:Decrypt",
        "kms:DescribeKey"
      ],
      "Resource": "*"
    }
  ]
}' \
  --description "XMLTV secrets" \
  --region us-west-2
```

```
aws kms create-alias \
  --alias-name alias/xmltv \
  --target-key-id 10000000-0000-0000-0000-000000000000 \
  --region us-west-2
```

## S3 Bucket

Enable HTTP access.
Apply policy:

```
{
        "Version": "2012-10-17",
        "Statement": [
                {
                        "Sid": "AddPerm",
                        "Effect": "Allow",
                        "Principal": "*",
                        "Action": "s3:GetObject",
                        "Resource": "arn:aws:s3:::bucket/*"
                }
        ]
}
```

## KMS secrets

Encrypt the secrets:

```
aws kms encrypt --key-id alias/xmltv --plaintext "foo" --query CiphertextBlob --output text --region us-west-2 | base64 -d | base64
```
