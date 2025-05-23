import math
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status
from rest_framework.exceptions import APIException
from taxdeduction.serializer import TaxSlabSerializer, TaxSlabUpdateSerializer, UpdateTaxregimeSerializer
from .models import financial_year, tax_regimes, tax_slabs, employee_tax_regimes
from datetime import date
from decimal import Decimal



@api_view(('POST',))
def setup_financial_year_and_regimes(request):
		# print("inside the setup function")
		today = date.today()
		current_year = today.year
		next_year = current_year + 1

		fy_start = date(current_year, 4, 1)
		fy_end = date(next_year, 3, 31)
		fy_label = f"{current_year}-{str(next_year)[-2:]}"

		print("fy_start",fy_start,"fy_end", fy_end,"fy_label", fy_label)

		# Check if the financial year already exists
		fy, created = financial_year.objects.get_or_create(
			start_date = fy_start,
			end_date = fy_end,
			is_active = True,
			defaults = {'year_label': fy_label}
		)
		if created:
			print("Financial year created:", fy)
		else:
			print("Financial year already exists:", fy)
		
		# Check if the tax regimes already exist
		old_regime, created = tax_regimes.objects.get_or_create(
			regime_name = 'Old Regime'
		)
		if created:
			print("Old regime created:", old_regime)
		else:
			print("Old regime already exists:", old_regime)

		new_regime, created = tax_regimes.objects.get_or_create(
			regime_name = 'New Regime'
		)
		if created:
			print("New regime created:", new_regime)
		else:
			print("New regime already exists:", new_regime)
		return Response({"statuscode" : status.HTTP_201_CREATED, "status" : "success", "message" : "Financial year and regimes setup successfully"}, status = status.HTTP_201_CREATED)




@api_view(('POST',))
def setup_tax_slabs(request):
	try:
		data = request.data
		slabs = data.get('slabs', [])

		if not slabs or not isinstance(slabs, list):
			return Response(
				{"statuscode" : status.HTTP_400_BAD_REQUEST, "status" : "error", "message" : "payload not found"},
				status=status.HTTP_400_BAD_REQUEST
			)
		today = date.today()
		current_year = today.year
		next_year = current_year + 1
		fy_start = date(current_year, 4, 1)
		fy_end = date(next_year, 3, 31)

		try:
			fy = financial_year.objects.get(start_date = fy_start, end_date = fy_end, is_active = True)
		except financial_year.DoesNotExist:
			return APIException({"error": "Financial year not found."}, status = status.HTTP_400_BAD_REQUEST)
		created_slabs = []

		for slab_group in slabs:
			regime_name = slab_group.get('regime_name')
			try:
				regime = tax_regimes.objects.get(regime_name = regime_name)
			except tax_regimes.DoesNotExist:
				raise APIException(detail = {"statuscode": 404, "status": "error", "message": f"Tax regime '{regime_name}' not found."})
			for slab in slab_group.get('slab_data', []):

				slab_data  = {
					'tax_regime':regime,
					'slab_from':slab.get('slab_from'),
					'slab_to':slab.get('slab_to'),
					'slab_rate':slab.get('slab_rate')
				}
				# print("slab_data=====>>>",slab_data)
				serializer = TaxSlabSerializer(data = slab_data)
				# print(serializer.is_valid(), "serializer.is_valid")
				if serializer.is_valid():
				
					slab_from = serializer.validated_data['slab_from']
					slab_to = serializer.validated_data['slab_to']
					slab_rate = serializer.validated_data['slab_rate']

					if slab_to > Decimal('999999999.99'):
						raise APIException(detail = {"statuscode": 400, "status": "error", "message": "slab_to value exceeds maximum allowed."})


					exists = tax_slabs.objects.filter(
							financial_year = fy,
							tax_regime = regime,
							slab_from = slab_from,
							slab_to = slab_to
						).exists()

					if exists:
						return Response({
							"statuscode": status.HTTP_400_BAD_REQUEST,
							"status": "error",
							"message": f"Tax slab for regime '{regime_name}' from {slab_from} to {slab_to} already exists."
						}, status = status.HTTP_400_BAD_REQUEST)
					
					print("serializer.validated_data=====>",serializer.validated_data)

					slab_obj = tax_slabs.objects.create(
						financial_year = fy,
						tax_regime = regime,
						slab_from = slab_from,
						slab_to = slab_to,
						slab_rate = slab_rate,
						is_active = True
					)
					created_slabs.append(slab_obj)
				else:
					return Response({
						"statuscode": status.HTTP_400_BAD_REQUEST,
						"status": "error",
						"message": serializer.errors
					}, status = status.HTTP_400_BAD_REQUEST)
		return Response({
			"statuscode": status.HTTP_201_CREATED,
			"status": "success",
			"message": "Tax slabs created successfully.",
		}, status = status.HTTP_201_CREATED)
	
	except financial_year.DoesNotExist:
		raise APIException(detail = {"statuscode": 404, "status": "error", "message": "Active financial year not found."})
	except tax_regimes.DoesNotExist:
		raise APIException(detail = {"statuscode": 404, "status": "error", "message": "Tax regime not found."})
	except Exception as e:
		return Response({
			"statuscode": status.HTTP_400_BAD_REQUEST,
			"status": "error",
			"message": str(e)
		}, status = status.HTTP_400_BAD_REQUEST)
	


