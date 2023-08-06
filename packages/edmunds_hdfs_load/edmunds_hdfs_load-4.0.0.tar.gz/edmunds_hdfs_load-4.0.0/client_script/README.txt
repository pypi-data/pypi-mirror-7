*********PYTHON SCRIPT TO LOAD LOCAL CSVs TO HIVE************


REQUIREMENTS:
1. You must either be using Mac, Linux or a Windows box with Cygwin installed.
2. If using windows, you MUST run the python script on your Cygwin version of python
3. You must have an LDAP account with access to one of the production hadoop clusters (i.e. pl1rhd402.internal.edmunds.com)
4. Unless you want to type in your password constantly, you should set up RSA authentification. Follow this tutorial:
http://www.linuxproblem.org/art_9.html

HOW TO RUN:
1. First create a configuration file using the sample config as a template.
	a. You Must change the server, username and password fields under RemotePaths
	b. You must change the delimiter to correspond to that which is used in your .csv files which you are going to process
	c. The missing value should correspond to what represents missing values (as opposed to blank values) in your .csv. These will be converted to NULL values in Hive
	d. The table prefix to be used in front of the table name. Unless told otherwise, use 'm_'
	e. The drop table flag should only be used if you wish to drop the table AND all of its partitions. The default should be false.
2. To run the script you will do:
	python create_hive_client.py path/to/your/configuration/file path/to/your/table1.csv path/to/your/table2.csv ... path/to/your/tableN.csv
	You may specify as many or as few tables as you would like. But obviously nothing will happen unless you specify at least one table.

ASSUMPTIONS:
1. A Partition will be created based on the date that you upload the data to the granularity of a day.
2. If you reload the same table more than once a day, that partition will be overwritten. Thus at most you can only have historical data per a day.
3. Data types will be assigned into the current available hive categories: STRING, BIGINT, FLOAT. Timestamps will not be inferred, 
if you would like timestamps for your columns you will need to create the hive table manually before loading the data.