# from .models import *
from rest_framework import  serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer,TokenRefreshSerializer
from rest_framework.exceptions import AuthenticationFailed
from rest_framework import status
from rest_framework_simplejwt.token_blacklist.models import OutstandingToken, BlacklistedToken
from rest_framework_simplejwt.tokens import AccessToken


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
	def get_token(self, user):
		token = super().get_token(user)

		token['first_name'] = user.first_name
		token['last_name'] = user.last_name
		return token
	
	def validate(self, attrs):
		try:
			data = super().validate(attrs)
			response = {
				'status_code': status.HTTP_200_OK,
				'status' : 'success',
				'refresh_token' : data.pop('refresh'),
				'access_token' : data.pop('access')
			}

			return response
		except AuthenticationFailed:
			raise AuthenticationFailed({
				'status': 'error',
				'status_code': status.HTTP_401_UNAUTHORIZED,
				'message': 'Unauthorized User. Invalid username or password. Please try again'
			})
		
class customTokenRefreshSerializer(TokenRefreshSerializer):
	def validate(self, attrs):
		print("attrs", attrs)
		data = super().validate(attrs)  # Get the default validated data

		request = self.context.get("request")
		if request and "Authorization" in request.headers:
			old_access_token = request.headers["Authorization"].split(" ")[1]
			try:
				token = AccessToken(old_access_token)
				print(f"Access token created:{token}")
				# outstanding_token = OutstandingToken.objects.get(token=token)
				# BlacklistedToken.objects.create(token=token)
				BlacklistedToken.objects.create(token=token)

				print("Blacklisting completed successfully!")


			except Exception as e:
				print(f"Error: {str(e)}")

		# Add custom response fields
		return {
			'status_code': status.HTTP_200_OK,
			'status': 'success',
			'access_token': data['access'],
			'refresh_token': data.get('refresh'),  # Ensure refresh token is returned
			'message': 'Token refreshed successfully'
		}