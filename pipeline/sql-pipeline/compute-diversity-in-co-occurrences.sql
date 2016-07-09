CREATE OR REPLACE FUNCTION public.__rf_diversity_in_cooccurrences_score(_t varchar)
  RETURNS void
AS
$BODY$
  BEGIN

    EXECUTE 'drop table IF EXISTS tmp_user_diversity_co_occ;';
    EXECUTE 'create table tmp_user_diversity_co_occ as SELECT
                user_a,
                user_b,
                grid_id,
                count(*) AS grid_id_count
              FROM friend_list_common_points a LEFT JOIN data_tracker b ON a.tracker_id_a = b.id
              GROUP BY user_a, user_b, grid_id;';



      EXECUTE 'ALTER TABLE tmp_user_diversity_co_occ drop COLUMN if exists point_diversity;';
      EXECUTE 'ALTER TABLE tmp_user_diversity_co_occ ADD COLUMN point_diversity FLOAT;';
      EXECUTE 'UPDATE tmp_user_diversity_co_occ a
                SET point_diversity = a.grid_id_count :: FLOAT / b.nr_of_occurences :: FLOAT FROM derived_friend_list b
                WHERE a.user_a = b.user_a AND a.user_b = b.user_b;';


      EXECUTE 'ALTER TABLE ' || _t  || ' ADD COLUMN diversity_in_cooccurrences FLOAT;';

      EXECUTE 'UPDATE ' || _t  || ' a
              SET diversity_in_cooccurrences = b.diversity_in_cooccurrences FROM (SELECT
                                                                                    user_a,
                                                                                    user_b,
                                                                                    exp(
                                                                                        diversity_in_cooccurrences) AS diversity_in_cooccurrences
                                                                                  FROM (SELECT
                                                                                          user_a,
                                                                                          user_b,
                                                                                          -sum(point_diversity * log(
                                                                                              point_diversity)) AS diversity_in_cooccurrences
                                                                                        FROM tmp_user_diversity_co_occ
                                                                                        GROUP BY user_a, user_b) d) b
              WHERE a.user_a = b.user_a AND a.user_b = b.user_b';

  END;
$BODY$
LANGUAGE plpgsql VOLATILE;