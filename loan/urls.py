from django.urls import path,include
from . import views
from . import api


urlpatterns = [
    # path('loan/',views.loan_list,name='loan_list_template'),
    # path('loan/<int:pk>/',views.loan_detail_by_employee,name='loan_details_by_employee_template'),
    # path('loan/create/',views.loan_create,name='loan_create_template'),
    # path('loan/update/<int:pk>/',views.loan_update,name='loan_update_template'),
    # path('loan/delete/<int:pk>/',views.loan_delete,name='loan_delete_template'),
    # path('request_acceptance/<int:pk>/',views.request_acceptance,name='request_acceptance_template'),

    # path('api/loans',api.LoanList.as_view(),name='loan_list'),
    # # path('api/loan/create/',api.LoanCreate.as_view(),name='loan_create'),
    # path('api/loan/<int:pk>',api.LoanDetails.as_view(),name='loan_details')
    
    path('loan',api.loan_list,name='loan_list'),
    path('loan/<int:pk>',api.loan_detail_by_employee,name='loan_detail'),
    path('loan/create',api.loan_create,name='loan_create'),
    path('loan/update/<int:pk>',api.update_loan,name='loan_update'),
    path('loan/delete/<int:pk>',api.loan_delete,name='loan_delete'),
    path('loan/request_acceptance/<int:pk>',api.request_acceptance, name='loan_request_acceptance'),

    path('repayments',api.repayment_list,name='repayment_list'),
    path('repayments/<int:pk>',api.repayment_detail,name='repayment_detail'),

]