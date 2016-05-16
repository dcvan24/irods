dpkg -P irods-database-plugin-postgres
dpkg -P irods-icat
err=$(userdel -r irods 2>&1)
if [ "$err" ];then
    kill -9 $(echo $err|awk '{print $NF}')
    userdel -r irods
fi
rm -rf /etc/irods
su - postgres -c "psql -c 'DROP DATABASE \"ICAT\"'"
