from os import path
from dotenv import load_dotenv
load_dotenv()
import paramiko
import getpass
import time
import sys
import os



def ldap_main_function(LDAP_Server_IP, Admin_User, Mgms_Admin_Password, LDAP_Server_Host, LDAP_Container_Name):
    try:

        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(hostname=LDAP_Client_IP, username=Admin_User, password=Mgms_Admin_Password, port=22, look_for_keys=False, allow_agent=False)

        _ldap_server_install_(ssh)

    except Exception as e:
        print('Connection Failed')
        print(e)
        raise Exception("Connection Failed")


def _ldap_server_install_(ssh):
    try:

        # Set Time Zone
        cleanup_zone  = f"echo '{Mgms_Admin_Password}' | sudo -S rm -rf /etc/localtime"
        time_zone  = f"echo '{Mgms_Admin_Password}' | sudo -S ln -s /usr/share/zoneinfo/Europe/Vienna /etc/localtime"

        # Setp 01
        server_main = f"docker run -d --name {LDAP_Container_Name} --restart unless-stopped --network host -e IPA_SERVER_IP={LDAP_Server_IP}"

        # Setp 02
        server_volume_mount = f"-v  /sys/fs/cgroup:/sys/fs/cgroup:ro -v /home/{Admin_User}/.ldap-ipa-data:/data:Z -v /etc/timezone:/etc/timezone:ro -v /etc/localtime:/etc/localtime:ro"

        # Setp 03
        server_cmd_pass = f"-U --domain=r3c.mgms --realm=R3C.MGMS --http-pin={Mgms_Admin_Password} --dirsrv-pin={Mgms_Admin_Password} --ds-password={Mgms_Admin_Password} --admin-password={Mgms_Admin_Password}"

        # Setp 04
        server_cmd = f"--setup-dns --auto-forwarders --auto-reverse --allow-zone-overlap --no-dnssec-validation --ip-address={LDAP_Server_IP} --unattended"


        # Setp 01 + Setp 02 + Setp 03 + Setp 04
        list_cmd = f"mkdir -p /home/{Admin_User}/.ldap-ipa-data;  {server_main} {server_volume_mount} {server_cmd_pass} {server_cmd}"


        # Connect to SSH Shell
        ssh.invoke_shell()
        # SSH Shell Execution
        stdin, stdout, stderr = ssh.exec_command( list_cmd, get_pty=True)
        # Get SSH Shell Output
        output = stdout.readlines()
        # Filter JSon Output
        cmd_logs = (' '.join(map(str, output)))
        print (cmd_logs)

    except Exception as e:
       print(f'Ldap Srver Installation Failed')
       print(e)
       raise Exception("Check Ldap Installation Command")

def _ldap_server_firewall_(ssh):
    try:

        ports = ["80", "443", "389", "636", "88", "464", "7389", "9443", "9444", "9445"]

        for i in ports:

          # Allow Ports
          cmd_tcp = f"ehco '{Mgms_Admin_Password}' | sudo -S ufw allow {i}/tcp"


        ports = ["88", "464", "123"]

        for i in ports:

          # Allow Ports
          cmd_udp = f"ehco '{Mgms_Admin_Password}' | sudo -S ufw allow {i}/udp"

        list_cmd  = f"{cmd_tcp}; { cmd_udp}"

        # Connect to SSH Shell
        ssh.invoke_shell()
        # SSH Shell Execution
        stdin, stdout, stderr = ssh.exec_command( list_cmd, get_pty=True)
        # Get SSH Shell Output
        output = stdout.readlines()
        # Filter JSon Output
        cmd_logs = (' '.join(map(str, output)))
        print (cmd_logs)

    except Exception as e:
       print(f'Ldap Srver Installation Failed')
       print(e)
       raise Exception("Check Ldap Installation Command")




# 1. Main
if __name__=='__main__':
    LDAP_Server_IP         = '0.0.0.0'
    Admin_User             = 'admin'
    Mgms_Admin_Password    = getpass.getpass('admin  Password:')
    LDAP_Server_Host       = 'example.com'
    LDAP_Container_Name    = 'ldap-master01'
    ldap_main_function(LDAP_Server_IP, Admin_User, Mgms_Admin_Password, LDAP_Server_Host, LDAP_Container_Name)
