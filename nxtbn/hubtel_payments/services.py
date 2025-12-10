import json
import logging
from typing import Optional

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from django.conf import settings

logger = logging.getLogger(__name__)


class HubtelPaymentService:
    def __init__(self):
        self.basic_key = getattr(settings, 'HUBTEL_BASIC_AUTH_KEY', '')
        self.pos_sales_id = getattr(settings, 'HUBTEL_POS_SALES_ID', '')
        self.callback_url = getattr(settings, 'HUBTEL_CALLBACK_URL', '')
        self.session = requests.Session()
        retries = Retry(total=3, backoff_factor=0.3, status_forcelist=(500, 502, 503, 504))
        self.session.mount('https://', HTTPAdapter(max_retries=retries))

    def _headers(self):
        headers = {
            'Authorization': f'Basic {self.basic_key}',
            'Content-Type': 'application/json',
        }
        return headers

    def initiate_payment(self, client_reference: str, msisdn: str, amount: str, channel: str, customer_name: Optional[str] = None, customer_email: Optional[str] = None) -> dict:
        """Call Hubtel Receive Money API to initiate a mobile money request.

        Returns parsed json response or raises requests.HTTPError on non-200.
        """
        if not self.pos_sales_id:
            raise RuntimeError('HUBTEL_POS_SALES_ID not configured')

        url = f"https://rmp.hubtel.com/merchantaccount/merchants/{self.pos_sales_id}/receive/mobilemoney"

        # Hubtel docs use fields like CustomerMsisdn and PrimaryCallbackUrl.
        # To be tolerant of variations, send both sets (safe redundancy).
        payload = {
            'Amount': float(amount),
            'MobileNumber': msisdn,
            'CustomerMsisdn': msisdn,
            'Channel': channel,
            'ClientReference': client_reference,
            'CallbackUrl': self.callback_url,
            'PrimaryCallbackUrl': self.callback_url,
            'Description': f'Payment {client_reference}',
        }
        if customer_name:
            payload['CustomerName'] = customer_name
        if customer_email:
            payload['CustomerEmail'] = customer_email

        resp = self.session.post(url, headers=self._headers(), json=payload, timeout=15)
        try:
            resp.raise_for_status()
        except Exception:
            # capture response body for debugging (but avoid logging credentials)
            body = None
            try:
                body = resp.json()
            except Exception:
                body = resp.text
            logger.error('Hubtel initiate_payment failed: %s %s', getattr(resp, 'status_code', 'N/A'), str(body)[:500])
            raise

        try:
            return resp.json()
        except ValueError:
            return {'raw_text': resp.text}

    def check_status(self, client_reference: str, hubtel_transaction_id: Optional[str] = None) -> dict:
        """Call Hubtel Transaction Status endpoint to reconcile state."""
        if not self.pos_sales_id:
            raise RuntimeError('HUBTEL_POS_SALES_ID not configured')

        url = f"https://api-txnstatus.hubtel.com/transactions/{self.pos_sales_id}/status"
        params = {'clientReference': client_reference}
        if hubtel_transaction_id:
            params['transactionId'] = hubtel_transaction_id

        resp = self.session.get(url, headers=self._headers(), params=params, timeout=15)
        try:
            resp.raise_for_status()
        except Exception:
            logger.exception('Hubtel check_status HTTP error')
            raise

        try:
            return resp.json()
        except ValueError:
            return {'raw_text': resp.text}

    def verify_callback(self, payload: dict) -> bool:
        """Basic verification: ensure clientReference present and looks valid."""
        if not payload or 'ClientReference' not in payload:
            return False
        # further verification such as signature or IP check should be handled in view
        return True
