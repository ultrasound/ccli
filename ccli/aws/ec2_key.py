import boto3
import json


ec2 = boto3.client('ec2', region_name='ap-northeast-2')


class KeyPairOperation:
    def __init__(self):
        self._key_name = ''

    @property
    def key_name(self):
        return self._key_name

    @key_name.setter
    def key_name(self, key_name):
        self._key_name = key_name

    def create_key(self):
        response = ec2.create_key_pair(self._key_name)
        key = response["KeyMaterial"]
        keyName = key_name + ".pem"

        with open(keyName, 'w') as f:
            f.write(key)

    def del_key(self):
        response = ec2.delete_key_pair(self._key_name)
        print(json.dumps(response, indent=4))

    def desc_keys(self):
        response = ec2.describe_key_pairs()
        # print(json.dumps(response, indent=4))

        return response


if __name__ == '__main__':
    key_pair = KeyPairOperation()

    while True:
        command = input(""
                        "1: Create Key,"
                        "2: Delete Key, "
                        "3: Listing Keys \n:")

        if command == "1":
            key_name = input("Type Key Name: ")
            key_pair.key_name = key_name
            key_pair.create_key()
        elif command == "2":
            key_name = input("Type Key Name: ")
            key_pair.key_name = key_name
            key_pair.del_key()
        elif command == "3":
            res = key_pair.desc_keys()
            for keyname in res['KeyPairs']:
                print('Key Name: ', keyname['KeyName'])
