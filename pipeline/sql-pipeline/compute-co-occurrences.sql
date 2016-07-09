CREATE OR REPLACE FUNCTION public.__rf_add_cooccurrences_features_to_feature_table(_t varchar)
  RETURNS void
AS
$BODY$
  BEGIN
      
      EXECUTE 'drop table IF EXISTS ' || _t  || ';';
      EXECUTE 'create table ' || _t  || ' as select user_a,user_b from derived_friend_list;';
    
      EXECUTE 'ALTER TABLE ' || _t  || ' ADD COLUMN co_occurneces INT;';
    
    
      EXECUTE ' UPDATE ' || _t  || ' a
                SET co_occurneces = b.nr_of_occurences FROM derived_friend_list b
                WHERE a.user_a = b.user_a AND b.user_b = a.user_b;';
    
      EXECUTE ' ALTER TABLE ' || _t  || ' ADD COLUMN co_occurneces_rank INT;';
      EXECUTE ' UPDATE ' || _t  || ' a
                SET co_occurneces_rank = b.rowno FROM derived_friend_list b
                WHERE a.user_a = b.user_a AND b.user_b = a.user_b;';
                
     
       EXECUTE 'ALTER TABLE ' || _t  || ' ADD COLUMN distinct_co_occurneces INT;';
       EXECUTE 'UPDATE ' || _t  || ' an
SET distinct_co_occurneces = b.coun FROM (SELECT
                                            user_a,
                                            user_b,
                                            count(DISTINCT b.grid_id) AS coun
                                          FROM friend_list_common_points a LEFT JOIN
                                            data_tracker b ON a.tracker_id_a = b.id

                                          GROUP BY user_a, user_b
                                          ) b
WHERE b.user_a = an.user_a AND b.user_b = an.user_b;
                ';
     
      
     
  END;
$BODY$
LANGUAGE plpgsql VOLATILE;