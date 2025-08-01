import os
import time
from .llm import extract_text_from_file, get_candidate_info, match_resume, convert_dict, insert_candidate_info, import_resumes
from rest_framework.response import Response
# from rest_framework.views import APIView
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from auth.views import IsAuthorized
from rest_framework import status
from datetime import datetime,date

@api_view(('POST',))
# @permission_classes((IsAuthenticated,))
# @IsAuthorized(['hr']) 
def fetch_resume(request):
	email = request.data['email']
	password = request.data['password']
	start_date = request.data.get('start_date', date.today())
	end_date = request.data.get('end_date', date.today())

	start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
	end_date = datetime.strptime(end_date, "%Y-%m-%d").date()
	try:
		import_resumes(email, password, start_date, end_date)
		return Response(
			{"statuscode": status.HTTP_200_OK, "status": "success", "message": "Imported successfully"},
			status=status.HTTP_200_OK,
		)
	
	except Exception as e:
		return Response({
			"status": "error",
			"message": str(e)
		}, status=status.HTTP_400_BAD_REQUEST)


@api_view(('POST',))
# @permission_classes((IsAuthenticated,))
# @IsAuthorized(['hr']) 
def resume_filteration(request, format=None):
	start_time = time.time()
	

	# tempr_path = "D:/downloads/resume2.pdf"
	# tempr_path = "D:/downloads/Mitrahsoft_Sivakumar_Python_2+yrs (2).pdf"
	# tempr_path = "D:/downloads/Naveen_Python_Developer _ 3 yr.pdf"
	# tempr_path = "D:/downloads/Resumes/Hariharan_M_Resume (1).pdf"  #
	# tempr_path = "D:/downloads/Resumes/Kesava Moorthy-2.pdf"
	# tempr_path = "D:/downloads/Resumes/Naukri_AvinashA[3y_0m].pdf"
	tempr_path = '/app/imap_resumes/resume2.pdf'
	try:
		resume_text = extract_text_from_file(tempr_path)
		parsed_info = get_candidate_info(resume_text)
		jd = request.data.get("jd")
		is_exp = request.data.get("is_experienced", "true").lower() == "true"
		passout_year = request.data.get("passout_year")
		degree = request.data.get("degree")

		match = match_resume(
			resume_text, is_experienced=is_exp, jd=jd, passout_year=passout_year, degree=degree
		)
		end_time = time.time()
		print("the total time--->",end_time - start_time)
		parsed_values = {"candidate_info": parsed_info,"match_result": match}
		print(parsed_values)
		parsed_dict = convert_dict({
			"candidate_info": parsed_info,
			"match_result": match
		})

		insert_candidate_info(parsed_dict)
		return Response(parsed_dict)
	except os.error as e:
		print("error will occur----->",e)






