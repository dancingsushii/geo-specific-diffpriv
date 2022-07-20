# PostGIS Setup

These instructions are written to help you configure PostgreSQL and PostGIS in order to be able to use our proxy. The commands below were written and tested in a GCP intance running OS Ubuntu 20.04 LTS.

## Install PostgreSQL 13 and PostGIs 3

1. Install required dependency packages:
```
sudo apt update && sudo apt install curl gpg gnupg2 software-properties-common apt-transport-https lsb-release
```
2. Add the APT repository required to pull the packages form the PostgreSQL repository, and add repository contents to your Ubuntu 20.04 system:
```
curl -fsSL https://www.postgresql.org/media/keys/ACCC4CF8.asc|sudo gpg --dearmor -o /etc/apt/trusted.gpg.d/postgresql.gpg
echo "deb http://apt.postgresql.org/pub/repos/apt/ `lsb_release -cs`-pgdg main" |sudo tee  /etc/apt/sources.list.d/pgdg.list
```
3. Install PostgresSQL 13 packages:
```
sudo apt update && sudo apt install postgresql-13 postgresql-client-13
```
4. Check that the PostgreSQL service is active:
```
systemctl status postgresql@13-main.service
```
5. Install PostGIS 3:
```
udo apt update && sudo apt-get install -y postgis postgresql-13-postgis-3
```
6. Enable PostGIS extension for your database (the database should exist already):
```
sudo -u postgres psql -c "CREATE EXTENSION postgis; CREATE EXTENSION postgis_topology;" your-database
```

## Allow external access to PostgreSQL

1. Open PostgreSQL configuration file:
```
sudo nano /etc/postgresql/13/main/postgresql.conf
```
2. Look for this line in the file " #listen_addresses = 'localhost' ", uncomment the line and change the value to '*', then save and exit the file:
```
listen_addresses = '*'
```
3. Open the file pg_hba.conf to modify it to allow connections from your public IP addresses:
```
sudo nano /etc/postgresql/13/main/pg_hba.conf
```
4. Scroll down to the bottom of the file and add the following lines, then save and exit the file: 
```
# IPv4 remote connections for PostgreSQL
host  all   all your-public-ip/32 md5
```
5. Restart Postgres to apply all the changes you have made to its configuration by running:
```
sudo service postgresql restart
```

# How to create PostGIS DB, tables and upload the needed datasets

## Create PostGIS database

1. Connect to postgres from your host/VM:
```
sudo -u postgres psql
```
2. Create database named 'geodp':
```
CREATE DATABASE geodp;
```
3. Connect to the geodp database:
```
\connect geodp
```

## Create PostGIS tables and upload dataset contents

We created three different table sizes (smalldata, mediumdata,bigdata) and we three different datasets:

1. Create tables:
```
CREATE TABLE smalldata ( id int4 primary key, date date, county varchar(50), state varchar(50), zipcode numeric, cases numeric, deaths numeric, stayhomea boolean, stayhomee boolean,  geom geometry(POINT,4326) );
CREATE TABLE mediumdata ( id int4 primary key, date date, county varchar(50), state varchar(50), zipcode numeric, cases numeric, deaths numeric, stayhomea boolean, stayhomee boolean,  geom geometry(POINT,4326) );
CREATE TABLE bigdata ( id int4 primary key, date date, county varchar(50), state varchar(50), zipcode numeric, cases numeric, deaths numeric, stayhomea boolean, stayhomee boolean,  geom geometry(POINT,4326) );
```
2. Download the [datasets](https://github.com/dancingsushii/geo-specific-diffpriv/tree/main/dataset) to the host/VM where you installed postgis, if you host/VM is hosted in GCP, you can use the following command:
```
gcloud compute scp your-local-path-to-dataset-file your-username@your-vm-name:~
```
3. In PostGIS, copy the contents of the dataset files to the tables we created:
```
COPY smalldata FROM '$HOME/big-dataset-covid19-us.csv' DELIMITERS ',' CSV HEADER;
COPY mediumdata FROM '$HOME/big-dataset-covid19-us.csv' DELIMITERS ',' CSV HEADER;
COPY bigdata FROM '$HOME/big-dataset-covid19-us.csv' DELIMITERS ',' CSV HEADER;
```

## Update your PostGIS server details
1. Change the values of your PostGIS server IP address and creds under the function: "db_conn()" in the script [dp.py](https://github.com/dancingsushii/geo-specific-diffpriv/blob/main/dp.py)
