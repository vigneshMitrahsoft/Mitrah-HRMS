CREATE OR REPLACE FUNCTION public.fn_get_employee_attendance(
	employee_id integer,
	month integer,
	year integer)
    RETURNS TABLE(
		date_value date,
		day_of_week character varying,
		is_week_off boolean,
		attendance_status character varying,
		leave_status character varying,
		check_in timestamp with time zone,
		check_out timestamp with time zone,
		effective_hours time without time zone,
		total_hours time without time zone
	) 
    LANGUAGE 'plpgsql'
    COST 100
    VOLATILE PARALLEL UNSAFE
    ROWS 1000

AS $$
DECLARE
    start_date DATE;
    end_date DATE;
BEGIN
    start_date := DATE_TRUNC('MONTH', TO_DATE(year || '-' || month || '-01', 'YYYY-MM-DD'));
    end_date := (start_date + INTERVAL '1 MONTH' - INTERVAL '1 day')::DATE;
    
    RETURN QUERY
    WITH CET_Dates AS (
        SELECT generate_series(start_date, end_date, '1 day'::INTERVAL)::DATE AS DateValue
    )
    SELECT 
        dat.DateValue AS date,
		--DAY(dat.DateValue) AS day_of_date,
		TO_CHAR(dat.DateValue, 'FMDay')::VARCHAR AS day_of_week,
		CASE
			WHEN TO_CHAR(dat.DateValue, 'FMDay')::VARCHAR IN('Saturday', 'Sunday')
			THEN True
			ELSE False
		END AS is_week_off,
        coalesce(attendance_info.status,'') AS attendance_status,
        coalesce(leave.status,'') AS leave_status,
		ea.check_in AS check_in,
		ea.check_out AS check_out,
		coalesce(ea.effective_hours,'00:00:00') AS effective_hours,
		coalesce(ea.total_hours,'00:00:00') AS total_hours
    FROM CET_Dates dat
    LEFT JOIN employee_attendance ea 
        ON ea.date = dat.DateValue AND ea.employee_id_id = employee_id
    LEFT JOIN employees_attendance_info attendance_info
        ON attendance_info.date = dat.DateValue AND attendance_info.employee_id_id = employee_id
    LEFT JOIN employee_applied_leaves leave
        ON leave.end_date = dat.DateValue AND leave.employee_id_id = employee_id
    ORDER BY dat.DateValue;
END;
$$;

