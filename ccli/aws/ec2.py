import datetime
import json

import boto3
from botocore.exceptions import ClientError

ec2 = boto3.client('ec2', region_name='ap-northeast-2')


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
    def run_instance(self, max_cnt=1, min_cnt=1, template_name=''):
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


class Templates:
    def create_launch_template(self, template_name='', version_description=None, template_data={}):
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

    def delete_launch_template(self, template_name=''):
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

    def describe_launch_templates(self, template_name=None, template_id=None):
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

    def get_launch_template_data(self, InstanceId=''):
        response = ec2.get_launch_template_data(
            DryRun=False,
            InstanceId=InstanceId
        )

        return response


if __name__ == '__main__':
    all_instances = ec2.describe_instances()

    instanceId_list = []
    for reservation in all_instances["Reservations"]:
        instance_id = reservation.get('Instances')[0].get('InstanceId')
        instanceId_list.append(instance_id)

    ec2_ = EC2Operation()

    while True:
        print("Instances List")

        for idx, instanceId in enumerate(instanceId_list, 1):
            print(idx, ": ", instanceId)

        print("")

        command = input("Operation\n"
                        "1: Stop Instances\n"
                        "2: Start Instances\n"
                        "3: Reboot Instances\n"
                        "4: Describe Instances\n"
                        "5: Check instance status\n"
                        "6: Launch instance\n"
                        "7: Exit\n:")

        if command not in ['1', '2', '3', '4', '5', '6']:
            print("Wrong number\n")
            continue

        print("")

        if command == '1':
            try:
                selected_instance = input("Instance ID to stop: ")
                print("")
                ec2_.instance_ids = instanceId_list[int(selected_instance) - 1]
                ec2_.stop_instances()
            except IndexError:
                print("Wrong Number\n")
                continue
        elif command == '2':
            try:
                selected_instance = input("Instance ID to start: ")
                print("")
                ec2_.instance_ids = instanceId_list[int(selected_instance) - 1]
                ec2_.start_instances()
            except IndexError:
                print("Wrong Number\n")
                continue
        elif command == '3':
            try:
                selected_instance = input("Instance ID to reboot: ")
                print("")
                ec2_.instance_ids = instanceId_list[int(selected_instance) - 1]
                ec2_.reboot_instances()
            except IndexError:
                print("Wrong Number\n")
                continue
        elif command == '4':
            while True:
                all_ = input("Do you want to describe all instances?(Y/N)\n")
                if all_.upper() not in ['Y', 'N']:
                    print("Type only Y or N\n")
                    continue
                break

            while True:
                save_ = input("Do you want to save describe into file?(Y/N)\n")
                if save_.upper() not in ['Y', 'N']:
                    print("Type only Y or N\n")
                    continue
                break

            if all_.upper() == "Y" and save_.upper() == "Y":
                ec2_.desc_instances(all_instance=True, save_to_file=True)
            elif all_.upper() == "Y" and save_.upper() == "N":
                ec2_.desc_instances(all_instance=True)
            else:
                selected_instance = input("Instance Id to describe: ")
                if save_.upper() == "Y":
                    ec2_.instance_ids = instanceId_list[int(selected_instance) - 1]
                    ec2_.desc_instances(save_to_file=True)
                else:
                    ec2_.instance_ids = instanceId_list[int(selected_instance) - 1]
                    ec2_.desc_instances()
        elif command == '5':
            try:
                selected_instance = input("Instance ID to check status: ")
                print("")
                ec2_.instance_ids = instanceId_list[int(selected_instance) - 1]
                ec2_.instance_status()
            except IndexError:
                print("Wrong Number\n")
                continue

        elif command == '6':
            pass

        elif command == '7':
            break

        else:
            print("Wrong Number")
            print("")
