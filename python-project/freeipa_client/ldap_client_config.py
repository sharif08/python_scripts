from os import path
from dotenv import load_dotenv
load_dotenv()
import paramiko
import base64
import time
import sys
import os



def ldap_main_function(LDAP_Server_IP, Admin_User, LDAP_Client_IP, LDAP_Client_Host, Mgms_Admin_Password, LDAP_Server_Contianer_Name):
    try:

        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(hostname=LDAP_Server_IP, username=Admin_User, password=Mgms_Admin_Password, port=22, look_for_keys=False, allow_agent=False)

        _prepare_ldap_server_Login_(ssh)

        get_dryrun_status = _prepare_ldap_server_dryrun_(ssh)

        print (get_dryrun_status)
        if get_dryrun_status:

            # Run this function to add new FQDN
            _ldap_server_add_client_fqdn_(ssh)

        else:
            print ('LDAP Client FQDN Already Exists in LDAO Server')
            exit

    except Exception as e:
        print('Connection Failed')
        print(e)
        raise Exception("Check SSH Connection User/Pass")


def _prepare_ldap_server_Login_(ssh):
    try:

        # # Login the Docker Ldap Container
        LDAP_Server_Login = f"docker exec -ti {LDAP_Server_Contianer_Name} bash -c 'echo {Mgms_Admin_Password} | kinit admin'"

        # Connect to SSH Shell
        ssh.invoke_shell()
        # SSH Shell Execution
        stdin, stdout, stderr = ssh.exec_command( LDAP_Server_Login, get_pty=True)
        # Get SSH Shell Output
        output = stdout.readlines()
        # Filter JSon Output
        Login_logs = (' '.join(map(str, output)))
        print (Login_logs)

    except Exception as e:
       print(f'Container Login Failed Check Admin Pass or Container Name')
       print(e)
       raise Exception("Container Login Failead")


def _prepare_ldap_server_dryrun_(ssh):
    try:

        Host_Domain = (LDAP_Client_Host.rsplit('.', 3)[0])
        Host_Domain_CN = (LDAP_Client_Host.rsplit('.', 3)[1])
        Host_Domain_Service = (LDAP_Client_Host.rsplit('.', 3)[2])

        # Get Ldap Server RealM
        Host_Domain_Realm = f'{Host_Domain_CN}.{Host_Domain_Service}'

        # # LDAP Server Entry dry run
        LDAP_Server_Entry_Check = f"docker exec -ti {LDAP_Server_Contianer_Name} bash -c 'ipa dnsrecord-find {Host_Domain_Realm} --name={Host_Domain}'"

        # Connect to SSH Shell
        ssh.invoke_shell()
        # SSH Shell Execution
        stdin, stdout, stderr = ssh.exec_command( LDAP_Server_Entry_Check, get_pty=True)
        # Get SSH Shell Output
        output = stdout.readlines()
        # Filter JSon Output
        Check_logs = (' '.join(map(str, output)))
        Filtr_Check_logs = (Check_logs.rsplit(' ', 3)[2])

        return (Filtr_Check_logs)

    except Exception as e:
       print(f'Dry run Failed')
       print(e)
       raise Exception("Check the Domail Realm")


def _ldap_server_add_client_fqdn_(ssh):
    try:
        # Revert the Ldap Client IP Order
        # Set the Variable for reverse zone
        IP_Order1 = (LDAP_Client_IP.rsplit('.', 3)[3])
        IP_Order2 = (LDAP_Client_IP.rsplit('.', 3)[2])
        IP_Order3 = (LDAP_Client_IP.rsplit('.', 3)[1])
        IP_Order4 = (LDAP_Client_IP.rsplit('.', 3)[0])

        IP_Order = f'{IP_Order2}.{IP_Order3}.{IP_Order4}.in-addr.arpa'

        Host_Domain_CN = (LDAP_Client_Host.rsplit('.', 3)[1])
        Host_Domain_Service = (LDAP_Client_Host.rsplit('.', 3)[2])

        # # Add New Client LDAP Entry
        Add_Client_FQDN_A = f"docker exec -ti {LDAP_Server_Contianer_Name} bash -c 'ipa dnsrecord-add {Host_Domain_CN}.{Host_Domain_Service} {IP_Order1} --a-rec {LDAP_Client_IP}'"

        Add_Client_FQDN_PTR = f"docker exec -ti {LDAP_Server_Contianer_Name} bash -c 'ipa dnsrecord-add {IP_Order} {IP_Order1} --ptr-rec {LDAP_Client_Host}'"



        # # Add New Client LDAP Entry to Host Service
        #Add_Client_Host = f"docker exec -ti {LDAP_Server_Contianer_Name} bash -c 'ipa service-add-host --hosts={LDAP_Client_Host}  HTTP/{LDAP_Client_Host}'"

        Mutil_commands = f"{Add_Client_FQDN_A}; {Add_Client_FQDN_PTR}"

        # Connect to SSH Shell
        ssh.invoke_shell()
        # SSH Shell Execution
        stdin, stdout, stderr = ssh.exec_command( Mutil_commands, get_pty=True)
        # Get SSH Shell Output
        output = stdout.readlines()
        # Filter JSon Output
        Add_logs = (' '.join(map(str, output)))
        print (Add_logs)

    except Exception as e:
       print(f'Add DNS Record Failed')
       print(e)
       raise Exception("Check Clent FQDN with Server Realm")


# 1. Main
if __name__=='__main__':
    LDAP_Server_IP              = os.environ.get('ldap_server_ip')
    Admin_User                  = os.environ.get('mgms-admin')
    LDAP_Client_IP              = os.environ.get('ldap_client_ip')
    LDAP_Client_Host            = os.environ.get('ldap_client_hostname')
    Mgms_Admin_Password         = os.environ.get('admin_pass')
    LDAP_Server_Contianer_Name  = os.environ.get('ldap_server_container_name')
    ldap_main_function(LDAP_Server_IP, Admin_User, LDAP_Client_IP, LDAP_Client_Host, Mgms_Admin_Password, LDAP_Server_Contianer_Name)
