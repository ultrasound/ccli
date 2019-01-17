# -*- coding: utf-8 -*-
from pprint import pprint

from cement import Controller, ex, shell
from PyInquirer import prompt, print_json, Separator
from examples import custom_style_3

from ..aws.ec2 import EC2Operation, SecurityGroups, availability_zones
from ..aws.ec2 import EC2Templates as tmp
from ..aws.ec2 import INSTANCE_TYPES, AMIS

from ..aws.ec2_key import KeyPairOperation

key_pair_operation = KeyPairOperation()


class AWS(Controller):

    class Meta:
        label = 'aws'
        stacked_type = 'nested'
        stacked_on = 'base'
        help = 'manage AWS'
        title = 'AWS commands'
        description = 'Managing AWS Cloud'


class EC2(Controller):

    class Meta:
        label = 'ec2'
        stacked_type = 'nested'
        stacked_on = 'aws'
        help = 'manage EC2'
        title = 'EC2 operations'
        description = 'Operating EC2 instances'

    def __init__(self):
        super().__init__()
        self.ec2_ = EC2Operation()

    @ex(help='List instances')
    def list(self):
        from ..aws.ec2 import get_all_instance

        all_instance = False
        save_to_file = False

        allInstances = shell.Prompt("Do you want to list all instances?",
                                    options=['yes', 'no'], numbered=True)

        if allInstances.prompt() == 'yes':
            all_instance = True
        elif allInstances.prompt() == 'no':
            instances = get_all_instance()
            instance_id = shell.Prompt("Select instance ID",
                                       options=instances, numbered=True)

            self.ec2_.instance_ids = instance_id

        saveToFile = shell.Prompt("Do you want to save data into JSON?",
                                  options=['yes', 'no'], numbered=True)

        if saveToFile.prompt() == 'yes':
            save_to_file = True

        self.ec2_.desc_instances(all_instance=all_instance, save_to_file=save_to_file)

    @ex(help='create new instance')
    def create(self):
        pass

    @ex(help='delete an instance')
    def delete(self):
        pass

    @ex(help='start an instance')
    def start(self):
        pass

    @ex(help='stop an instance')
    def stop(self):
        pass

    @ex(help='reboot an instance')
    def reboot(self):
        pass

    @ex(help='terminate an instance')
    def terminate(self):
        pass


class Templates(Controller):

    class Meta:
        label = 'templates'
        stacked_type = 'embedded'
        stacked_on = 'ec2'
        help = 'Managing EC2 templates'
        title = 'Managing EC2 templates'
        description = 'Managing EC2 Templates'

    @ex(help='create templates')
    def create_templates(self):
        amis = AMIS
        amis_names = [ami['name'] for ami in amis]
        amis_id = [ami['id'] for ami in amis]

        security_groups = SecurityGroups.describe_security_groups()
        sg_names = [security_group['GroupName'] for security_group in security_groups.get('SecurityGroups')]
        sg_ids = [security_group['GroupId'] for security_group in security_groups.get('SecurityGroups')]

        zones = availability_zones()
        zone_names = [zone['ZoneName'] for zone in zones.get('AvailabilityZones')]

        key_pairs = key_pair_operation.desc_keys()
        key_name = [key['KeyName'] for key in key_pairs.get('KeyPairs')]

        questions = [
            {
                'type': 'input',
                'name': 'template name',
                'message': 'What is a template name?'
            },
            {
                'type': 'list',
                'name': 'instance type',
                'message': 'Select Instance type',
                'choices': INSTANCE_TYPES,
            },
            {
                'type': 'list',
                'name': 'image name',
                'message': 'Select AMI(Amazon Machine Image)',
                'choices': amis_names,
            },
            {
                'type': 'confirm',
                'name': 'public address',
                'message': 'Do you want to use publc address?',
                'default': True,
            },
            {
                'type': 'list',
                'name': 'security group',
                'message': 'Select Security Group',
                'choices': sg_names,
            },
            {
                'type': 'list',
                'name': 'availability zone',
                'message': 'Select Availability Zone',
                'choices': zone_names,
            },
            {
                'type': 'list',
                'name': 'key pair',
                'message': 'Select Key Pair',
                'choices': key_name,
            },
            {
                'type': 'list',
                'name': 'shutdown behavior',
                'message': 'Select instance shutdown behavior',
                'choices': ['stop', 'terminate'],
            },
            {
                'type': 'confirm',
                'name': 'tag specifications',
                'message': 'Do you want to put a tag?',
                'default': False,
            },
            {
                'type': 'input',
                'name': 'tag key',
                'message': 'Put Key for tag',
                'when': lambda answers: answers['tag specifications']
            },
            {
                'type': 'input',
                'name': 'tag value',
                'message': 'Put Value for tag',
                'when': lambda answers: answers['tag specifications']
            }
        ]

        answers = prompt(questions, style=custom_style_3)

        template_data = {
            'ImageId': amis_id[amis_names.index(answers['image name'])],
            'KeyName': answers['key pair'],
            'InstanceType': answers['instance type'],
            'NetworkInterfaces': [
                {
                    'AssociatePublicIpAddress': answers['public address'],
                    'DeleteOnTermination': True,
                    'Groups': [
                        sg_ids[sg_names.index(answers['security group'])]
                    ],
                },
            ],
            'Placement': {
                'AvailabilityZone': answers['availability zone'],
                'Tenancy': 'default',
            },
            'DisableApiTermination': False,
            'InstanceInitiatedShutdownBehavior': answers['shutdown behavior'],
        }

        try:
            if answers['tag value'] and answers['tag key']:
                tag_list = [{'ResourceType': 'instance',
                             'Tags': [
                                 {
                                     'Value': answers['tag value'],
                                     'Key': answers['tag key']
                                 }
                             ]}]

                template_data['TagSpecifications'] = tag_list
        except KeyError:
            pass
        print(template_data)
        tmp.create_launch_template(template_name=answers['template name'], template_data=template_data)


