# from django.shortcuts import render
# from rest_framework_simplejwt.authentication import JWTAuthentication
# from rest_framework.exceptions import AuthenticationFailed
# from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken, OutstandingToken
# from rest_framework_simplejwt.tokens import AccessToken

# class CustomJWTAuthentication(JWTAuthentication):
#     def authenticate(self, request):
#         user, token = super().authenticate(request) 
#         try:
#             outstanding_token = OutstandingToken.objects.get(token=str(token))
#             if BlacklistedToken.objects.filter(token=outstanding_token).exists():
#                 raise AuthenticationFailed("Token has been blacklisted. Please log in again.")
#         except OutstandingToken.DoesNotExist:
#             pass 
#         return user, token