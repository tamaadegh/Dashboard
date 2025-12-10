import json
import logging
from django.conf import settings
from django.http import JsonResponse, HttpResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework.decorators import api_view, permission_classes

from .serializers import InitiatePaymentSerializer, PaymentTransactionSerializer
from .models import PaymentTransaction
from .services import HubtelPaymentService

logger = logging.getLogger(__name__)


class InitiatePaymentAPIView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = InitiatePaymentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        # create unique client reference
        import uuid
        client_ref = str(uuid.uuid4())

        # prevent duplicates just in case
        if PaymentTransaction.objects.filter(client_reference=client_ref).exists():
            return Response({'detail': 'Duplicate client reference generated, try again'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        tx = PaymentTransaction.objects.create(
            client_reference=client_ref,
            customer_name=data.get('customer_name', ''),
            customer_msisdn=data['msisdn'],
            customer_email=data.get('customer_email', ''),
            channel=data['channel'],
            amount=data['amount'],
            status=PaymentTransaction.STATUS_PENDING,
        )

        service = HubtelPaymentService()
        try:
            resp = service.initiate_payment(client_reference=client_ref, msisdn=data['msisdn'], amount=str(data['amount']), channel=data['channel'], customer_name=data.get('customer_name'), customer_email=data.get('customer_email'))
        except Exception as e:
            logger.exception('Hubtel initiate error')
            tx.status = PaymentTransaction.STATUS_UNKNOWN
            tx.raw_initial_response = {'error': str(e)}
            tx.save()
            return Response({'detail': 'Failed to initiate payment'}, status=status.HTTP_502_BAD_GATEWAY)

        # store raw response
        tx.raw_initial_response = resp
        # attempt to capture hubtel transaction id if present
        tx.hubtel_transaction_id = resp.get('TransactionId') or resp.get('transactionId') or resp.get('HubtelTransactionId')
        tx.save()

        return Response({'client_reference': client_ref, 'hubtel_response': resp}, status=status.HTTP_200_OK)


@csrf_exempt
@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def hubtel_callback(request):
    try:
        payload = request.data if hasattr(request, 'data') else json.loads(request.body)
    except Exception:
        return HttpResponseBadRequest('Invalid JSON')

    service = HubtelPaymentService()
    if not service.verify_callback(payload):
        return HttpResponseBadRequest('Invalid callback payload')

    client_ref = payload.get('ClientReference') or payload.get('clientReference') or payload.get('client_reference')
    if not client_ref:
        return HttpResponseBadRequest('Missing ClientReference')

    try:
        tx = PaymentTransaction.objects.get(client_reference=client_ref)
    except PaymentTransaction.DoesNotExist:
        return HttpResponseBadRequest('Unknown ClientReference')

    # prevent double-processing
    if tx.status == PaymentTransaction.STATUS_SUCCESS:
        return HttpResponse('Already processed', status=200)

    tx.raw_callback_response = payload

    # Hubtel commonly uses fields like 'Status' or 'ResponseCode'
    status_field = payload.get('Status') or payload.get('status') or payload.get('ResponseCode') or payload.get('responseCode')
    # interpret
    if status_field in ['0000', '200', 'Success', 'success']:
        tx.status = PaymentTransaction.STATUS_SUCCESS
    elif status_field in ['0001', 'Pending', 'pending']:
        tx.status = PaymentTransaction.STATUS_PENDING
    else:
        # map common Hubtel failure codes
        resp_code = str(payload.get('ResponseCode') or payload.get('responseCode') or '')
        if resp_code in ['4000', '4101', '4103']:
            tx.status = PaymentTransaction.STATUS_FAILED
        else:
            tx.status = PaymentTransaction.STATUS_UNKNOWN

    tx.hubtel_transaction_id = tx.hubtel_transaction_id or payload.get('TransactionId') or payload.get('transactionId')
    tx.external_transaction_id = tx.external_transaction_id or payload.get('ExternalId') or payload.get('externalId')
    tx.save()

    return HttpResponse(status=200)


class PaymentStatusAPIView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, client_reference):
        try:
            tx = PaymentTransaction.objects.get(client_reference=client_reference)
        except PaymentTransaction.DoesNotExist:
            return Response({'detail': 'Not found'}, status=status.HTTP_404_NOT_FOUND)

        # If still pending and older than 5 minutes, call status API
        from django.utils import timezone
        if tx.status == PaymentTransaction.STATUS_PENDING and (timezone.now() - tx.created_at).total_seconds() > 300:
            service = HubtelPaymentService()
            try:
                resp = service.check_status(client_reference=client_reference, hubtel_transaction_id=tx.hubtel_transaction_id)
            except Exception:
                return Response({'detail': 'Failed to reach Hubtel status service'}, status=status.HTTP_502_BAD_GATEWAY)

            tx.raw_callback_response = tx.raw_callback_response or {}
            tx.raw_callback_response.update({'status_check': resp})
            # interpret response if possible
            code = resp.get('ResponseCode') or resp.get('responseCode') or resp.get('Status')
            if code in ['0000', 'Success', 'success']:
                tx.status = PaymentTransaction.STATUS_SUCCESS
            elif code in ['0001', 'Pending', 'pending']:
                tx.status = PaymentTransaction.STATUS_PENDING
            else:
                tx.status = PaymentTransaction.STATUS_UNKNOWN
            tx.save()

        serializer = PaymentTransactionSerializer(tx)
        return Response(serializer.data)
