import os
import subprocess
import urllib
from gridapi.resources.models import GridEntity, configs

class custom_infrastructure_generator(object):
    def __init__(self, grid_name, *args, **kwargs):
        self.grid_name = grid_name
        self.current_grid = GridEntity.objects(name=grid_name).get()
        grid = self.current_grid
        self.current_config = configs[grid.provider].objects(parentgrid=grid_name).get()

    def generate_ssh_key(self):
        with open('result/{}/grid.pem'.format(self.grid_name), 'w+') as ssh_key:
            ssh_key.write(urllib.unquote(self.current_config.sshkeydata))

    def generate_all(self):
        self.generate_ssh_key()
        os.chmod('result/{}/grid.pem'.format(self.grid_name), 0600)
        subprocess.check_call(['ssh-add', 'result/{}/grid.pem'.format(self.grid_name)])
