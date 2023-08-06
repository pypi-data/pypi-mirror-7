"""
MySearch
Copyright (C) 2013   Tuxicoman

This program is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Affero General Public License for more details.
You should have received a copy of the GNU Affero General Public License along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

import os
current_path = os.path.dirname(__file__)
if current_path != "":
  os.chdir(current_path) #set current directory to script folder

from mysearch.mysearch import read_config, save_config, MainPage, config, onion
config_file_path = '/etc/mysearch/mysearch.conf'
read_config(config_file_path, config)
save_config(config_file_path, config)

from twisted.application import internet, service
from twisted.web import server
application = service.Application("MySearch")
if config["relay"] == True:
  mysearch_relay_service = internet.TCPServer(onion.relay_port, onion.RelayServerFactory())
  mysearch_relay_service.setServiceParent(application)
mysearch_service = internet.TCPServer(int(config["bind_port"]), server.Site(MainPage()), interface=config["bind_interface"])
mysearch_service.setServiceParent(application)
