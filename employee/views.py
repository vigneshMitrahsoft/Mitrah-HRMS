from django.shortcuts import render,HttpResponse,redirect
from .models import *
from datetime import date

def get(request):
    employee_list = Employee.objects.all().values()
    return render(request,"list.html",{'employee_list':employee_list})

def delete(request,id):
    employee = Employee.objects.get(employee_id = id)
    employee.is_active = False
    employee.save()
    return redirect("/employees")
def insertEmployee(request):
    companies = Company.objects.all().values()
    roles = EmployeeRole.objects.all().values()
    types = EmployeeType.objects.all().values()
    return render(request,"employee_add_update.html",{'companies':companies,'types':types,'roles':roles,'header':'Insert'})
def addEmployee(request):
    employee_id = request.POST['employee_id']
    company_id = 2
    company = Company.objects.get(company_id = company_id)
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
    date_of_joining = request.POST['date_of_joining']
    if employee_id=="":
        print("hlooo")
        # employee = Employee.objects.create(company_id = company, first_name = first_name,last_name = last_name,password = password,email = email, date_of_birth = dob, address = address, role_id = role,type_id = type, created_by = "testing", updated_by = "testing",date_of_joining = date_of_joining)
        pass
    else:
        print("dfdsdsfjsn",employee_id)
        employee = Employee.objects.get(employee_id = employee_id)
        employee.first_name = first_name
        employee.last_name = last_name
        employee.email = email
        employee.password = password
        employee.role_id = role
        employee.type_id = type
        employee.comapny_id = company
        employee.address = address
        employee.date_of_birth = dob
        employee.date_of_joining = date_of_joining
        employee.save()

def employeeUpdate(request,id):
    employee = Employee.objects.get(employee_id = id)
    employee.date_of_birth = employee.date_of_birth.strftime('%Y-%m-%d')
    employee.date_of_joining = employee.date_of_joining.strftime('%Y-%m-%d')
    companies = Company.objects.all().values()
    roles = EmployeeRole.objects.all().values()
    types = EmployeeType.objects.all().values()
    return render(request,"employee_add_update.html",{'companies':companies,'types':types,'roles':roles,'employee':employee,'header':'Update'})

