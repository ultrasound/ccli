import os

from libcloud.compute.types import Provider
from libcloud.compute.providers import get_driver

EC2_ACCESS_ID = os.environ['AWS_ACCESS_KEY_ID']
EC2_SECRET_KEY = os.environ['AWS_SECRET_ACCESS_KEY']


class Compute:
    EC2Driver = get_driver(Provider.EC2)
    def __init__(self):
        self. EC2 = self.EC2Driver(EC2_ACCESS_ID, EC2_SECRET_KEY)

    def list_size(self):
        self.EC2.list_sizes()


if __name__ == '__main__':
     IMAGE_ID = 'ami-c8052d8d'
    SIZE_ID = 't1.micro'

    cls = get_driver(Provider.EC2())
    driver = cls(ACCESS_ID, SECRET_KEY, region="us-west-1")

    sizes = driver.list_sizes()
    images = driver.list_images()

    size = [s for s in sizes if s.id == SIZE_ID][0]
    image = [i for i in images if i.id == IMAGE_ID][0]

    node = driver.create_node(name='test-node', image=image, size=size)

    # Here we allocate and associate an elastic IP
    elastic_ip = driver.ex_allocate_address()
    driver.ex_associate_address_with_node(node, elastic_ip)

    # When we are done with our elastic IP, we can disassociate from our
    # node, and release it
    driver.ex_disassociate_address(elastic_ip)
    driver.ex_release_address(elastic_ip)

    volume = driver.create_volume(size=100, name='Test GP volume',
                                  ex_volume_type='gp2')

    volume = driver.create_volume(size=100, name='Test IOPS volume',
                                  ex_volume_type='io1', ex_iops=1000)


