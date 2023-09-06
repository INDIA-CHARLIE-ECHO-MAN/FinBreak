/*SELECT distinct DATE_PART('year', transDate) from transaction*/


DROP FUNCTION get_amount_month();


CREATE OR REPLACE FUNCTION get_amount_month()
RETURNS TABLE (
    id INT,
    transDate date,
	
	finAmount float
)
AS $$
DECLARE
    result_row record;
	year_row int;
BEGIN
	FOR year_row in select distinct DATE_PART('year', t.transDate) as year 
		from transaction t
		order by year 
		
	LOOP
		raise notice 'year: %', year_row;
		
		    FOR counter IN 1..12 LOOP
			SELECT *
			FROM transaction t
			WHERE DATE_PART('month', t.transDate) = counter and DATE_PART('year', t.transDate) = year_row
			ORDER BY t.transDate DESC, id 
			LIMIT 1
			INTO result_row;

			IF FOUND THEN
				-- Return the result_row
				RETURN query select result_row.id, result_row.transDate, result_row.finAmount;
			END IF;
			END LOOP;
		
	END LOOP;
	/*

    */
    RETURN;
END;
$$ LANGUAGE plpgsql;

SELECT * FROM get_amount_month();



/*
DROP FUNCTION get_amount_month();


CREATE OR REPLACE FUNCTION get_amount_month()
RETURNS TABLE (
    id INT,
    transDate date,
	finAmount float
)
AS $$
DECLARE
    result_row record;
BEGIN
    FOR counter IN 1..12 LOOP
        SELECT *
        FROM transaction t
        WHERE DATE_PART('month', t.transDate) = counter
        ORDER BY t.transDate DESC, id 
        LIMIT 1
		INTO result_row;
        
        IF FOUND THEN
            -- Return the result_row
            RETURN query select result_row.id, result_row.transDate, result_row.finAmount;
        END IF;
    END LOOP;
    
    RETURN;
END;
$$ LANGUAGE plpgsql;

SELECT * FROM get_amount_month();
*/