# @api_view(('POST',))
# def calculate_employee_tax_deduction(request):

# 	employee_id = request.data.get('employee_id')
# 	ctc = request.data.get('ctc')

# 	# 1. Get employee record
# 	# employee_id = request.data.get('employee_id')
# 	print("inside the calculate function")
# 	emp = check_employee_exists(employee_id)
# 	print("emp====>",emp)

# 	# 2. If ctc is not provided, calculate from DB
# 	if ctc is None:
# 		ctc = Decimal(emp.gross_pay or 0) + Decimal(emp.variable_pay or 0)
# 	else:
# 		ctc = Decimal(ctc)

# 	if ctc == 0:
# 		return Response({
# 			"statuscode": status.HTTP_400_BAD_REQUEST,
# 			"status": "error",
# 			"message": "ctc not found"
# 		}, status=status.HTTP_400_BAD_REQUEST)

# 	# 3. Determine current financial year
# 	today = date.today()
# 	current_year = today.year
# 	fy_start = date(current_year, 4, 1)
# 	fy_end = date(current_year + 1, 3, 31)

# 	try:
# 		current_fy = financial_year.objects.get(start_date=fy_start, end_date=fy_end, is_active=True)
# 	except financial_year.DoesNotExist:
# 		return Response({
# 			"statuscode": status.HTTP_400_BAD_REQUEST,
# 			"status": "error",
# 			"message": "financial year not found"
# 		}, status=status.HTTP_400_BAD_REQUEST)

# 	# 4. Get employee's selected tax regime for current FY
# 	regime_selection = employee_tax_regimes.objects.get(
# 		employee_id=employee_id,
# 		financial_year=current_fy,
# 		is_active=True
# 	)
# 	print("regime_selection",regime_selection)
# 	try:
# 		regime = regime_selection.tax_regime
# 	except employee_tax_regimes.DoesNotExist:
# 		return Response({
# 			"statuscode": status.HTTP_400_BAD_REQUEST,
# 			"status": "error",
# 			"message": "regime not found"
# 		}, status=status.HTTP_400_BAD_REQUEST)
	
# 	# 5. Get tax slabs for this FY and regime
# 	slabs = tax_slabs.objects.filter(
# 		financial_year=current_fy,
# 		tax_regime=regime,
# 		is_active=True
# 	).order_by('slab_from')

# 	if not slabs.exists():
# 		return Response({
# 			"statuscode": status.HTTP_400_BAD_REQUEST,
# 			"status": "error",
# 			"message": "slab not found"
# 		}, status=status.HTTP_400_BAD_REQUEST)

# 	# 6. Apply slabs progressively
# 	total_tax = Decimal('0.00')

# 	for slab in slabs:
# 		slab_from = slab.slab_from
# 		slab_to = slab.slab_to
# 		slab_rate = slab.slab_rate / Decimal('100.0')

# 		if ctc > slab_from:
# 			taxable_amount = min(ctc, slab_to) - slab_from
# 			tax_for_slab = taxable_amount * slab_rate
# 			total_tax += tax_for_slab

# 	print("total_tax",total_tax)
# 	annual_tax = Decimal(math.ceil(total_tax))
# 	monthly_tax = annual_tax / Decimal('12.0')
# 	print("monthly_tax",monthly_tax)

# 	return Response({
# 		"statuscode": status.HTTP_200_OK,
# 		"annual_tax": round(annual_tax, 2),
# 		"monthly_tax": round(monthly_tax, 2),
# 		# "message": "Tax calculated successfully."
# 	}, status=status.HTTP_200_OK)

