from django.urls import path
from . import views
from . import api
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    # path("employees",views.get),
    # path("employee",views.insertEmployee),
    # path('addemployee',views.addEmployee),
    # path("employee/<int:id>",views.employeeUpdate),
    # path("password",views.passsword_check),
    # path("delete/<int:id>",views.delete),
    path("", api.get_employees),
    path("create", api.create_employee),
    path("<int:id>", api.get_employee),
    path("update/<int:id>", api.update_employee),
    path("delete/<int:id>", api.delete_employee),
    path("login", api.login),
    path("token", TokenObtainPairView.as_view(), name="token_obtain_pair"),  
    path("token/refresh", TokenRefreshView.as_view(), name="token_refresh"),
]