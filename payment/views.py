from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status 
from user.models import User_Model, Bill
# import sslcommerz_lib
from sslcommerz_lib import SSLCOMMERZ
from django.conf import settings
import logging
from django.http import JsonResponse
from django.conf import settings
import logging
from django.shortcuts import get_object_or_404,redirect
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from user.models import Bill
from user.serializers import BillHistorySerializer





logger = logging.getLogger(__name__)

@csrf_exempt
@api_view(['POST'])
def initiate_payment(request):
    bill_id = request.data.get('bill_id')
    user = request.user

    if not user.is_authenticated:
        return Response({'error': 'Authentication required'}, status=status.HTTP_401_UNAUTHORIZED)

    try:
        user = User_Model.objects.get(id=user.id)
        bill = Bill.objects.get(id=bill_id, user=user)
    except User_Model.DoesNotExist:
        logger.error(f"No associated Account found for user {user.username}")
        return Response({'error': 'User does not have an associated account'}, status=status.HTTP_400_BAD_REQUEST)
    except Bill.DoesNotExist:
        logger.error(f"Bill {bill_id} not found for user {user.username}")
        return Response({'error': 'Bill does not exist'}, status=status.HTTP_404_NOT_FOUND)
    
    if bill.status == 'Paid':
        logger.warning(f"Attempted to initiate payment for already paid bill {bill.id}")
        return Response({'error': 'This bill has already been paid.'}, status=status.HTTP_400_BAD_REQUEST)
    
    payment_data = {
        'total_amount': str(bill.total_amount),
        'currency': 'BDT',
        'tran_id': bill.transaction_id,
        'success_url': settings.SSLCOMMERZ['SUCCESS_URL'],
        'fail_url': settings.SSLCOMMERZ['FAIL_URL'],
        'cancel_url': settings.SSLCOMMERZ['CANCEL_URL'],
        'cus_name': user.username,
        'cus_email': user.email,
        'cus_phone': getattr(user, 'phone', 'N/A'),
        'cus_add1': 'Customer Address',
        'cus_city': 'Dhaka',
        'cus_country': 'Bangladesh',
        'shipping_method': 'NO',
        'product_name': 'Bill Payment',
        'product_category': 'Billing',
        'product_profile': 'general',
    }

    sslcz = SSLCOMMERZ({
        'store_id': settings.SSLCOMMERZ['STORE_ID'],
        'store_pass': settings.SSLCOMMERZ['STORE_PASSWORD'],
        'issandbox': settings.SSLCOMMERZ['IS_SANDBOX']
    })

    response = sslcz.createSession(payment_data)

    if response.get('status') == 'SUCCESS':
        logger.info(f"Payment session created for bill {bill_id}: {response['GatewayPageURL']}")
        return Response({'payment_url': response['GatewayPageURL']}, status=status.HTTP_200_OK)
    else:
        logger.error(f"Failed to create payment session for bill {bill_id}: {response}")
        return Response({'error': 'Failed to create payment session'}, status=status.HTTP_400_BAD_REQUEST)


# @csrf_exempt
# @api_view(['POST'])
# def update_bill_status(bill, status, val_id=None):
#     if bill.status in ['Completed', 'Failed']:
#         logger.warning(f"Bill {bill.id} already processed. Current status: {bill.payment_status}")
#         return
#     bill.payment_status = status
#     if val_id:
#         bill.transaction_id = val_id
#     bill.status = 'Paid' if status == 'Completed' else 'Failed'
#     bill.save()
#     logger.info(f"Bill {bill.id} status updated to {bill.status} with payment status {bill.payment_status}.")


@csrf_exempt
@api_view(['POST'])
def update_bill_status(bill, status, val_id=None):
    if bill.status in ['Paid', 'Failed']:  # ✅ Now checking status only
        logger.warning(f"Bill {bill.id} already processed. Current status: {bill.status}")
        return
    bill.status = 'Paid' if status == 'Completed' else 'Failed'
    if bill.status == 'Paid':
        bill.payment_date = timezone.now()
    if val_id:
        bill.transaction_id = val_id  # Optional: if you expect to override txn ID
    bill.save()
    logger.info(f"Bill {bill.id} marked as {bill.status}.")



logger = logging.getLogger(__name__)

