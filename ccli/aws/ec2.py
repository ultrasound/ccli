import datetime
import json

import boto3
from botocore.exceptions import ClientError

ec2 = boto3.client('ec2', region_name='ap-northeast-2')

INSTANCE_TYPES = ['t2.nano',
                  't2.micro',
                  't2.small',
                  't2.medium',
                  't2.large',
                  't2.xlarge',
                  't2.2xlarge']

AMIS = [{'name': 'Amazon Linux2', 'id': 'ami-018a9a930060d38aa'},
       {'name': 'Ubuntu', 'id': 'ami-06e7b9c5e0c4dd014', 'version': '18.04'},
       {'name': 'RedHat', 'id': 'ami-3eee4150', 'version': '7.5'},
       {'name': 'SUSE', 'id': 'ami-04ecb44b7d8e8d354', 'version': 'ES15'}]

REGIONS = [
    'us-east-1',
    'us-east-2',
    'us-west-1',
    'us-west-2',
    'us-gov-west-1',
    'eu-west-1',
    'eu-west-2',
    'eu-central-1',
    'ca-central-1',
    'ap-southeast-1',
    'ap-southeast-2',
    'ap-northeast-1',
    'ap-northeast-2',
    'ap-south-1',
    'sa-east-1',
    'cn-north-1',
]


def datetime_to_str(data):
    if isinstance(data, datetime.datetime):
        return data.__str__()


def get_all_instance():
    all_instances = ec2.describe_instances()

    instanceId_list = []
    for reservation in all_instances["Reservations"]:
        instance_id = reservation.get('Instances')[0].get('InstanceId')
        instanceId_list.append(instance_id)

    return instanceId_list


class EC2Operation:
    def __init__(self):
        self._instance_ids = ''

    @property
    def instance_ids(self):
        return self._instance_ids

    @instance_ids.setter
    def instance_ids(self, instance_ids):
        self._instance_ids = instance_ids

    def start_instances(self):
        """
        Starts an Amazon EBS-backed instance that you've previously stopped.

        :return:
        """
        try:
            ec2.start_instances(InstanceIds=[self._instance_ids], DryRun=True)
        except ClientError as e:
            if 'DryRunOperation' not in str(e):
                raise

        # Dry run succeeded, run start_instances without dryrun
        try:
            ec2.start_instances(InstanceIds=[self._instance_ids], DryRun=False)
            print("Instance ", self._instance_ids, ": starting\n")
            waiter = ec2.get_waiter('instance_running')
            waiter.wait(InstanceIds=[self._instance_ids])
            print("Instance ", self._instance_ids, ": running\n")
        except ClientError as e:
            print(e)

    def stop_instances(self):
        """
        Stops an Amazon EBS-backed instance.
        :return:
        """
        # Do a dryrun first to verify permissions
        try:
            ec2.stop_instances(InstanceIds=[self._instance_ids], DryRun=True)
        except ClientError as e:
            if 'DryRunOperation' not in str(e):
                raise

        # Dry run succeeded, call stop_instances without dryrun
        try:
            ec2.stop_instances(InstanceIds=self._instance_ids, DryRun=False)
            print("Instance ", self.instance_ids, ": stopping")
            waiter = ec2.get_waiter('instance_stopped')
            waiter.wait(InstanceIds=self.instance_ids)
            print("Instance ", self.instance_ids, ": stopped\n")
        except ClientError as e:
            print(e)

    def reboot_instances(self):
        try:
            ec2.reboot_instances(InstanceIds=[self.instance_ids], DryRun=True)
        except ClientError as e:
            if 'DryRunOperation' not in str(e):
                print("You don't have permission to reboot instances.")
                raise

        try:
            ec2.reboot_instances(InstanceIds=[self.instance_ids], DryRun=False)
            print("Instance ", self.instance_ids, ": rebooting")
            waiter = ec2.get_waiter('instance_status_ok')
            waiter.wait(InstanceIds=[self.instance_ids])
            print("Instance ", self.instance_ids, ": running\n")
        except ClientError as e:
            print('Error', e)

    def terminate_instances(self):
        """
        Shuts down one or more instances.

        :return:
        """
        try:
            ec2.terminate_instances(InstanceIds=[self.instance_ids], DryRun=True)
        except ClientError as e:
            if 'DryRunOperation' not in str(e):
                print("You don't have permission to terminate instances.")
                raise

        try:
            ec2.terminate_instances(InstanceIds=[self.instance_ids], DryRun=False)
            print("Instance ", self.instance_ids, ": terminating")
            waiter = ec2.get_waiter('instance_terminated')
            waiter.wait(InstanceIds=[self.instance_ids])
            print("Instance ", self.instance_ids, ": terminated\n")
        except ClientError as e:
            print('Error', e)

    def desc_instances(self, save_to_file=False, all_instance=False):
        """
        Describes one or more of your instances.

        :param save_to_file:
        :param all_instance:
        :return:
        """
        if all_instance:
            res = ec2.describe_instances()
            print(json.dumps(res, default=datetime_to_str, indent=4))
            if save_to_file:
                json.dump(res, open("all_instances.json", 'w'), default=datetime_to_str, indent=4)
            return res
        else:
            res = ec2.describe_instances(InstanceIds=[self.instance_ids])
            print(json.dumps(res, default=datetime_to_str, indent=4))
            if save_to_file:
                json.dump(res, open(self.instance_ids + ".json", 'w'), default=datetime_to_str, indent=4)

    def instance_status(self):
        try:
            response = ec2.describe_instances(InstanceIds=[self.instance_ids])
            status = response.get('Reservations')[0].get('Instances')[0].get('State').get('Name')
            print("Instance ", self.instance_ids, ": ", status)
            print("")
        except ClientError as e:
            print(e)


