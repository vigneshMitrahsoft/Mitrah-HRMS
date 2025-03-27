from django.urls import path
from . import views
from . import api
urlpatterns = [
    # path("employees",views.get),
    # path("employee",views.insertEmployee),
    # path('addemployee',views.addEmployee),
    # path("employee/<int:id>",views.employeeUpdate),
    # path("delete/<int:id>",views.delete),
    path("api/employees",api.get_employees),
    path("employee/create",api.create_employee),
    path("employee/<int:id>",api.get_employee),
    path("employee/<int:id>",api.update_employee),
    path("employee/<int:id>",api.delete_employee),
    path("password",views.passsword_check)

]