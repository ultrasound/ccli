from cement import Controller, ex, shell
from ..aws.ec2 import EC2Operation


class AWS(Controller):

    class Meta:
        label = 'aws'
        stacked_type = 'nested'
        stacked_on = 'base'
        help = 'manage AWS'
        title = 'AWS commands'

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

