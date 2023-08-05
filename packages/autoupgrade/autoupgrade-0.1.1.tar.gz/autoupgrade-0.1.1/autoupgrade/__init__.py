import urllib
from bs4 import BeautifulSoup
import re
import pkg_resources
from os import execl, environ
from sys import executable, argv
import pip

class PkgNotFoundError(Exception):
    """No package found"""

class NoVersionsError(Exception):
    """No versions found for package"""
    
def normalize_version(v):
    """Helper function to normalize version
    Returns a comparable object
    Args:
        v (str) version, e.g. "0.1.0"
    
    """
    return [int(x) for x in v.split(".")]

class AutoUpgrade(object):
    """AutoUpgrade class, holds one package
    """
    
    def __init__(self, pkg, index = None):
        """Args:
                pkg (str): name of package
                index (str): alternative index, if not given https://pypi.python.org will be used"""
        self.pkg = pkg
        if index:
            self.index = index
            self.index_set = True
        else:
            self.index = "https://pypi.python.org/" 
            self.index_set = False
        
    def upgrade_if_needed(self, restart = True, dependencies = False):
        """ Upgrade the package if there is a later version available.
            Args:
                restart, restart app if True
                dependencies, update dependencies if True (see pip --no-deps)
        """
        if self.check():
            print "Upgrading %s" % self.pkg
            self.upgrade(dependencies)
            if restart:
                self.restart()
            
    def upgrade(self, dependencies = False):
        """ Upgrade the package unconditionaly
            Args:
                dependencies, update dependencies if True (see pip --no-deps)
        """
        pip_args = [ '-vvv' ]
        proxy = environ.get('http_proxy')
        if proxy:
            pip_args.append('--proxy')
            pip_args.append(proxy)
        pip_args.append('install')
        pip_args.append(self.pkg)
        if self.index_set:
            pip_args.append('-i')
            pip_args.append("{}/simple/".format(self.index))
        if not dependencies:
            pip_args.append("--no-deps")
        if self._get_current() != [-1]:
            pip_args.append("--upgrade")
        a=pip.main(initial_args = pip_args)
        print a
        return a
        
    def restart(self):
        """ Restart application with same args as it was started.
            Does **not** return
        """
        print "Restarting " + executable + " " + str(argv) 
        execl(executable, *([executable]+argv))
        
    def check(self):
        """ Check if pkg has a later version
            Returns true if later version exists.
        """
        current = self._get_current()
        highest = self._get_highest_version()
        return highest > current 
    
    def _get_current(self):
        try:
            current = normalize_version(pkg_resources.get_distribution(self.pkg).version)
        except pkg_resources.DistributionNotFound:
            current = [-1]
        return current
    
    def _get_highest_version(self):
        url = "{}/simple/{}/".format(self.index, self.pkg)
        try:
            html = urllib.urlopen(url)
        except IOError:
            print "Could not connect to %s" % url
            return [-1]
        if html.getcode() != 200:
            raise PkgNotFoundError
        soup = BeautifulSoup(html.read())
        versions = []
        for link in soup.find_all('a'):
            text = link.get_text()
            try:
                version = re.search( self.pkg + '-(.*)\.tar\.gz', text).group(1)
                versions.append(normalize_version(version))
            except AttributeError:
                pass
        if len(versions) == 0:
            raise NoVersionsError()
        return max(versions)
