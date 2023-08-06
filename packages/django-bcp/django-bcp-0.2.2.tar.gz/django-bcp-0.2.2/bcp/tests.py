"""
Module: Bar Code Printer Unit Tests
Project: Django BCP
Copyright: Adlibre Pty Ltd 2012
License: See LICENSE for license information
"""

from django.core.urlresolvers import reverse
from django.test import TestCase


class BarCodeTest(TestCase):

    def setUp(self):
        """Test data"""
        # auth user
        self.username = 'admin'
        self.password = 'admin'

        self.barcode_test_data = [
            # ('type', 'barcode'),
            ('Standard39', 'ABC1234'),
            ('Standard39', 'ABC-1234'),
            ('Standard39', '123456789'),
            ('Code128', 'ABC1234'),
            ('Code128', 'ABC-1234'),
            ('Code128', '123456789'),
        ]

    def test_generate_barcode(self):
        for barcode in self.barcode_test_data:
            url = reverse('bcp-generate', kwargs={'barcode_type': barcode[0], 'code': barcode[1], })
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200)

    def test_print_barcode(self):
        for barcode in self.barcode_test_data:
            url = reverse('bcp-print', kwargs={'barcode_type': barcode[0], 'code': barcode[1], })
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200)

    def test_embed_example(self):
        for barcode in self.barcode_test_data:
            url = reverse('bcp-embed-example', kwargs={'barcode_type': barcode[0], 'code': barcode[1], })
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200)
            self.assertContains(response, barcode[1])