#psql -d $1 < create_tables.sql

# Migrate existing tables
pg_dump -C -t rf_lineup linode_grid25 | psql -d $1
pg_dump -C -t user_concerts linode_grid25 | psql -d $1
pg_dump -C -t tmp_user_genre linode_grid25 | psql -d  $1
pg_dump -C -t rf_event_polygons linode_grid25 | psql -d $1
pg_dump -C -t tmp_user_camp linode_grid25 | psql -d $1
pg_dump -C -t tmp_stage_points linode_grid25 | psql -d $1
pg_dump -C -t derived_countries_visited linode_grid25 | psql -d $1
pg_dump -C -t data_users linode_grid25 | psql -d $1

# Migrate functions
#bash migrate_functions.sh linode_gri255_data1 $1
