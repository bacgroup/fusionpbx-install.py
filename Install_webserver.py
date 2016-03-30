import subprocess
import os
import pwd
import grp
import sys
import FPBXParms


def iwebserver():
    retcode = 0
    INSTALL_ROOT = os.getcwd()
    if os.path.isfile("%s/resources/install.json" % (INSTALL_ROOT)):
        FPBXParms.PARMS = FPBXParms.load_parms(FPBXParms.PARMS)
    else:
        print("Error no install parameters")  
        sys.exit(1) 
                   
    #=============================================================================== 
    # We need a web server for FusionPBX
    #=============================================================================== 
    
    if FPBXParms.PARMS["WebServer"][0] == "a":
        ws = "Apache2"
    if FPBXParms.PARMS["WebServer"][0] == "N":
        ws = "nginx"
    print("Installing %s for our Webserver " % (ws))
    if FPBXParms.PARMS["WebServer"][0] == "a":
        subprocess.call("apt-get -y install apache2", stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, shell=True)
    elif FPBXParms.PARMS["WebServer"][0] == "N":
        # apache2 may have been installed as a dependency for another package
        # Shutdown and disable apache2
        subprocess.call("systemctl --quiet disable apache2", stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, shell=True)
        subprocess.call("systemctl --quiet stop apache2", stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, shell=True)
        subprocess.call("apt-get -y remove apache2 apache2-mpm-prefork apache2-utils apache2.2-bin apache2.2-common libapache2-mod-php5 libapr1 libaprutil1 libaprutil1-dbd-sqlite3 libaprutil1-ldap", stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, shell=True)
        subprocess.call("apt-get -y install nginx", stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, shell=True)
    else:
        print("No Web Server was defined, FusionPBX will not operate with out a Web Server")
        sys.exit(6)
    #TODO: Do we need this code? 
    if not os.path.isfile("/usr/sbin/ppa-purge"):
        subprocess.call("/usr/bin/wget -O /var/cache/apt/archives/ppa-purge_0+bzr46.1~lucid1_all.deb http://us.archive.ubuntu.com/ubuntu/pool/universe/p/ppa-purge/ppa-purge_0+bzr46.1~lucid1_all.deb", stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, shell=True)
        subprocess.call("/usr/bin/dpkg -i /var/cache/apt/archives/ppa-purge_0+bzr46.1~lucid1_all.deb", stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, shell=True)
    
    #=============================================================================== 
    # www-data needs to own all of Freeswitch
    #=============================================================================== 
    
    print("Setting access on Freeswitch for FusionPBX")
    if os.path.isfile("/usr/bin/freeswitch"):
        subprocess.call("systemctl stop freeswitch", stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, shell=True)
        paths = ["/usr/lib/freeswitch", "/usr/share/freeswitch", "/etc/freeswitch"]
        for path in paths:
            for root, dirs, files in os.walk(path):  
                for directory in dirs:  
                    ret = subprocess.call("setfacl -R -m u:www-data:rwx,g:www-data:rwx %s" % (os.path.join(root, directory)), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, shell=True)
                    FPBXParms.check_ret(ret, "Setting user acl for %s" % (os.path.join(root, directory)))
                    ret = subprocess.call("setfacl -R -d -m u:www-data:rwx,g:www-data:rwx %s" % (os.path.join(root, directory)), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, shell=True)
                    FPBXParms.check_ret(ret, "Setting user acl for %s" % (os.path.join(root, directory)))                    
                for filename in files:
                    ret = subprocess.call("setfacl -R -m u:www-data:rwx,g:www-data:rwx %s" % (os.path.join(root, filename)), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, shell=True)
                    FPBXParms.check_ret(ret, "Setting user acl for %s" % (os.path.join(root, filename)))                    
                    ret = subprocess.call("setfacl -R -d -m u:www-data:rwx,g:www-data:rwx %s" % (os.path.join(root, filename)), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, shell=True)
                    FPBXParms.check_ret(ret, "Setting user acl for %s" % (os.path.join(root, filename)))                    
        subprocess.call("systemctl start freeswitch", stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, shell=True)
    else:
        print("Freeswitch is not installed on this system")
        sys.exit(5)    
    
    return retcode