@api_view(['PATCH'])
def update_tax_slab(request, pk):
	try:
		# Fetch the existing tax slab using the ID from path
		try:
			slab = tax_slabs.objects.get(tax_slab_id = pk)
		except tax_slabs.DoesNotExist:
			return Response({
				"statuscode": status.HTTP_404_NOT_FOUND,
				"status": "error",
				"message": f"Tax slab with ID {pk} not found."
			}, status = status.HTTP_404_NOT_FOUND)

		# Validate the input using the updated serializer
		serializer = TaxSlabUpdateSerializer(data = request.data, partial = True)
		if serializer.is_valid():
			# Update the fields if provided
			for field, value in serializer.validated_data.items():
				setattr(slab, field, value)

			slab.save()

			return Response({
				"statuscode": status.HTTP_200_OK,
				"status": "success",
				"message": "Tax slab updated successfully."
			}, status = status.HTTP_200_OK)

		else:
			return Response({
				"statuscode": status.HTTP_400_BAD_REQUEST,
				"status": "error",
				"message": serializer.errors
			}, status = status.HTTP_400_BAD_REQUEST)

	except Exception as e:
		return Response({
			"statuscode": status.HTTP_400_BAD_REQUEST,
			"status": "error",
			"message": str(e)
		}, status = status.HTTP_400_BAD_REQUEST)



def calculate_employee_tax_deduction(employee_id, ctc):
	
	ctc = Decimal(str(ctc))
	# Determine current financial year
	today = date.today()
	current_year = today.year
	fy_start = date(current_year, 4, 1)
	fy_end = date(current_year + 1, 3, 31)

	try:
		current_fy = financial_year.objects.get(start_date = fy_start, end_date = fy_end, is_active = True)
	except financial_year.DoesNotExist:
		return Response({
			"statuscode": status.HTTP_400_BAD_REQUEST,
			"status": "error",
			"message": "financial year not found"
		}, status = status.HTTP_400_BAD_REQUEST)

	# Get employee's selected tax regime for current FY
	regime_selection = employee_tax_regimes.objects.get(
		employee_id = employee_id,
		financial_year = current_fy,
		is_active = True
	)
	print("regime_selection",regime_selection)
	try:
		regime = regime_selection.tax_regime
	except employee_tax_regimes.DoesNotExist:
		return Response({
			"statuscode": status.HTTP_400_BAD_REQUEST,
			"status": "error",
			"message": "regime not found"
		}, status = status.HTTP_400_BAD_REQUEST)
	
	# Get tax slabs for this FY and regime
	slabs  =  tax_slabs.objects.filter(
		financial_year = current_fy,
		tax_regime = regime,
		is_active = True
	).order_by('slab_from')

	if not slabs.exists():
		return Response({
			"statuscode": status.HTTP_400_BAD_REQUEST,
			"status": "error",
			"message": "slab not found"
		}, status = status.HTTP_400_BAD_REQUEST)

	# Apply slabs progressively
	total_tax = Decimal('0.00')

	for slab in slabs:
		slab_from = slab.slab_from
		slab_to = slab.slab_to
		slab_rate = slab.slab_rate / Decimal('100.0')

		if ctc > slab_from:
			taxable_amount = min(ctc, slab_to) - slab_from
			tax_for_slab = taxable_amount * slab_rate
			total_tax += tax_for_slab

	annual_tax = Decimal(math.ceil(total_tax))  
	monthly_tax = annual_tax / Decimal('12.0')

	return float(monthly_tax)


@api_view(('PATCH',))
def update_employee_regime(request, pk):
	try:
		tax_regime = employee_tax_regimes.objects.get(employee_id = pk)
	except employee_tax_regimes.DoesNotExist:
		raise APIException(detail = {"statuscode": 404, "status": "error", "message": "Employee tax regime not found"})
	serializer = UpdateTaxregimeSerializer(tax_regime, data = request.data, partial = True)
	if serializer.is_valid():
		employee_tax_regimes.objects.filter(employee_id = pk).update(**serializer.validated_data)
		return Response({"statuscode": status.HTTP_200_OK, "status": "success", "message": "Employee tax regime updated successfully"}, status = status.HTTP_200_OK)
	else:
		return Response({"statuscode": status.HTTP_400_BAD_REQUEST, "status": "error", "message": serializer.errors}, status = status.HTTP_400_BAD_REQUEST)