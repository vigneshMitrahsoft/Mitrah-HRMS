CREATE OR REPLACE FUNCTION public.fn_get_employee_attendances(
	p_employee_id integer,
	month integer,
	year integer)
    RETURNS TABLE(date_value date, day_of_week character varying, weekend boolean, attendance_status character varying, leave_status character varying, check_in timestamp with time zone, check_out timestamp with time zone, effective_hours time without time zone, total_hours time without time zone, session character varying, leave_type character varying, attendance_id bigint, occasion character varying, permisions_start_time time without time zone, permissions_end_time time without time zone) 
    LANGUAGE 'plpgsql'
    COST 100
    VOLATILE PARALLEL UNSAFE
    ROWS 1000

AS $BODY$
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
        dat.DateValue AS date_value,
        TRIM(TO_CHAR(dat.DateValue, 'Day'))::character varying AS day_of_week,
        CASE
            WHEN TRIM(TO_CHAR(dat.DateValue, 'Day')) IN ('Saturday', 'Sunday') THEN TRUE
            ELSE FALSE
        END AS weekend,
        COALESCE(attendance_info.status, '') AS attendance_status,
        COALESCE(leave.status, '') AS leave_status,
        ea.check_in,
        ea.check_out,
        COALESCE(ea.effective_hours, '00:00:00') AS effective_hours,
        COALESCE(ea.total_hours, '00:00:00') AS total_hours,
        COALESCE(leave_days.session,'') AS  session,  
        COALESCE(leave.leave_type,'') AS leave_type,
		ea.attendance_id,
		holiday.occasion AS occasion,
		ap.start_time AS permissions_start_time,
		ap.end_time AS permissions_end_time
		
    FROM CET_Dates dat
    LEFT JOIN employee_attendance ea 
        ON ea.date = dat.DateValue AND ea.employee_id = p_employee_id
    LEFT JOIN employees_attendance_info attendance_info
        ON attendance_info.date = dat.DateValue AND attendance_info.employee_id = p_employee_id
    LEFT JOIN (
        SELECT ld.*
        FROM employee_applied_leave_days ld
        JOIN employee_applied_leaves l ON l.id = ld.applied_leave_request_id
        WHERE l.employee_id = p_employee_id AND ld.status <> 'Cancelled'
    ) AS leave_days
        ON leave_days.leave_date = dat.DateValue
    LEFT JOIN employee_applied_leaves leave
        ON leave.id = leave_days.applied_leave_request_id AND leave.employee_id = p_employee_id
	LEFT JOIN holiday_holiday holiday
		ON holiday.holiday_date = dat.DateValue
	LEFT JOIN employee_applied_permissions ap
		ON ap.permission_date = dat.DateValue AND ap.employee_id = p_employee_id
    ORDER BY dat.DateValue;
END;
$BODY$;