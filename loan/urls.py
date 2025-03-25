from django.urls import path,include
from . import views


urlpatterns = [
    path('loan/',views.loan_list,name='loan_list_template'),
    path('loan/<int:pk>/',views.loan_detail,name='loan_details_template'),
    path('loan/create/',views.loan_create,name='loan_create_template'),
    path('loan/update/<int:pk>/',views.loan_update,name='loan_update_template'),
    path('loan/delete/<int:pk>/',views.loan_delete,name='loan_delete_template'),
    # path('api/loans/',views.LoanList.as_view(),name='loan_list'),
    # path('api/loan/create/',views.LoanCreate.as_view(),name='loan_create'),
    # path('api/loan/<int:pk>/',views.LoanDetails.as_view(),name='loan_details')
]