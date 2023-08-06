# Copyright 2014 OpenCore LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import logging
import sh
import sys
from string import Template
from ferry.config.openmpi.mpiconfig import *

class OpenMPIClientInitializer(object):
    """
    Create a new initializer
    Param user The user login for the git repo
    """
    def __init__(self):
        self.mpi = OpenMPIInitializer()
        self.container_data_dir = self.mpi.container_data_dir
        self.container_log_dir = self.mpi.container_log_dir

    @property
    def template_dir(self):
        self.mpi.template_dir

    @template_dir.setter
    def template_dir(self, value):
        self.mpi.template_dir = value

    @property
    def template_repo(self):
        self.mpi.template_repo

    @template_repo.setter
    def template_repo(self, value):
        self.mpi.template_repo = value

    """
    Generate a new hostname
    """
    def new_host_name(self, instance_id):
        return 'openmpi_client' + str(instance_id)

    """
    Start the service on the containers. 
    """
    def start_service(self, containers, entry_point, fabric):
        self.mpi.start_service(containers, entry_point, fabric)
    def restart_service(self, containers, entry_point, fabric):
        self.mpi.restart_service(containers, entry_point, fabric)
    def stop_service(self, containers, entry_point, fabric):        
        self.mpi.stop_service(containers, entry_point, fabric)

    """
    Get the ports necessary.
    """
    def get_necessary_ports(self, num_instances):
        return self.mpi.get_necessary_ports(num_instances)

    """
    Get the internal ports. 
    """
    def get_exposed_ports(self, num_instances):
        return self.mpi.get_exposed_ports(num_instances)

    """
    Generate a new configuration
    Param num Number of instances that need to be configured
    Param image Image type of the instances
    """
    def generate(self, num):
        return self.mpi.generate(num)

    """
    Apply the configuration to the instances
    """
    def apply(self, config, containers):
        config_dirs, entry_point = self.mpi.apply(config, containers)
        entry_point['type'] = 'mpi-client'
        return config_dirs, entry_point
