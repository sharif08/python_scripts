from os import path
from dotenv import load_dotenv
load_dotenv()
import paramiko
import time
import sys
import os

def ldap_main_function(LDAP_Server_IP, Admin_User, LDAP_Client_IP, LDAP_Client_Host, Mgms_Admin_Password, LDAP_Server_Host):
    try:

        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(hostname=LDAP_Client_IP, username=Admin_User, password=Mgms_Admin_Password, port=22, look_for_keys=False, allow_agent=False)

        _prepare_ldap_client_package_(ssh)
        _ldap_client_install_(ssh)

    except Exception as e:
        print('Connection Failed')
        print(e)
        raise Exception("Connection Failed")


def _prepare_ldap_client_package_(ssh):
    try:

        Host_Domain = (LDAP_Server_Host.rsplit('.', 3)[0])

        # Install Packages
        packages = f"echo '{Mgms_Admin_Password}' | sudo -S apt install resolvconf  realmd oddjob-mkhomedir -y"

        # Add Server Entry to etcd/hosts
        host_entry  = f"echo '{LDAP_Server_IP} {LDAP_Server_Host} {Host_Domain}' | sudo tee -a /etc/hosts"

        # Set Time Zone
        cleanup_zone  = f"echo '{Mgms_Admin_Password}' | sudo -S rm -rf /etc/localtime"
        time_zone  = f"echo '{Mgms_Admin_Password}' | sudo -S ln -s /usr/share/zoneinfo/Europe/Vienna /etc/localtime"

        # Add Server Resolve Conf
        resolve_entry  = f"echo 'nameserver {LDAP_Server_IP}' | sudo tee -a  /etc/resolvconf/resolv.conf.d/tail"

        # Add Login Dir Permission
        pam_entry  = "echo 'session  required     pam_mkhomedir.so skel=/etc/skel umask=0022' | sudo tee -a  /etc/pam.d/common-session"


        list_cmd = f"{packages}; {host_entry}; {cleanup_zone}; {time_zone}; {resolve_entry}; {pam_entry}"

        # Connect to SSH Shell
        ssh.invoke_shell()
        # SSH Shell Execution
        stdin, stdout, stderr = ssh.exec_command( list_cmd, get_pty=True)
        # Get SSH Shell Output
        output = stdout.readlines()
        # Filter JSon Output
        list_cmd_logs = (' '.join(map(str, output)))
        print (list_cmd_logs)

    except Exception as e:
       print(f'Ldap Package Installation Failed')
       print(e)
       raise Exception("Check Package Installation Commands")

def _ldap_client_install_(ssh):
    try:

        Host_Domain = (LDAP_Client_Host.rsplit('.', 3)[0])
        Host_Domain_CN = (LDAP_Client_Host.rsplit('.', 3)[1])
        Host_Domain_Service = (LDAP_Client_Host.rsplit('.', 3)[2])

        Host_FQDN = f'{Host_Domain_CN}.{Host_Domain_Service}'

        print (Host_FQDN)

        # CMD 01
        ldap_server_info = f"--domain={Host_FQDN} --server={LDAP_Server_Host} --realm=R3C.MGMS --principal=admin --password={Mgms_Admin_Password}"

        # CMD 02
        ldap_client_cmd = f"echo '{Mgms_Admin_Password}' | sudo -S ipa-client-install --unattended {ldap_server_info} --mkhomedir  --hostname={LDAP_Client_Host} -N"

        # CMD 02
        reset_hostname_cmd = f"echo '{Mgms_Admin_Password}' | sudo  -S hostnamectl set-hostname {Host_Domain} "

        cmd_list = f"{ldap_client_cmd}; {reset_hostname_cmd}"

        # Connect to SSH Shell
        ssh.invoke_shell()
        # SSH Shell Execution
        stdin, stdout, stderr = ssh.exec_command( cmd_list, get_pty=True)
        # Get SSH Shell Output
        output = stdout.readlines()
        # Filter JSon Output
        cmd_logs = (' '.join(map(str, output)))
        print (cmd_logs)

    except Exception as e:
       print(f'Ldap Client Installation Failed')
       print(e)
       raise Exception("Check Ldap Installation Commands")



# 1. Main
if __name__=='__main__':
    LDAP_Server_IP         = os.environ.get('ldap_server_ip')
    Admin_User             = os.environ.get('mgms_admin')
    LDAP_Client_IP         = os.environ.get('ldap_client_ip')
    LDAP_Client_Host       = os.environ.get('ldap_client_hostname')
    Mgms_Admin_Password    = os.environ.get('admin_pass')
    LDAP_Server_Host       = os.environ.get('ldap_server_hostname')
    ldap_main_function(LDAP_Server_IP, Admin_User, LDAP_Client_IP, LDAP_Client_Host, Mgms_Admin_Password, LDAP_Server_Host)
