setup_script=/var/lib/irods/scripts/setup_irods.py

replace_prompt(){
    sed -i "s/\(\t*$1.*$2.*=\).*/\1 $3/g" $setup_script
}

delete_trailing_lines(){
    sed -i "/$1/, +$2d" $setup_script
}

# modify iRODS user and group
sed -i "s/default_prompt('iRODS user'.*/'irods'/g" $setup_script 
sed -i "s/default_prompt('iRODS group'.*/'irods'/g" $setup_script

# modify DB info
replace_prompt 'db_config' 'db_odbc_driver' "'PostgreSQL Unicode'"
delete_trailing_lines "'ODBC driver for %s'" 1
delete_trailing_lines "No default ODBC drivers configured for" 2

replace_prompt 'db_config' 'db_host' "'localhost'"
delete_trailing_lines "'Database server.'s hostname or IP address'" 1

replace_prompt 'db_config' 'db_port' 5432
delete_trailing_lines "'Database server.'s port'" 2

replace_prompt 'db_config' 'db_name' "'ICAT'"
delete_trailing_lines "'Database name'" 1
delete_trailing_lines "'Service name'" 1

replace_prompt 'db_config' 'db_username' "'irods'"
delete_trailing_lines "'Database username'" 1

replace_prompt 'db_config' 'db_password' "'test'"
delete_trailing_lines "'Database password'" 1

sed -i "s/\(.*db_password_salt = \).*/\1 'test'/g" $setup_script
delete_trailing_lines "'Salt for passwords stored in the database'" 1

# modify iCAT server info
replace_prompt 'server_config' 'icat_host' "'icat'"
delete_trailing_lines 'iRODS catalog (ICAT) host' 2

replace_prompt 'server_config' 'zone_name' "'tempZone'"
delete_trailing_lines 'iRODS.*zone name.*' 3

replace_prompt 'server_config' 'zone_port' 1247
delete_trailing_lines "'iRODS server.'s port'" 3

replace_prompt 'server_config' 'server_port_range_start' 20000
delete_trailing_lines "'iRODS port range (begin)'" 2

replace_prompt 'server_config' 'server_port_range_end' 20199
delete_trailing_lines "'iRODS port range (end)'" 2

replace_prompt 'server_config' 'server_control_plane_port' 1248
delete_trailing_lines "'Control Plane port'" 2

replace_prompt 'server_config' 'schema_validation_base_uri' "'https:\/\/schemas.irods.org\/configuration'"
delete_trailing_lines "'Schema Validation Base URI (or off)'" 2

replace_prompt 'server_config' 'zone_user' "'irods'"
delete_trailing_lines "'iRODS server.'s administrator username'" 2

sed -i '/if default_prompt(confirmation_message,/{n;d}' $setup_script
sed -i 's/if default_prompt(confirmation_message,.*$/break/g' $setup_script

replace_prompt 'server_config' 'zone_key' "'TEMPORARY_zone_key'"
delete_trailing_lines "'iRODS server.'s zone key'" 2

replace_prompt 'server_config' 'negotiation_key' "'TEMPORARY_32byte_negotiation_key'"
delete_trailing_lines "'iRODS server.'s negotiation key (32 characters)'" 2

replace_prompt 'server_config' 'server_control_plane_key' "'TEMPORARY__32byte_ctrl_plane_key'"
delete_trailing_lines "'Control Plane key (32 characters)'" 2

sed -i "s/\(.*default_resource_directory = \).*/\1 '\/var\/lib\/irods\/iRODS\/Vault'/g" $setup_script
delete_trailing_lines "'iRODS Vault directory'" 1

sed -i "s/\(irods_config.admin_password = \).*/\1 'test'/g" $setup_script 
delete_trailing_lines "'iRODS server.'s administrator password'" 2

