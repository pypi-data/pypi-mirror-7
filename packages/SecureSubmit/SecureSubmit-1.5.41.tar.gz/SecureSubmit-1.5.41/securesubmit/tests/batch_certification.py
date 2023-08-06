import unittest
from securesubmit.tests.test_data \
    import (TestServicesConfig,
            TestCreditCard,
            TestCardHolder)
from securesubmit.services.gateway \
    import (HpsCreditService,
            HpsExceptionCodes,
            HpsException,
            HpsBatchService)


class BatchCertTests(unittest.TestCase):
    batch_service = HpsBatchService(TestServicesConfig.valid_services_config)
    charge_service = HpsCreditService(TestServicesConfig.valid_services_config)

    def test_inline_certification(self):
        self.batch_should_close_ok()
        self.visa_should_charge_ok()
        self.mastercard_should_charge_ok()
        self.discover_should_charge_ok()
        self.amex_should_charge_ok()
        self.jcb_should_charge_ok()
        self.visa_should_verify_ok()
        self.mastercard_should_verify_ok()
        self.discover_should_verify_ok()
        self.amex_avs_should_verify_ok()
        self.mastercard_return_should_be_ok()
        self.visa_should_reverse_ok()
        self.batch_should_close_ok()

    def batch_should_close_ok(self):
        try:
            response = self.batch_service.close_batch()
            if response is None:
                self.fail("Response is None")
        except HpsException, e:
            if e.message != HpsExceptionCodes.no_open_batch:
                self.fail("Something failed other than 'no open batch'.")

    def visa_should_charge_ok(self):
        response = self.charge_service.charge(
            17.01, "usd",
            TestCreditCard.valid_visa,
            TestCardHolder.cert_holder_short_zip)
        if response is None:
            self.fail("Response is None")

        self.assertEqual(response.response_code, "00")

    def mastercard_should_charge_ok(self):
        response = self.charge_service.charge(
            17.02, "usd",
            TestCreditCard.valid_mastercard,
            TestCardHolder.cert_holder_short_zip_no_street)
        if response is None:
            self.fail("Response is None")

        self.assertEqual(response.response_code, "00")

    def discover_should_charge_ok(self):
        response = self.charge_service.charge(
            17.03, "usd",
            TestCreditCard.valid_discover,
            TestCardHolder.cert_holder_long_zip_no_street)
        if response is None:
            self.fail("Response is None")

        self.assertEqual(response.response_code, "00")

    def amex_should_charge_ok(self):
        response = self.charge_service.charge(
            17.04, "usd",
            TestCreditCard.valid_amex,
            TestCardHolder.cert_holder_short_zip)
        if response is None:
            self.fail("Response is None")

        self.assertEqual(response.response_code, "00")

    def jcb_should_charge_ok(self):
        response = self.charge_service.charge(
            17.05, "usd",
            TestCreditCard.valid_jcb,
            TestCardHolder.cert_holder_long_zip)
        if response is None:
            self.fail("Response is None")

        self.assertEqual(response.response_code, "00")

    def visa_should_verify_ok(self):
        response = self.charge_service.verify(TestCreditCard.valid_visa)
        if response is None:
            self.fail("Response is None")

        self.assertEqual(response.response_code, "85")

    def mastercard_should_verify_ok(self):
        response = self.charge_service.verify(TestCreditCard.valid_visa)
        if response is None:
            self.fail("Response is None")

        self.assertEqual(response.response_code, "85")

    def discover_should_verify_ok(self):
        response = self.charge_service.verify(TestCreditCard.valid_visa)
        if response is None:
            self.fail("Response is None")

        self.assertEqual(response.response_code, "85")

    def amex_avs_should_verify_ok(self):
        response = self.charge_service.verify(
            TestCreditCard.valid_visa,
            TestCardHolder.cert_holder_short_zip_no_street)
        if response is None:
            self.fail("Response is None")

        self.assertEqual(response.response_code, "85")

    def mastercard_return_should_be_ok(self):
        response = self.charge_service.refund(
            15.15, "usd",
            TestCreditCard.valid_mastercard,
            TestCardHolder.cert_holder_short_zip)
        if response is None:
            self.fail("Response is None")

        self.assertEqual(response.response_code, "00")

    def visa_should_reverse_ok(self):
        response = self.charge_service.reverse(
            TestCreditCard.valid_visa,
            17.01, "usd")
        if response is None:
            self.fail("Response is None")

        self.assertEqual(response.response_code, "00")