@csrf_exempt
@api_view(['POST'])
def payment_success(request):
    tran_id = request.data.get('tran_id')
    val_id = request.data.get('val_id')

    logger.info(f"Received payment success data: {request.data}")

    if not tran_id or not val_id:
        logger.error("Missing transaction ID or validation ID in the request.")
        return Response({'error': 'Missing transaction or validation ID'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        bill = Bill.objects.get(transaction_id=tran_id)  # Get Bill instead of Order
    except Bill.DoesNotExist:
        logger.error(f"Bill with transaction ID {tran_id} not found.")
        return Response({'error': 'Bill not found'}, status=status.HTTP_404_NOT_FOUND)

    sslcz = SSLCOMMERZ({
        'store_id': settings.SSLCOMMERZ['STORE_ID'],
        'store_pass': settings.SSLCOMMERZ['STORE_PASSWORD'],
        'issandbox': settings.SSLCOMMERZ['IS_SANDBOX']
    })

    response = sslcz.validationTransactionOrder(val_id)

    logger.info(f"Validation response from SSLCOMMERZ: {response}")

    if response.get('status') == 'VALID':
        bill.status = 'Paid'
        bill.payment_date = timezone.now()
        bill.save()
        logger.info(f"Payment successful for bill {bill.id}.")
        return redirect('https://mess-management-frontend-five.vercel.app/payment_success.html')
    else:
        logger.error(f"Payment validation failed: {response}")
        return redirect('https://mess-management-frontend-five.vercel.app/payment_fail.html')


@csrf_exempt
@api_view(['POST'])
def payment_fail(request):
    data = request.GET if request.method == 'GET' else request.POST

    transaction_id = data.get('tran_id')
    status = data.get('status')

    if status == 'FAILED':
        try:
            bill = Bill.objects.get(transaction_id=transaction_id)
            bill.status = 'Failed'
            # bill.payment_date = timezone.now()
            bill.save()
            return redirect('https://mess-management-frontend-five.vercel.app/payment_fail.html')
        except Bill.DoesNotExist:
            return JsonResponse({'error': 'Bill not found for this transaction ID.'}, status=404)
    else:
        return JsonResponse({'error': 'Invalid payment status.'}, status=400)


@csrf_exempt
@api_view(['POST'])
def payment_cancel(request):
    tran_id = request.data.get('tran_id')

    if not tran_id:
        logger.error("Missing transaction ID in payment cancellation")
        return Response({'error': 'Missing transaction ID'}, status=status.HTTP_400_BAD_REQUEST)

    logger.info(f"Payment canceled for transaction ID: {tran_id}")
    return Response({'message': 'Payment Cancelled'}, status=status.HTTP_200_OK)


@csrf_exempt
@api_view(['POST'])
def payment_ipn(request):
    data = request.data
    tran_id = data.get('tran_id')
    val_id = data.get('val_id')
    status = data.get('status')

    if not tran_id or not status:
        logger.error(f"Missing required IPN data: tran_id={tran_id}, status={status}")
        return Response({'error': 'Missing required IPN data'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        bill_id = tran_id.split("_")[1]
        bill = Bill.objects.get(id=bill_id)

        if status == 'VALID':
            bill.status = 'Paid'
            bill.save()
            logger.info(f"IPN validated for bill {bill_id}, transaction ID: {val_id}")
            return Response({'message': 'Payment validated successfully'}, status=status.HTTP_200_OK)
        else:
            bill.status = 'Failed'
            bill.save()
            logger.warning(f"IPN validation failed for bill {bill_id}, status: {status}")
            return Response({'error': 'Payment validation failed'}, status=status.HTTP_400_BAD_REQUEST)
    except Bill.DoesNotExist:
        logger.error(f"Bill not found for IPN transaction ID {tran_id}")
        return Response({'error': 'Bill does not exist'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logger.error(f"Error processing IPN: {str(e)}", exc_info=True)
        return Response({'error': 'Internal Server Error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



@api_view(['POST'])
def payment_callback(request):
    payment_status = request.data.get('status')
    transaction_id = request.data.get('transaction_id')
    bill_id = request.data.get('bill_id')
    bill = get_object_or_404(Bill, id=bill_id)
    if payment_status == 'Completed':
        update_bill_status(bill, 'Completed', transaction_id)
    else:
        update_bill_status(bill, 'Failed')
    return Response({"status": "success"})



# @api_view(['GET'])
# @permission_classes([IsAuthenticated])
# def payment_history(request):
#     if request.user.user_type == 'Admin':
#         bills = Bill.objects.filter(status='Paid').order_by('-payment_date')
#     else:
#         bills = Bill.objects.filter(user=request.user, status='Paid').order_by('-payment_date')
#     serializer = BillHistorySerializer(bills, many=True)
#     return Response(serializer.data)
