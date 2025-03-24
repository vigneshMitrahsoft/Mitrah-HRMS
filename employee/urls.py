from django.urls import path,include
from . import views
urlpatterns = [
    path("employees",views.get),
    path("employee",views.insertEmployee),
    path('addemployee',views.addEmployee),
    path("employee/<int:id>",views.put),
    path("delete/<int:id>",views.delete)
]