from django.urls import path,include
from . import views


urlpatterns = [
    path('loans/',views.loan_list,name='loan_list_template'),
    path('loan/<int:pk>/',views.loan_details,name='loan_details_template'),
    # path('api/loans/',views.LoanList.as_view(),name='loan_list'),
    # path('api/loan/create/',views.LoanCreate.as_view(),name='loan_create'),
    # path('api/loan/<int:pk>/',views.LoanDetails.as_view(),name='loan_details')
]