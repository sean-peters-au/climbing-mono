#!/bin/bash

# Exit on any error
set -e

echo "Warning: This will delete all data in the local database!"
read -p "Are you sure you want to continue? (yes/no): " response

if [ "$response" = "yes" ]; then
    PGPASSWORD=postgres psql -h localhost -U postgres -d postgres -c "
        DO \$\$ 
        DECLARE
            r RECORD;
        BEGIN
            FOR r IN (SELECT tablename FROM pg_tables WHERE schemaname = 'public' AND tablename != 'alembic_version') 
            LOOP
                EXECUTE 'TRUNCATE TABLE ' || quote_ident(r.tablename) || ' CASCADE';
            END LOOP;
        END \$\$;
    "
    echo "Database data cleared successfully"
else
    echo "Operation cancelled"
fi