from main import settings
import psycopg2
from datetime import datetime
from django.contrib.auth.hashers import make_password

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'main.settings')  # 🔁 Change this to your actual settings module path
django.setup()

from django.conf import settings

# Now you can use make_password
plain_password = 'hr@rtesting'
hashed_password = make_password(plain_password)

data = settings.DATABASES['default']
conn = psycopg2.connect(
	host = data['HOST'],
	port = data['PORT'],
	dbname = data['NAME'],
	user = data['USER'],
	password = data['PASSWORD']
	
)

cursor = conn.cursor()
cursor.execute(f"INSERT INTO company(company_name, address, created_at, updated_at, updated_by,is_active)VALUES('testing','testing','{datetime.now()}','2025-05-06 22:16:05.786801+05:30',1,True)RETURNING company_id")
company_id = cursor.fetchone()[0]
cursor.execute(f"INSERT INTO company_settings(hra, employer_esi, employee_esi, employer_pf, employee_pf, leave_compensation, basic_work_hours, sick_leaves, casual_leaves, basic_pay, other_allowances, permission_hours, pay_cycle_day, company_id) VALUES(40,3.25,0.75,12,12,1.00,8.30,2,1,100,40,1.5,12,{company_id})")
cursor.execute("INSERT INTO roles(role_name)VALUES('Admin'),('HR'),('HR Admin'),('Staff')")
cursor.execute("INSERT INTO employee_type(type_name)VALUES('Full Time'),('Part Time'),('Contract') RETURNING type_id")
type_id = cursor.fetchone()[0]
cursor.execute(f"INSERT INTO employee(company_id, first_name, last_name, email, password, date_of_birth, address, date_of_joining, type_id, created_at, updated_at, created_by, updated_by, is_active, is_superuser)VALUES({company_id},'hr','testing','hr.bala3@gmail.com','{hashed_password}', '1998-01-01','testing','2024-01-01',{type_id},'{datetime.now()}','2025-05-06 22:16:05.786801+05:30',1,1,true,false)")
cursor.execute("SELECT employee_id FROM employee WHERE email = 'hr.bala3@gmail.com'")
employee_id = cursor.fetchone()[0]

role_ids = [5,6]
for role_id in role_ids:
	cursor.execute(f"""
		INSERT INTO employee_roles (employee_id, role_id, is_active, created_at, updated_at, created_by, updated_by)
		VALUES ({employee_id}, {role_id}, TRUE, '{datetime.now()}', '{datetime.now()}', 1, 1)
	""")


conn.commit()
cursor.close()
conn.close()
print("User generated successfully")
print("username: hr.hrms@gmail.com")
print("password: hr@rtesting")