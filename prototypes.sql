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