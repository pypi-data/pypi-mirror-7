import unittest
from enum import Enum
from securesubmit.tests.test_data \
    import (TestServicesConfig,
            TestCreditCard,
            TestCardHolder)
from securesubmit.services.gateway \
    import (HpsCreditService,
            HpsExceptionCodes,
            HpsCreditException,
            HpsTransactionDetails)


class VisaTests(unittest.TestCase):
    charge_service = HpsCreditService(
        TestServicesConfig.valid_services_config)

    def test_visa_should_charge(self):
        response = self._charge_valid_visa(50)
        self.assertEqual("00", response.response_code)

    def test_visa_with_details(self):
        details = HpsTransactionDetails()
        details.memo = 'memo'
        details.invoice_number = '1234'
        details.customer_id = 'customerID'

        charge = self.charge_service.charge(
            50, 'usd',
            TestCreditCard.valid_visa,
            TestCardHolder.valid_card_holder,
            False, 'descriptor', False,
            details)

        self.assertIsNotNone(charge)

        transaction = self.charge_service.get(charge.transaction_id)
        self.assertIsNotNone(transaction)
        self.assertEquals(transaction.memo, 'memo')
        self.assertEquals(transaction.invoice_number, '1234')
        self.assertEquals(transaction.customer_id, 'customerID')

    # AVS Tests
    def test_visa_avs_response_B(self):
        response = self._charge_valid_visa(91.01)
        self.assertEqual("B", response.avs_result_code)

    def test_visa_avs_response_C(self):
        response = self._charge_valid_visa(91.02)
        self.assertEqual("C", response.avs_result_code)

    def test_visa_avs_response_D(self):
        response = self._charge_valid_visa(91.03)
        self.assertEqual("D", response.avs_result_code)

    def test_visa_avs_response_I(self):
        response = self._charge_valid_visa(91.05)
        self.assertEqual("I", response.avs_result_code)

    def test_visa_avs_response_M(self):
        response = self._charge_valid_visa(91.06)
        self.assertEqual("M", response.avs_result_code)

    def test_visa_avs_response_P(self):
        response = self._charge_valid_visa(91.07)
        self.assertEqual("P", response.avs_result_code)

    # CVV Tests
    def test_visa_cvv_response_M(self):
        response = self._charge_valid_visa(96.01)
        self.assertEqual("M", response.cvv_result_code)

    def test_visa_cvv_response_N(self):
        response = self._charge_valid_visa(96.02)
        self.assertEqual("N", response.cvv_result_code)

    def test_visa_cvv_response_P(self):
        response = self._charge_valid_visa(96.03)
        self.assertEqual("P", response.cvv_result_code)

    def test_visa_cvv_response_S(self):
        response = self._charge_valid_visa(96.04)
        self.assertEqual("S", response.cvv_result_code)

    def test_visa_cvv_response_U(self):
        response = self._charge_valid_visa(96.05)
        self.assertEqual("U", response.cvv_result_code)

    # Visa to Visa 2nd
    def test_visa_response_refer_card_issuer(self):
        try:
            response = self._charge_valid_visa(10.34)
        except HpsCreditException, e:
            self.assertEqual(HpsExceptionCodes.card_declined, e.code)
            return

        self.fail("No exception was thrown.")

    def test_visa_response_invalid_merchant(self):
        try:
            response = self._charge_valid_visa(10.22)
        except HpsCreditException, e:
            self.assertEqual(HpsExceptionCodes.card_declined, e.code)
            return

        self.fail("No exception was thrown.")

    def test_visa_response_pickup_card(self):
        try:
            response = self._charge_valid_visa(10.04)
        except HpsCreditException, e:
            self.assertEqual(HpsExceptionCodes.card_declined, e.code)
            return

        self.fail("No exception was thrown.")

    def test_visa_response_do_not_honor(self):
        try:
            response = self._charge_valid_visa(10.25)
        except HpsCreditException, e:
            self.assertEqual(HpsExceptionCodes.card_declined, e.code)
            return

        self.fail("No exception was thrown.")

    def test_visa_response_invalid_transaction(self):
        try:
            response = self._charge_valid_visa(10.26)
        except HpsCreditException, e:
            self.assertEqual(HpsExceptionCodes.processing_error, e.code)
            return

        self.fail("No exception was thrown.")

    def test_visa_response_invalid_amount(self):
        try:
            response = self._charge_valid_visa(10.27)
        except HpsCreditException, e:
            self.assertEqual(HpsExceptionCodes.invalid_amount, e.code)
            return

        self.fail("No exception was thrown.")

    def test_visa_response_invalid_card(self):
        try:
            response = self._charge_valid_visa(10.28)
        except HpsCreditException, e:
            self.assertEqual(HpsExceptionCodes.incorrect_number, e.code)
            return

        self.fail("No exception was thrown.")

    def test_visa_response_invalid_issuer(self):
        try:
            response = self._charge_valid_visa(10.18)
        except HpsCreditException, e:
            self.assertEqual(HpsExceptionCodes.processing_error, e.code)
            return

        self.fail("No exception was thrown.")

    def test_visa_response_system_error_reenter(self):
        try:
            response = self._charge_valid_visa(10.29)
        except HpsCreditException, e:
            self.assertEqual(HpsExceptionCodes.processing_error, e.code)
            return

        self.fail("No exception was thrown.")

    def test_visa_response_lost_card(self):
        try:
            response = self._charge_valid_visa(10.31)
        except HpsCreditException, e:
            self.assertEqual(HpsExceptionCodes.card_declined, e.code)
            return

        self.fail("No exception was thrown.")

    def test_visa_response_hot_card_pickup(self):
        try:
            response = self._charge_valid_visa(10.03)
        except HpsCreditException, e:
            self.assertEqual(HpsExceptionCodes.card_declined, e.code)
            return

        self.fail("No exception was thrown.")

    def test_visa_response_insufficient_funds(self):
        try:
            response = self._charge_valid_visa(10.08)
        except HpsCreditException, e:
            self.assertEqual(HpsExceptionCodes.card_declined, e.code)
            return

        self.fail("No exception was thrown.")

    def test_visa_response_no_check_amount(self):
        try:
            response = self._charge_valid_visa(10.16)
        except HpsCreditException, e:
            self.assertEqual(HpsExceptionCodes.processing_error, e.code)
            return

        self.fail("No exception was thrown.")

    def test_visa_response_no_savings_account(self):
        try:
            response = self._charge_valid_visa(10.17)
        except HpsCreditException, e:
            self.assertEqual(HpsExceptionCodes.processing_error, e.code)
            return

        self.fail("No exception was thrown.")

    def test_visa_response_expired_card(self):
        try:
            response = self._charge_valid_visa(10.32)
        except HpsCreditException, e:
            self.assertEqual(HpsExceptionCodes.expired_card, e.code)
            return

        self.fail("No exception was thrown.")

    def test_visa_response_txn_not_permitted(self):
        try:
            response = self._charge_valid_visa(10.30)
        except HpsCreditException, e:
            self.assertEqual(HpsExceptionCodes.processing_error, e.code)
            return

        self.fail("No exception was thrown.")

    def test_visa_response_invalid_aquirer(self):
        try:
            response = self._charge_valid_visa(10.30)
        except HpsCreditException, e:
            self.assertEqual(HpsExceptionCodes.processing_error, e.code)
            return

        self.fail("No exception was thrown.")

    def test_visa_response_exceeds_limit(self):
        try:
            response = self._charge_valid_visa(10.09)
        except HpsCreditException, e:
            self.assertEqual(HpsExceptionCodes.card_declined, e.code)
            return

        self.fail("No exception was thrown.")

    def test_visa_response_restricted_card(self):
        try:
            response = self._charge_valid_visa(10.10)
        except HpsCreditException, e:
            self.assertEqual(HpsExceptionCodes.card_declined, e.code)
            return

        self.fail("No exception was thrown.")

    def test_visa_response_security_violation(self):
        try:
            response = self._charge_valid_visa(10.11)
        except HpsCreditException, e:
            self.assertEqual(HpsExceptionCodes.card_declined, e.code)
            return

        self.fail("No exception was thrown.")

    def test_visa_response_check_digit_err(self):
        try:
            response = self._charge_valid_visa(10.05)
        except HpsCreditException, e:
            self.assertEqual(HpsExceptionCodes.incorrect_cvc, e.code)
            return

        self.fail("No exception was thrown.")

    def test_visa_response_system_error(self):
        try:
            response = self._charge_valid_visa(10.21)
        except HpsCreditException, e:
            self.assertEqual(HpsExceptionCodes.processing_error, e.code)
            return

        self.fail("No exception was thrown.")

    def test_visa_response_cvv2_mismatch(self):
        try:
            response = self._charge_valid_visa(10.23)
        except HpsCreditException, e:
            self.assertEqual(HpsExceptionCodes.incorrect_cvc, e.code)
            return

        self.fail("No exception was thrown.")

    # Verify, Authorize & Capture
    def test_visa_verify(self):
        response = self.charge_service.verify(
            TestCreditCard.valid_visa,
            TestCardHolder.valid_card_holder)
        self.assertEqual("85", response.response_code)

    def test_visa_edit(self):
        auth_response = self.charge_service.authorize(
            50, 'usd',
            TestCreditCard.valid_visa,
            TestCardHolder.valid_card_holder)
        self.assertEqual('00', auth_response.response_code)

        edit_response = self.charge_service.edit(
            auth_response.transaction_id, 55, 5)
        self.assertEqual('00', edit_response.response_code)

    def test_visa_authorize(self):
        response = self.charge_service.authorize(
            50, "usd",
            TestCreditCard.valid_visa,
            TestCardHolder.valid_card_holder)
        self.assertEqual("00", response.response_code)

    def test_visa_token_authorize(self):
        response = self.charge_service.authorize(
            50, "usd",
            TestCreditCard.valid_visa,
            TestCardHolder.valid_card_holder, True)
        self.assertEqual('0', response.token_data.token_rsp_code)
        self.assertEqual("00", response.response_code)

    def test_visa_capture(self):
        # Authorize the card.
        auth_response = self.charge_service.authorize(
            50, "usd",
            TestCreditCard.valid_visa,
            TestCardHolder.valid_card_holder)
        self.assertEqual("00", auth_response.response_code)

        # Capture the authorization.
        capture_response = self.charge_service.capture(
            auth_response.transaction_id)
        self.assertEqual("00", capture_response.response_code)

    # Helper Methods
    def _charge_valid_visa(self, amount):
        response = self.charge_service.charge(
            amount, "usd",
            TestCreditCard.valid_visa,
            TestCardHolder.valid_card_holder)
        if response is None:
            self.fail("Response is None")

        return response