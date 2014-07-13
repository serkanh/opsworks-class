#!/usr/bin/python
import boto.opsworks.layer1 as opsworks


##########################################################################################
# Simple class to manage opsworks provisioning                                           #
# It can be useful to integrate CI servers and issue                                     #
# lifecycle events such as deployment through aws boto library                           #
# Make sure to add your access credentials in .boto file in                              #
# home directory.                                                                        #
# http://boto.readthedocs.org/en/latest/getting_started.html#configuring-boto-credentials#
##########################################################################################


class OpsManage:
    """Opsworks management class"""
    #conn = opsworks.OpsWorksConnection()

    def __init__(self, stack_name):
        self.stack_name = stack_name
        self.conn = opsworks.OpsWorksConnection()

    def print_stackname(self):
        print self.stack_name

    def get_stack_id(self):
        for stack in self.conn.describe_stacks()['Stacks']:
            if stack.get('Name') == self.stack_name:
                return stack['StackId']

    def get_layers(self):
        layers = [layer for layer in self.conn.describe_layers(stack_id=self.get_stack_id())['Layers']]
        return layers

    def get_layer_id(self, layer_name):
        layers = self.get_layers()
        for layer in layers:
            if layer['Name'] == layer_name:
                return layer['LayerId']



    def get_stack_inst_info(self):
        """


        """
        instances = [ins for ins in self.conn.describe_instances(self.get_stack_id())['Instances']]
        print instances
        for ins in instances:
            if ins['Status'] == 'online':
                print(
                    "Hostname:", ins['Hostname'], "Status:", ins['Status'], "Private-ip:", ins["PrivateIp"],
                    "Layer Id:", ins['LayerIds'], "Instance Id:", ins['InstanceId'])
            else:
                print("Hostname:", ins['Hostname'], "Status:", ins['Status'], "Layer Id:", ins['LayerIds'], "Instance Id:", ins['InstanceId'])

    def get_online_layer_insts(self, layer_name):
        instances = [ins for ins in self.conn.describe_instances(self.get_stack_id())['Instances']]
        online_instances = [inst['InstanceId'] for inst in instances if inst['Status']=='online' and inst['LayerIds'][0] == self.get_layer_id(layer_name)]
        layerids = [inst['LayerIds'] for inst in instances]
        return online_instances

    #Calls predefined chef recipe on a layer
    def execute_recipe(self, stack_name, layer_name, recipe, recipe_function):
        args = {
        'stack_id': self.get_stack_id(),
        'instance_ids': self.get_online_layer_insts(layer_name),
        'comment': 'Automated deployment',
        'command': {
            'Name': 'execute_recipes',  #'Args': {'recipes':['app-staging-deploy::deploy']}
            'Args': {'recipes': ['{}::{}'.format(recipe, recipe_function)]}

        }}

        self.conn.create_deployment(**args)



apl_staging = OpsManage('aboutPlace Staging')
#print(apl_staging.get_layers())
#print(apl_staging.get_layer_id('API'))
print(apl_staging.get_stack_inst_info())
print(apl_staging.get_online_layer_insts('API'))
apl_staging.execute_recipe('aboutPlace Staging','API','api-deploy','deploy')


