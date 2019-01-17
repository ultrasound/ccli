import boto3
from botocore.exceptions import ClientError

ec2 = boto3.client('ec2', region_name='ap-northeast-2')


class VPC:
    def describe_vpcs(self):
        try:
            response = ec2.describe_vpcs()

            return response
        except ClientError as e:
            print(e)

    def describe_subnets(self):
        try:
            response = ec2.describe_subnets()

            return response
        except ClientError as e:
            print(e)
