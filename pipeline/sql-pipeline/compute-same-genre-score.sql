CREATE OR REPLACE FUNCTION public.__rf_same_genre_score(_t varchar)
  RETURNS void
AS
$BODY$
  BEGIN

      EXECUTE 'Alter table ' || _t  || ' drop column if exists same_genre_score;';
      EXECUTE 'Alter table ' || _t  || ' add column same_genre_score boolean;';

      EXECUTE 'UPDATE ' || _t  || ' set same_genre_score=FALSE;';
      EXECUTE 'UPDATE ' || _t || ' AS fr set same_genre_score = TRUE where (select itunes_genre FROM tmp_user_genre  WHERE user_id = fr.user_a limit 1) = (select itunes_genre FROM tmp_user_genre WHERE user_id = fr.user_b limit 1);';

  END;
$BODY$
LANGUAGE plpgsql VOLATILE;