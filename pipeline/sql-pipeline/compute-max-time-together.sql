CREATE OR REPLACE FUNCTION public.__rf_max_time_consecutive_grid_score(_t varchar)
  RETURNS void
AS
$BODY$
  BEGIN


      --calculate the entropy and save it in the friend feature table
      EXECUTE 'ALTER TABLE ' || _t  || ' DROP COLUMN IF EXISTS max_time_consecutive_grid;';
      EXECUTE 'ALTER TABLE ' || _t  || ' ADD COLUMN max_time_consecutive_grid INT;';
      EXECUTE 'UPDATE ' || _t  || '
                SET max_time_consecutive_grid = 0;
                ';

      EXECUTE 'UPDATE ' || _t  || ' a
                SET max_time_consecutive_grid = b.time_spent FROM (
                                                                    SELECT
                                                                      user_a,
                                                                      user_b,
                                                                      max(time_spent) AS time_spent
                                                                    FROM (
                                                                           SELECT
                                                                             consecutive_grid_id,
                                                                             b.user_id       AS user_a,
                                                                             c.user_id       AS user_b,
                                                                             count(*),
                                                                             max(b.c_time),
                                                                             min(b.c_time),
                                                                             EXTRACT(EPOCH FROM (Max(b.c_time) - min(
                                                                                 b.c_time))) AS time_spent
                                                                           FROM derived_consecutive_grids a LEFT JOIN
                                                                             data_tracker b ON a.tracker_id_a = b.id
                                                                             LEFT JOIN
                                                                             data_tracker c ON a.tracker_id_b = c.ID
                                                                           GROUP BY consecutive_grid_id, b.user_id, c.user_id
                                                                         ) a
                                                                    GROUP BY user_a, user_b) b
                WHERE a.user_a = b.user_a AND a.user_b = b.user_b;';

  END;
$BODY$
LANGUAGE plpgsql VOLATILE;