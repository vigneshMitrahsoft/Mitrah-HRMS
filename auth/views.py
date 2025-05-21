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

from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.state import token_backend
from employee.models import employee_roles

def IsAuthorized(required_roles):
	def decorator(view_func):
		def _wrapped_view(request, *args, **kwargs):
			auth_header = request.headers.get("Authorization", None)
			if not auth_header:
				return Response({"detail": "Authorization token missing"}, status=status.HTTP_401_UNAUTHORIZED)

			try:
				token = auth_header.split(" ")[1] 
				decoded_token = token_backend.decode(token)
				employee_id = decoded_token.get("employee_id")
				print("employee_id-->",employee_id)

				if not employee_id:
					return Response({"detail": "Invalid token"}, status=status.HTTP_401_UNAUTHORIZED)

				# roles = list(employee_roles.objects.filter(employee_id=employee_id, is_active=True).values_list("role__role_name", flat=True))
				roles = [role.lower() for role in employee_roles.objects.filter(employee_id=employee_id, is_active=True).values_list("role__role_name", flat=True)]
				print("roles---->",roles)
				if not roles:  
					return Response({"detail": "Employee has no assigned roles"}, status=status.HTTP_403_FORBIDDEN)

				if not any(role in roles for role in required_roles):
					print("employee_",roles)
					return Response({"detail": "Permission denied"}, status=status.HTTP_403_FORBIDDEN)

				return view_func(request, *args, **kwargs)
			
			except Exception as e:
				return Response({"detail": f"Authorization error: {str(e)}"}, status=status.HTTP_401_UNAUTHORIZED)
		return _wrapped_view
	return decorator