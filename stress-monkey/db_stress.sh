#!/bin/bash

# Replace these with your actual MySQL database details
DB_HOST="your-db-host"
DB_USER="your-db-user"
DB_PASSWORD="your-db-password"
DB_NAME="todo_db"

# Sysbench commands for MySQL

# Prepare the database for stress testing
sysbench /usr/share/sysbench/oltp_read_write.lua --mysql-host=$DB_HOST --mysql-user=$DB_USER --mysql-password=$DB_PASSWORD --mysql-db=$DB_NAME --table-size=100000 --tables=10 prepare

# Run the stress test with 10 threads for 60 seconds
sysbench /usr/share/sysbench/oltp_read_write.lua --mysql-host=$DB_HOST --mysql-user=$DB_USER --mysql-password=$DB_PASSWORD --mysql-db=$DB_NAME --table-size=100000 --tables=10 --threads=10 --time=60 run

# Clean up the database after stress testing
sysbench /usr/share/sysbench/oltp_read_write.lua --mysql-host=$DB_HOST --mysql-user=$DB_USER --mysql-password=$DB_PASSWORD --mysql-db=$DB_NAME cleanup
