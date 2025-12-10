from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from unittest.mock import patch
from .models import PaymentTransaction


class HubtelPaymentsTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    @patch('nxtbn.hubtel_payments.services.HubtelPaymentService.initiate_payment')
    def test_initiate_payment_creates_transaction(self, mock_initiate):
        mock_initiate.return_value = {'ResponseCode': '0001', 'TransactionId': 'tx123'}
        url = reverse('hubtel_initiate')
        data = {'msisdn': '233245000000', 'amount': '10.00', 'channel': 'mtn-gh'}
        resp = self.client.post(url, data, format='json')
        self.assertEqual(resp.status_code, 200)
        body = resp.json()
        self.assertIn('client_reference', body)
        cr = body['client_reference']
        tx = PaymentTransaction.objects.get(client_reference=cr)
        self.assertEqual(tx.status, PaymentTransaction.STATUS_PENDING)

    def test_callback_updates_transaction(self):
        tx = PaymentTransaction.objects.create(client_reference='cr-123', customer_msisdn='233245000000', channel='mtn-gh', amount='5.00')
        url = reverse('hubtel_callback')
        payload = {'ClientReference': 'cr-123', 'Status': '0000', 'TransactionId': 'tx-abc'}
        resp = self.client.post(url, payload, format='json')
        self.assertEqual(resp.status_code, 200)
        tx.refresh_from_db()
        self.assertEqual(tx.status, PaymentTransaction.STATUS_SUCCESS)

    @patch('nxtbn.hubtel_payments.services.HubtelPaymentService.check_status')
    def test_status_check_endpoint(self, mock_check):
        tx = PaymentTransaction.objects.create(client_reference='cr-456', customer_msisdn='233245000001', channel='mtn-gh', amount='7.00')
        mock_check.return_value = {'ResponseCode': '0000'}
        url = reverse('hubtel_status', args=['cr-456'])
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        tx.refresh_from_db()
        self.assertEqual(tx.status, PaymentTransaction.STATUS_SUCCESS)
