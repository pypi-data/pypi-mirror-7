"""ResourceSync client state class

The client requires memory of state to support incremental
synchronization. At minimum it must store the source timestamp
of the last change seen.
"""

import sys
import urllib
import urlparse
import os.path
import datetime
import distutils.dir_util 
import re
import time
import logging
import ConfigParser


class ClientState(object):
    """
    """

    def __init__(self):
        self.status_file = '.resync-client-status.cfg'

    def set_state(self,site,timestamp=None):
        """Write status dict to client status file
        
        FIXME - should have some file lock to avoid race
        """
        parser = ConfigParser.SafeConfigParser()
        parser.read(self.status_file)
        status_section = 'incremental'
        if (not parser.has_section(status_section)):
            parser.add_section(status_section)
        if (timestamp is None):
            parser.remove_option(status_section, self.config_site_to_name(site))
        else:
            parser.set(status_section, self.config_site_to_name(site), str(timestamp))
        with open(self.status_file, 'wb') as configfile:
            parser.write(configfile)
            configfile.close()

    def get_state(self,site):
        """Read client status file and return dict"""
        parser = ConfigParser.SafeConfigParser()
        status_section = 'incremental'
        parser.read(self.status_file)
        timestamp = None
        try:
            timestamp = float(parser.get(status_section,self.config_site_to_name(site)))
        except ConfigParser.NoSectionError as e:
            pass
        except ConfigParser.NoOptionError as e:
            pass
        return(timestamp)

    def config_site_to_name(self, name):
        return( re.sub(r"[^\w]",'_',name) )
