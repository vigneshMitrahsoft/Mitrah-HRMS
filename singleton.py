from main import settings
import psycopg2

data = settings.DATABASES['default']
conn = psycopg2.connect(
	host = data['HOST'],
	port = data['PORT'],
	dbname = data['NAME'],
	user = data['USER'],
	password = data['PASSWORD']
)
cursor = conn.cursor()
cursor.execute("INSERT INTO company(company_name, address, updated_by)VALUES('testing','testing','1')")
cursor.execute("INSERT INTO roles(role_name)VALUES('Admin'),('HR'),('HR Admin'),('Staff')")
cursor.execute("INSERT INTO employee_type(type_name)VALUES('Full Time'),('Part Time'),('Contract')")
cursor.execute("INSERT INTO employee(company_id_id, first_name, last_name, email, password, date_of_birth, address, date_of_joining, type_id_id, created_at, updated_at, created_by, updated_by, is_active, is_superuser)VALUES(1,'hr','testing','hr.hrms@gmail.com','hr@rtesting', '1998-01-01','testing','2024-01-01',1,'2025-05-06 22:16:05.786801+05:30','2025-05-06 22:16:05.786801+05:30',1,1,false,false)")
conn.commit()
cursor.close()
conn.close()


