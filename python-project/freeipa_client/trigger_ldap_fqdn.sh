#!/bin/bash


# Env Entry
read -s -p  "Enter the 'mgms-admin' Admin Password: "  pswd
echo '\n'
read -e -p  "Enter the New Client IP: " client_ip
read -e -p  "Enter the New Client HostName: " client_hostname



# Login User Info
export mgms_admin='mgms-admin'
export admin_pass=$pswd

# Ldap Client Info
export ldap_client_hostname=$client_hostname
export ldap_client_ip=$client_ip


# Ldap Server Info based on Vlan
vlan=$(echo $client_ip | awk -F'.' '{print $3}')

if [ $vlan == '10' ]; then

   export ldap_server_container_name='ldap-master01'
   export ldap_server_ip='0.0.0.0'
   export ldap_server_hostname='vie01-freeipa01.r3c.mgms'

elif [ $vlan == '11' ]; then

   export ldap_server_container_name='ldap-master01'
   export ldap_server_ip='0.0.0.0'
   export ldap_server_hostname='vie01-freeipa01.r3c.mgms'

elif [ $vlan == '15' ]; then

   export ldap_server_container_name='ldap-master01'
   export ldap_server_ip='0.0.0.0'
   export ldap_server_hostname='vie01-freeipa01.r3c.mgms'

fi


# Check Dry run before excute python Secripts
status_check=$(sshpass -p "$admin_pass" ssh  -o LogLevel=QUIET  -t $mgms_admin@$client_ip 'cat /etc/resolvconf/resolv.conf.d/tail' | awk 'NR==1 {print $1}')


if [[ "$status_check" == "nameserver" ]]; then

   echo "LDAP Client FQDN Already Exists in LDAO Server, Try to Uninstall 'sudo ipa-client-install --uninstall' and remove hostservice entry from LDAP Server GUI"
   exit

else
   #Setp:1 Prepare Ldap Client on Server Host
   python3 $PWD/ldap_client_config.py

   #Setp:2  Ldap Client Installation
   python3 $PWD/ldap_client_install.py
fi
