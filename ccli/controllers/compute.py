# -*- coding: utf-8 -*-
from pprint import pprint

from cement import Controller, ex, shell
from PyInquirer import prompt, print_json, Separator
from examples import custom_style_3


class Compute(Controller):

    class Meta:
        label = 'compute'
        stacked_type = 'nested'
        stacked_on = 'base'
        help = 'Multi Public Compute'
        title = 'Multi Public Compute'
        description = 'Managing Multi Public Compute'


class EC2(Controller):
    class Meta:
        label = 'ec2'
        stacked_type = 'embedded'
        stacked_on = 'compute'
        help = 'manage EC2'
        title = 'EC2 operations'
        description = 'Operating EC2 instances'
