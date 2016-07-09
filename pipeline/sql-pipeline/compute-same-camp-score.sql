CREATE OR REPLACE FUNCTION public.__rf_same_camp_score(_t varchar)
  RETURNS void
AS
$BODY$
  BEGIN
     -- Creates the feature same camp score by looking in the table tmp_user_camp, that consists of the most frequent visited camp site.
    EXECUTE 'Alter table ' || _t || ' drop column if exists same_camp_score;';
    EXECUTE 'Alter table ' || _t || ' add column same_camp_score boolean;';

    EXECUTE 'UPDATE ' || _t || ' set same_camp_score=FALSE;';

    EXECUTE 'UPDATE ' || _t || ' AS fr set same_camp_score = TRUE
    where (select title FROM tmp_user_camp WHERE user_id = fr.user_a limit 1) = (select title FROM tmp_user_camp WHERE user_id = fr.user_b limit 1)
    ;';
    END;
$BODY$
LANGUAGE plpgsql VOLATILE;