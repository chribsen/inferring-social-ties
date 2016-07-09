CREATE OR REPLACE FUNCTION public.__rf_setup_indexes()
  RETURNS void
AS
$BODY$
  BEGIN

      -- DATA TRACKER INDEXES
      CREATE INDEX data_tracker_user_id_idx ON data_tracker USING HASH(user_id);
      CREATE INDEX data_tracker_time_id_idx ON data_tracker USING HASH(time_id);
      CREATE INDEX data_tracker_grid_id_idx ON data_tracker USING HASH(grid_id);

      -- DATA TRACKER USER INDEXES
      CREATE INDEX data_users_user_id_idx ON data_users USING hash(id);

      -- DERIVED FRIEND LIST INDEXES
      CREATE INDEX friend_list_user_a_idx ON derived_friend_list USING HASH(user_a);
      CREATE INDEX friend_list_user_b_idx ON derived_friend_list USING HASH(user_b);


  END;
$BODY$
LANGUAGE plpgsql VOLATILE;