class LaunchEC2:
    @staticmethod
    def run_instance(max_cnt=1, min_cnt=1, template_name=None, **kwargs):
        ec2.run_instances(
            BlockDeviceMappings=[
                {
                    'Ebs': {
                        'DeleteOnTermination': kwargs['delete_on_termination'],
                        'VolumeSize': volume_size,
                        'VolumeType': 'gp2',
                    },
                },
            ],
            ImageId=image_id,
            InstanceType=instance_type,
            KeyName=key_name,
            MaxCount=max_cnt,
            MinCount=min_cnt,
            Placement={
                'AvailabilityZone': availability_zones_,
                'Tenancy': 'default',
            },
            DisableApiTermination=diasble_api_termination,
            InstanceInitiatedShutdownBehavior=shutdown_behavior,
            NetworkInsterfaces=[
                {
                    'AssociatePublicIpAddress': public_address,
                    'DeleteOnTermination': delete_on_termination,
                    'Groups': [
                        security_group,
                    ],
                    'SubnetId': subnet_id,
                },
            ],
        )

        try:
            ec2.run_instances(
                MaxCount=max_cnt,
                MinCount=min_cnt,
                DryRun=True,
                LaunchTemplate={
                    'LaunchTemplateName': template_name
                }
            )
        except ClientError as e:
            if 'DryRunOperation' not in str(e):
                print("You don't have permission to launch instances.")
                raise

        try:
            response = ec2.run_instances(
                MaxCount=max_cnt,
                MinCount=min_cnt,
                DryRun=True,
                LaunchTemplate={
                    'LaunchTemplateName': template_name
                }
            )

            ins_id = response.get('Instances')[0].get('InstanceId')
            public_dns_name = response.get('Instances')[0].get('PublicDnsName')
            public_ip_address = response.get('Instances')[0].get('PublicIpAddress')
            key_name = response.get('Instances')[0].get('KeyName')

            json.dump(response, open(ins_id + ".json", 'w'), default=datetime_to_str, indent=4)

            print(f'Instance ID: {ins_id}\n'
                  f'Public DNS Name: {public_dns_name}\n'
                  f'Public IP Address: {public_ip_address}\n'
                  f'Key Name: {key_name}\n')
        except ClientError as e:
            print(e)


class EC2Templates:
    @staticmethod
    def create_launch_template(template_name='', version_description='', template_data={}):
        try:
            ec2.create_launch_template(
                DryRun=True,
                LaunchTemplateName=template_name,
                VersionDescription=version_description,
                LaunchTemplateData=template_data
            )
        except ClientError as e:
            if 'DryRunOperation' not in str(e):
                print("You don't have permission to create template.")
                raise

        try:
            response = ec2.create_launch_template(
                DryRun=False,
                LaunchTemplateName=template_name,
                VersionDescription=version_description,
                LaunchTemplateData=template_data
            )

            template_id = response.get('LaunchTemplate').get('LaunchTemplateId')

            print(f'Template ID: {template_id}\nTemplate Name: {template_name}\n')
        except ClientError as e:
            print(e)


    @staticmethod
    def delete_launch_template(template_name=''):
        try:
            ec2.delete_launch_template(
                DryRun=True,
                LaunchTemplateName=template_name
            )
        except ClientError as e:
            if 'DryRunOperation' not in str(e):
                print("You don't have permission to delete template.")
                raise

        try:
            ec2.delete_launch_template(
                DryRun=False,
                LaunchTemplateName=template_name
            )

            print(template_name, " - deleted")
        except ClientError as e:
            print(e)

    @staticmethod
    def describe_launch_templates(template_name=None, template_id=None):
        if template_id is not None:
            response = ec2.describe_launch_templates(
                DryRun=False,
                LaunchTemplateIds=template_id
            )
        elif template_name is not None:
            response = ec2.describe_launch_templates(
                DryRun=False,
                LaunchTemplateNames=template_name,
            )
        else:
            response = ec2.describe_launch_templates(DryRun=False)

        return response

    @staticmethod
    def get_launch_template_data(InstanceId=''):
        response = ec2.get_launch_template_data(
            DryRun=False,
            InstanceId=InstanceId
        )

        return response


class SecurityGroups:
    @staticmethod
    def describe_security_groups():
        try:
            response = ec2.describe_security_groups()

            return response
        except ClientError as e:
            print(e)


def availability_zones():
    try:
        response = ec2.describe_availability_zones(
            DryRun=False,
        )

        return response
    except ClientError as e:
        print(e)


if __name__ == '__main__':
    ec2_ = EC2Templates()
    template_data = {
        "TagSpecifications": [
            {
                "ResourceType": "instance",
                "Tags": [
                    {
                        "Value": "Test",
                        "Key": "Name"
                    }
                ]
            }
        ],
        "ImageId": "ami-00dc207f8ba6dc919",
        "KeyName": "test",
        "CreditSpecification": {
            "CpuCredits": "standard"
        },
        "Placement": {
            "Tenancy": "default",
            "AvailabilityZone": "ap-northeast-2a"
        },
        "InstanceType": "t2.micro",
        "NetworkInterfaces": [
            {
                "SubnetId": "subnet-bd0c23d5",
                "DeleteOnTermination": True,
                "Groups": [
                    "sg-02996e2bf676d5776"
                ],
                "AssociatePublicIpAddress": True
            }
        ]
    }

    res = ec2_.create_launch_template(template_name='test', template_data=template_data)
    import pprint
    pprint.pprint(res)
