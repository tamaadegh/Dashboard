"""
Example: Enhanced Hubtel Payment Views with Sentry Monitoring

This file demonstrates how to integrate comprehensive Sentry monitoring
into your payment processing views. Copy the patterns shown here to your
actual views.py file.
"""

import json
import logging
from django.conf import settings
from django.http import JsonResponse, HttpResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework.decorators import api_view, permission_classes

# Import monitoring utilities
from nxtbn.core.monitoring import (
    log_info,
    log_warning,
    log_error,
    capture_exception,
    track_performance,
    add_breadcrumb,
    increment_counter,
    record_distribution,
    set_custom_context,
)

from nxtbn.hubtel_payments.serializers import InitiatePaymentSerializer, PaymentTransactionSerializer
from nxtbn.hubtel_payments.models import PaymentTransaction
from nxtbn.hubtel_payments.services import HubtelPaymentService

logger = logging.getLogger(__name__)


class InitiatePaymentAPIView(APIView):
    """
    Enhanced payment initiation with comprehensive monitoring
    """
    permission_classes = [permissions.AllowAny]

    @track_performance("payment.initiate")
    def post(self, request):
        # Add breadcrumb for debugging
        add_breadcrumb(
            message="Payment initiation started",
            category="payment",
            level="info",
            data={"channel": request.data.get('channel')}
        )
        
        serializer = InitiatePaymentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        # Log payment initiation
        log_info('Payment initiation request received', extra={
            'channel': data['channel'],
            'amount': float(data['amount']),
            'msisdn': data['msisdn'][:4] + '****'  # Mask phone number for privacy
        })

        # Create unique client reference
        import uuid
        client_ref = str(uuid.uuid4())

        # Prevent duplicates
        if PaymentTransaction.objects.filter(client_reference=client_ref).exists():
            log_error('Duplicate client reference generated', extra={
                'client_reference': client_ref
            })
            increment_counter('payment.error', tags={'reason': 'duplicate_reference'})
            return Response(
                {'detail': 'Duplicate client reference generated, try again'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        # Create transaction record
        try:
            tx = PaymentTransaction.objects.create(
                client_reference=client_ref,
                customer_name=data.get('customer_name', ''),
                customer_msisdn=data['msisdn'],
                customer_email=data.get('customer_email', ''),
                channel=data['channel'],
                amount=data['amount'],
                status=PaymentTransaction.STATUS_PENDING,
            )
            
            # Set context for this transaction
            set_custom_context("payment_transaction", {
                "client_reference": client_ref,
                "channel": data['channel'],
                "amount": float(data['amount'])
            })
            
        except Exception as e:
            log_error('Failed to create payment transaction', extra={
                'error': str(e),
                'channel': data['channel']
            })
            capture_exception(e, context={
                'operation': 'create_payment_transaction',
                'channel': data['channel']
            })
            increment_counter('payment.error', tags={'reason': 'db_error'})
            return Response(
                {'detail': 'Failed to create payment transaction'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        # Initiate payment with Hubtel
        service = HubtelPaymentService()
        try:
            add_breadcrumb(
                message="Calling Hubtel API",
                category="external_api",
                level="info"
            )
            
            resp = service.initiate_payment(
                client_reference=client_ref,
                msisdn=data['msisdn'],
                amount=str(data['amount']),
                channel=data['channel'],
                customer_name=data.get('customer_name'),
                customer_email=data.get('customer_email')
            )
            
            # Log successful initiation
            log_info('Hubtel payment initiated successfully', extra={
                'client_reference': client_ref,
                'hubtel_transaction_id': resp.get('TransactionId') or resp.get('transactionId')
            })
            
            # Track metrics
            increment_counter('payment.initiated', tags={
                'channel': data['channel'],
                'status': 'success'
            })
            record_distribution(
                'payment.amount',
                float(data['amount']),
                unit='dollar',
                tags={'channel': data['channel']}
            )
            
        except Exception as e:
            logger.exception('Hubtel initiate error')
            
            # Capture exception with full context
            capture_exception(e, context={
                'operation': 'hubtel_initiate_payment',
                'client_reference': client_ref,
                'channel': data['channel'],
                'amount': float(data['amount'])
            })
            
            # Update transaction status
            tx.status = PaymentTransaction.STATUS_UNKNOWN
            tx.raw_initial_response = {'error': str(e)}
            tx.save()
            
            # Track failure
            increment_counter('payment.initiated', tags={
                'channel': data['channel'],
                'status': 'failed'
            })
            
            log_error('Failed to initiate Hubtel payment', extra={
                'client_reference': client_ref,
                'error': str(e)
            })
            
            return Response(
                {'detail': 'Failed to initiate payment'},
                status=status.HTTP_502_BAD_GATEWAY
            )

        # Store response
        tx.raw_initial_response = resp
        tx.hubtel_transaction_id = (
            resp.get('TransactionId') or 
            resp.get('transactionId') or 
            resp.get('HubtelTransactionId')
        )
        tx.save()

        return Response({
            'client_reference': client_ref,
            'hubtel_response': resp
        }, status=status.HTTP_200_OK)


@csrf_exempt
@api_view(['POST'])
@permission_classes([permissions.AllowAny])
@track_performance("payment.callback")
def hubtel_callback(request):
    """
    Enhanced callback handler with monitoring
    """
    add_breadcrumb(
        message="Hubtel callback received",
        category="payment_callback",
        level="info"
    )
    
    # Parse payload
    try:
        payload = request.data if hasattr(request, 'data') else json.loads(request.body)
    except Exception as e:
        log_warning('Invalid callback JSON received', extra={
            'error': str(e)
        })
        increment_counter('payment.callback.error', tags={'reason': 'invalid_json'})
        return HttpResponseBadRequest('Invalid JSON')

    # Verify callback
    service = HubtelPaymentService()
    if not service.verify_callback(payload):
        log_warning('Invalid callback payload verification failed', extra={
            'payload_keys': list(payload.keys())
        })
        increment_counter('payment.callback.error', tags={'reason': 'verification_failed'})
        return HttpResponseBadRequest('Invalid callback payload')

    # Extract client reference
    client_ref = (
        payload.get('ClientReference') or 
        payload.get('clientReference') or 
        payload.get('client_reference')
    )
    
    if not client_ref:
        log_warning('Callback missing ClientReference')
        increment_counter('payment.callback.error', tags={'reason': 'missing_reference'})
        return HttpResponseBadRequest('Missing ClientReference')

    # Set context
    set_custom_context("payment_callback", {
        "client_reference": client_ref,
        "status": payload.get('Status') or payload.get('status')
    })

    # Find transaction
    try:
        tx = PaymentTransaction.objects.get(client_reference=client_ref)
    except PaymentTransaction.DoesNotExist:
        log_warning('Callback for unknown transaction', extra={
            'client_reference': client_ref
        })
        increment_counter('payment.callback.error', tags={'reason': 'unknown_reference'})
        return HttpResponseBadRequest('Unknown ClientReference')

    # Prevent double-processing
    if tx.status == PaymentTransaction.STATUS_SUCCESS:
        log_info('Callback for already processed transaction', extra={
            'client_reference': client_ref
        })
        return HttpResponse('Already processed', status=200)

    # Store callback data
    tx.raw_callback_response = payload

    # Determine status
    status_field = (
        payload.get('Status') or 
        payload.get('status') or 
        payload.get('ResponseCode') or 
        payload.get('responseCode')
    )
    
    old_status = tx.status
    
    if status_field in ['0000', '200', 'Success', 'success']:
        tx.status = PaymentTransaction.STATUS_SUCCESS
        log_info('Payment successful', extra={
            'client_reference': client_ref,
            'amount': float(tx.amount)
        })
        increment_counter('payment.completed', tags={
            'channel': tx.channel,
            'status': 'success'
        })
        
    elif status_field in ['0001', 'Pending', 'pending']:
        tx.status = PaymentTransaction.STATUS_PENDING
        log_info('Payment still pending', extra={
            'client_reference': client_ref
        })
        
    else:
        # Map failure codes
        resp_code = str(payload.get('ResponseCode') or payload.get('responseCode') or '')
        if resp_code in ['4000', '4101', '4103']:
            tx.status = PaymentTransaction.STATUS_FAILED
        else:
            tx.status = PaymentTransaction.STATUS_UNKNOWN
            
        log_warning('Payment failed or unknown status', extra={
            'client_reference': client_ref,
            'status_field': status_field,
            'response_code': resp_code
        })
        increment_counter('payment.completed', tags={
            'channel': tx.channel,
            'status': 'failed'
        })

    # Update transaction IDs
    tx.hubtel_transaction_id = (
        tx.hubtel_transaction_id or 
        payload.get('TransactionId') or 
        payload.get('transactionId')
    )
    tx.external_transaction_id = (
        tx.external_transaction_id or 
        payload.get('ExternalId') or 
        payload.get('externalId')
    )
    
    try:
        tx.save()
        
        # Add breadcrumb for status change
        if old_status != tx.status:
            add_breadcrumb(
                message=f"Payment status changed: {old_status} -> {tx.status}",
                category="payment",
                level="info",
                data={
                    'client_reference': client_ref,
                    'old_status': old_status,
                    'new_status': tx.status
                }
            )
            
    except Exception as e:
        log_error('Failed to save payment transaction', extra={
            'client_reference': client_ref,
            'error': str(e)
        })
        capture_exception(e, context={
            'operation': 'save_payment_callback',
            'client_reference': client_ref
        })

    return HttpResponse(status=200)


class PaymentStatusAPIView(APIView):
    """
    Enhanced payment status check with monitoring
    """
    permission_classes = [permissions.AllowAny]

    @track_performance("payment.status_check")
    def get(self, request, client_reference):
        add_breadcrumb(
            message="Payment status check",
            category="payment",
            data={"client_reference": client_reference}
        )
        
        try:
            tx = PaymentTransaction.objects.get(client_reference=client_reference)
        except PaymentTransaction.DoesNotExist:
            log_warning('Status check for unknown transaction', extra={
                'client_reference': client_reference
            })
            increment_counter('payment.status_check', tags={'result': 'not_found'})
            return Response(
                {'detail': 'Not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        # Check if we need to query Hubtel
        from django.utils import timezone
        age_seconds = (timezone.now() - tx.created_at).total_seconds()
        
        if tx.status == PaymentTransaction.STATUS_PENDING and age_seconds > 300:
            log_info('Checking stale payment status with Hubtel', extra={
                'client_reference': client_reference,
                'age_seconds': age_seconds
            })
            
            service = HubtelPaymentService()
            try:
                add_breadcrumb(
                    message="Calling Hubtel status API",
                    category="external_api"
                )
                
                resp = service.check_status(
                    client_reference=client_reference,
                    hubtel_transaction_id=tx.hubtel_transaction_id
                )
                
                # Update transaction
                tx.raw_callback_response = tx.raw_callback_response or {}
                tx.raw_callback_response.update({'status_check': resp})
                
                # Interpret response
                code = (
                    resp.get('ResponseCode') or 
                    resp.get('responseCode') or 
                    resp.get('Status')
                )
                
                old_status = tx.status
                
                if code in ['0000', 'Success', 'success']:
                    tx.status = PaymentTransaction.STATUS_SUCCESS
                elif code in ['0001', 'Pending', 'pending']:
                    tx.status = PaymentTransaction.STATUS_PENDING
                else:
                    tx.status = PaymentTransaction.STATUS_UNKNOWN
                
                tx.save()
                
                if old_status != tx.status:
                    log_info('Payment status updated from Hubtel', extra={
                        'client_reference': client_reference,
                        'old_status': old_status,
                        'new_status': tx.status
                    })
                
                increment_counter('payment.status_check', tags={
                    'result': 'updated',
                    'status': tx.status
                })
                
            except Exception as e:
                log_error('Failed to check Hubtel status', extra={
                    'client_reference': client_reference,
                    'error': str(e)
                })
                capture_exception(e, context={
                    'operation': 'hubtel_status_check',
                    'client_reference': client_reference
                })
                increment_counter('payment.status_check', tags={'result': 'error'})
                return Response(
                    {'detail': 'Failed to reach Hubtel status service'},
                    status=status.HTTP_502_BAD_GATEWAY
                )
        else:
            increment_counter('payment.status_check', tags={
                'result': 'cached',
                'status': tx.status
            })

        serializer = PaymentTransactionSerializer(tx)
        return Response(serializer.data)
