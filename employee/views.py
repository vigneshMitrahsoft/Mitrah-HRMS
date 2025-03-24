from django.shortcuts import render,HttpResponse,redirect
from .models import *
from datetime import date
def testing(request):
    return render(request,"dashboard.html")
    # company = Company.objects.create(company_name = "companyA", address = "'weststreet,madurai'")
    # role = EmployeeRole.objects.create(role_name = "HR")
    # type = EmployeeType.objects.create(type_name = "Full-Time")

def employeesList(request):
    company = Company.objects.get(company_id = 2)
    type = EmployeeType.objects.get(type_id =1)
    role = EmployeeRole.objects.get(role_id = 1)
    today = date.today()
    if role.role_name == "HR":
        print(company.company_id)
        employee = Employee.objects.create(company_id = company, first_name = "user1",last_name = "testing", email = "user1@gmail.com", date_of_birth = today, address ="madurai", role_id = role,type_id = type, created_by = "testing", updated_by = "testing",employee_last_date = today)
   
def get(request):
    employee_list = Employee.objects.all().values()
    return render(request,"list.html",{'employee_list':employee_list})
def put(request,id):
    employee = Employee.objects.get(employee_id = id)
    employee.last_name = "test"
    employee.save()
    return redirect("/")
def delete(request,id):
    employee = Employee.objects.get(employee_id = id)
    employee.is_active = False
    employee.save()
    return redirect("/")
def insertEmployee(request):
    companies = Company.objects.all().values()
    roles = EmployeeRole.objects.all().values()
    types = EmployeeType.objects.all().values()
    print("companies--->",roles)  
    return render(request,"employee_add_update.html",{'companies':companies,'types':types,'roles':roles})
def addEmployee(request):
    id_field = request.POST['id_field']
    company_id = request.POST['company']
    company = Company.objects.get(company_id =company_id)
    role_id = request.POST['role']
    role = EmployeeRole.objects.get(role_id = role_id)
    type_id = request.POST['type']
    type = EmployeeType.objects.get(type_id = type_id)
    first_name = request.POST['fname']
    last_name = request.POST['lname']
    email = request.POST['email']
    password = request.POST['password']
    address = request.POST['address']
    dob = request.POST['dob']
    # print("ggghkjgh------>",company_id,role_id,type_id,first_name,last_name,email,password,address,dob)

    if id_field=="":
        # employee = Employee.objects.create(company_id = company, first_name = first_name,last_name = last_name,password = password,email = email, date_of_birth = dob, address = address, role_id = role,type_id = type, created_by = "testing", updated_by = "testing")
        print("hlhpkp")
    else:
        print("dfdsdsfjsn",id_field)
        print(type(id_field),len(id_field))
