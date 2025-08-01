import os
import tempfile
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser
from pdfminer.high_level import extract_text
from docx import Document
from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage, SystemMessage
from imap_tools import MailBox, AND
from datetime import datetime

llm = ChatOllama(model="mistral")

def extract_text_from_file(file_path):
	print("file_path---->",file_path)
	ext = os.path.splitext(file_path)[-1].lower()
	print("extension---->",ext)
	if ext == ".pdf":
		print("pdf block executed--->",file_path)
		return extract_text(file_path)
	elif ext == ".docx":
		print("doc file executed------>",file_path)
		doc = Document(file_path)
		return "\n".join(p.text for p in doc.paragraphs)
	else:
		print("fhkjdshskhf-->0",ext)
		return ""

def get_candidate_info(text):
	system = SystemMessage(
		content ="""
			You are a resume parser. Your job is to return a clean Python dictionary.

			Only output the dictionary with these keys:
			- name
			- email
			- phone
			- education (list of dicts with keys: class_course, institution, percentage_cgpa)
			- location
			- years_of_experience

			Do not include markdown, code blocks, or explanations. Just the dict.
		"""
		# content = "Extract the following resume into a Python dictionary with keys: name, email, phone, education (list of dicts with class_course, institution, percentage_cgpa), location, and years_of_experience. Return only the dictionary without quotes or explanation."
		# content="You are a resume parser. Extract name, email, phone, education, location, years of experience if available. provide the response in python dictionary"
		
		# content  = 'Extract the following resume into a Python dictionary with the keys: name, email, phone, education (a list of dictionaries with class_course, institution, percentage_cgpa), location, and years_of_experience. Return only the dictionary, not as a string or code block.'	
	)

	human = HumanMessage(content=text)
	return llm.invoke([system, human]).content

def match_resume(text, is_experienced=True, jd=None, passout_year=None, degree=None):
	system_msg = SystemMessage(content="You are a recruitment assistant.")
	
	if is_experienced and jd:
		# prompt = f"""
		# Candidate Resume: {text}
		# Job Description: {jd}
		

		# Return how well this candidate matches the job, with reasoning. Give a match score out of 100

		# and additional provide the key with name matched and value must be true or false based on the creteria.
		# """
		# prompt = f"""
		# Compare the following resume and job description. Return a Python dictionary with two keys: "analysis" (a short explanation string) and "matched" (true if the resume meets the job criteria, else false). For experienced candidates, match based on skills and experience; for freshers, match based on graduation year and education. Respond with only the dictionary. Resume: {text} JD: {jd}
		# """

		prompt = f"""
			Compare the following resume and job description.

			Return only a **valid Python dictionary**, no explanations, no markdown, no code blocks.

			The dictionary must contain exactly two keys:
			- "analysis": a short summary string
			- "matched": true if the resume fits the JD, otherwise false

			Example output:
			{{"analysis": "Candidate has 3 years of Python experience matching the role.", "matched": true}}

			Now process:

			Resume: {text}
			JD: {jd}
			"""
		
			
	else:
		# prompt = f"""
		# Candidate Resume: {text}

		# Filter based on fresher criteria:
		# - Graduation Year: {passout_year}
		# - Degree: {degree}
	

		# Return match score out of 100 with reasoning

		# and additional provide the key with name matched and value must be true or false based on the creteria.
		# """
		# prompt = f"""
		# Compare the following resume and job description. Return a Python dictionary with two keys: "analysis" (a short explanation string) and "matched" (true if the resume meets the job criteria, else false). For experienced candidates, match based on skills and experience; for freshers, match based on graduation year and education. Respond with only the dictionary. Resume: {text} JD: {jd}
		# """
		prompt = f"""
			Compare the following resume and job description.

			Return only a **valid Python dictionary**, no explanations, no markdown, no code blocks.

			The dictionary must contain exactly two keys:
			- "analysis": a short summary string
			- "matched": true if the resume fits the JD, otherwise false

			Example output:
			{{"analysis": "Candidate has 3 years of Python experience matching the role.", "matched": true}}

			Now process:

			Resume: {text}
			JD: {jd}
			"""


		 

	return llm.invoke([system_msg, HumanMessage(content=prompt)]).content

	   

import ast
import json
import pandas as pd


def parse_stringified_dict(data):
	
	if isinstance(data, dict):
		return data  

	if not isinstance(data, str):
		raise ValueError("Input must be a string or a dictionary.")

	try:
		return json.loads(data)
	except json.JSONDecodeError:
		try:
			return ast.literal_eval(data)
		except (ValueError, SyntaxError) as e:
			raise ValueError(f"Failed to parse data: {e}")

def convert_dict(payload):
	
	result = {}
	for key, val in payload.items():
		result[key] = parse_stringified_dict(val)
	return result

									# INSERT CANDIDATE INFO INTO EXCEL

def insert_candidate_info(info_data):
	excel_path = "D:/downloads/resume_data.xlsx"

	candidate_info = info_data.get("candidate_info", {})
	match_result = info_data.get("match_result", {})
	flat_data = {
		**candidate_info,
		"analysis": match_result.get("analysis"),
		"matched": match_result.get("matched")
	}


	new_row_df = pd.DataFrame([flat_data])


	if os.path.exists(excel_path):
		existing_df = pd.read_excel(excel_path)
		combined_df = pd.concat([existing_df, new_row_df], ignore_index=True)
	else:
		combined_df = new_row_df

	# Save to Excel
	combined_df.to_excel(excel_path, index=False)



									# IMPORT RESUMES FROM IMAP
def import_resumes(email,password, start_date, end_date):
	print("Start the process -------->")
	SAVE_DIR = 'D:/imap_resumes'
	with MailBox('imap.gmail.com').login(email, password, initial_folder='INBOX') as mailbox:
		messages = mailbox.fetch(AND(date_gte=start_date))

		for msg in messages:
			if msg.date.date() > end_date:
				continue

			if not msg.attachments:
				continue

			for att in msg.attachments:    
				if att.filename.lower().endswith(('.pdf', '.docx')):
					filepath = os.path.join(SAVE_DIR, att.filename)
					with open(filepath, 'wb') as f:
						f.write(att.payload)
					print(f"Saved: {filepath}")