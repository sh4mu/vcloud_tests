from pyvcloud.vcd.client import BasicLoginCredentials, Client
from pyvcloud.vcd.vdc import VDC
from pyvcloud.vcd.org import Org
from pyvcloud.vcd.vapp import VApp
from pyvcloud.vcd.vm import VM

import sys

# Connect to vCloud Director
host = 'vcloud01.uclab.intra'
username = 'uclab'
password = 'Celfocus2021'
org = 'Celfocus'
vdc = 'uclab'
api_version = '35.0'

client = Client(host, api_version, verify_ssl_certs=False)
client.set_credentials(BasicLoginCredentials(username, org, password))

org = Org(client, resource=client.get_org())
vdc_resource = org.get_vdc(vdc)
vdc = VDC(client, resource=vdc_resource)

## Get catalog vApp/VM with base image
catalog_vapp_name = 'base_template'
catalog_vm_name = 'GD-RH8-template'

catalog_item = org.get_catalog_item('jctests', catalog_vapp_name)
catalog_vapp = VApp(client, href=catalog_item.Entity.get('href'))
catalog_vm = VM(client, catalog_vapp.get_vm(catalog_vm_name).get('href'))
print('name: {}'.format(catalog_vm.get_resource().get('name')))

## Create new empty vApp
vapp_name = 'xanana'
vapp_description = 'Custom vApp template for celfocus'
network_name = 'oam'
script_path = '/opt/config/bin/test'

result = vdc.create_vapp(name=vapp_name,                
                description=vapp_description)

task = client.get_task_monitor().wait_for_status(task=result.Tasks.Task[0])
# assert task.get('status') == TaskStatus.SUCCESS.value
    
new_vapp = VApp(client, resource=vdc.get_vapp(vapp_name))
for link in new_vapp.get_resource().findall('{http://www.vmware.com/vcloud/v1.5}Link'):
    print('2 rel {}, media {}, name {}'.format(link.get('rel'), link.get('type'), link.get('name')))
    
## Add VMs to vApp from existing VM template
spec_pilot_a = {'source_vm_name': catalog_vm.get_resource().get('name'), 'vapp': catalog_vapp.get_resource()}
spec_pilot_a['target_vm_name'] = 'xanana-0-0-1'
spec_pilot_a['hostname'] = 'xanana-0-0-1'
spec_pilot_a['network'] = 'oam'
# spec_pilot_a['ip_allocation_mode'] = 'pool'

spec_pilot_b = {'source_vm_name': catalog_vm.get_resource().get('name'), 'vapp': catalog_vapp.get_resource()}
spec_pilot_b['target_vm_name'] = 'xanana-0-0-9'
spec_pilot_b['hostname'] = 'xanana-0-0-9'
spec_pilot_b['network'] = 'oam' 
# spec_pilot_b['ip_allocation_mode'] = 'pool'

vms = [spec_pilot_a, spec_pilot_b]

new_vapp.add_vms(vms, deploy=False, power_on=False, all_eulas_accepted=True)
new_vapp.reload()

client.logout()
