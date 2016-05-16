dpkg -i /root/irods-icat-*-64bit.deb 
dpkg -i /root/irods-database-plugin-postgres-*.deb 

useradd -d /var/lib/irods irods 
su - irods -c "psql -c 'create database \"ICAT\"'"
bash /root/modify_setup_irods.sh
python /var/lib/irods/scripts/setup_irods.py 2> /dev/null 
su - irods -c "irm $(ils|awk 'NR>1{print $0}')"
