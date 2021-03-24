# Introduction
hdm-redfish-script, developed by using Python, is a server management command tool based on HTTPs and Redfish/RESTful. It allows users to use commands to obtain server information and configure servers.

# Command format
An hdm-redfish-script command uses the python main.py -H host -p port -U username -P password [command] format, where:
*	-H host—Specifies the HDM IP address of the managed device.
*	-p port—Specifies the HTTPS port number. By default, the port number is 443. This option is optional.
*	-U username -P password—Specifies the HDM username and password of the managed device.
*	[command]—Specifies which action to take on which instance.

# Prerequisites
*	HDM-1.30.15 or later.Some commands might require specific HDM versions. For more information, see the specific command.
*	Windows Server 2012 R2、Windows 7、Windows 10、CentOS 6.2、CentOS 7.3
*	Python 3.7 or later

# Use the command tool
To use the command tool:
*	Local operating system configuration python 3 environment.
*	Copy the tool project file to the operating system. 
*	Enter the corresponding command and then press Enter to execute the command.

    `python main.py -H host -p port -U username -P password <command>`


Copyright and License
---------------------

Copyright 2021 New H3C Technologies Co., Ltd.

Licensed under the Apache License, Version 2.0 (the "License"); you may
not use this file except in compliance with the License. You may obtain
a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
License for the specific language governing permissions and limitations
under the License.
