CREATE OR REPLACE FUNCTION public.__rf_location_entropy_score(_t varchar)
  RETURNS void
AS
$BODY$
  BEGIN

      EXECUTE 'Alter table friend_list_common_points drop column if exists nr_of_users_in_grid';
      --First find the number of people in each common point
      EXECUTE 'ALTER TABLE friend_list_common_points ADD COLUMN nr_of_users_in_grid INT;
                UPDATE friend_list_common_points
                SET nr_of_users_in_grid = 0;';
      EXECUTE 'UPDATE friend_list_common_points a
                SET nr_of_users_in_grid = d.nr_of_user_in_grid FROM (
                                                                      SELECT
                                                                        tracker_id_a,
                                                                        tracker_id_b,
                                                                        b.grid_id,
                                                                        b.time_id,
                                                                        c.nr_of_user_in_grid
                                                                      FROM friend_list_common_points a LEFT JOIN data_tracker b
                                                                          ON a.tracker_id_a = b.id
                                                                        LEFT JOIN (
                                                                                    SELECT
                                                                                      grid_id,
                                                                                      time_id,
                                                                                      count(*) AS nr_of_user_in_grid
                                                                                    FROM data_tracker
                                                                                    GROUP BY grid_id, time_id
                                                                                  ) c
                                                                          ON b.grid_id = c.grid_id AND b.time_id = c.time_id) d
                WHERE a.tracker_id_a = d.tracker_id_a AND a.tracker_id_b = d.tracker_id_b;';
    EXECUTE 'ALTER TABLE friend_list_common_points DROP COLUMN IF EXISTS entropy';
    EXECUTE 'ALTER TABLE friend_list_common_points ADD COLUMN entropy FLOAT';
    EXECUTE 'UPDATE friend_list_common_points
                SET entropy = (1.0 / nr_of_users_in_grid::float) * log((1.0 / nr_of_users_in_grid::float))';


      --calculate the entropy and save it in the friend feature table

    EXECUTE 'alter table ' || _t || ' drop column if exists location_entropy;';
    EXECUTE 'ALTER TABLE ' || _t || ' ADD COLUMN location_entropy FLOAT;';

    EXECUTE 'UPDATE ' || _t || ' SET location_entropy = 0;';

    EXECUTE 'UPDATE ' || _t || ' a
              SET location_entropy = loc_ent FROM (SELECT
                                                     user_a,
                                                     user_b,
                                                     sum(log(nr_of_users_in_grid)) AS loc_ent
                                                   FROM friend_list_common_points
                                                   GROUP BY user_a, user_b) b
              WHERE a.user_a = b.user_a AND a.user_b = b.user_b;';

  END;
$BODY$
LANGUAGE plpgsql VOLATILE;