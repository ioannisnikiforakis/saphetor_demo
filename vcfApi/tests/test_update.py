"""
This module Contains various tests for the views PUT functionality
"""
import json
from collections import OrderedDict
from rest_framework import status
from django.test import TestCase
from django.urls import reverse
from django.conf import settings
from vcfApi.models import Vcf
from vcfApi.models import VcfRow
from vcfApi.serializers import VcfRowSerializer

class EditVcfRowTest(TestCase):
    """ Test module for the Update VcfRow API """

    def setUp(self):
        """
        DB Setup
        """
        self.vcf = Vcf.objects.create(name='file1.vcf', fullpath='path/to/file/file1.vcf')
        self.row1 = VcfRow.objects.create(vcf_id=self.vcf.id,chrom='chr1', pos=12345,
            id='rs123456',ref='G',alt='A')
        self.row2 = VcfRow.objects.create(vcf_id=self.vcf.id,chrom='chr1', pos=12346,
            id='rs123459',ref='A',alt='G')
        row3 = VcfRow.objects.create(vcf_id=self.vcf.id,chrom='chr1', pos=1234,
            id='rs123459',ref='G',alt='T')
        self.secret = settings.PREDEFINED_SECRET

    def test_update_valid_row(self):
        """
        Test Updating a valid row
        """
        self.valid_payload = {
            'chrom': 'chrX',
            'pos': 123456,
            'id':'rs123456',
            'ref':"G",
            'alt':"A"
        }
        # get API response
        response = self.client.put(reverse('vcfrow-detail',kwargs={'id': self.row1.id}),data=json.dumps(self.valid_payload),
            content_type='application/json',HTTP_AUTHORIZATION=self.secret)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        row = VcfRow.objects.get(id='rs123456')
        serializer = VcfRowSerializer(row, many=False)
        self.assertEqual(OrderedDict(self.valid_payload),OrderedDict(serializer.data))

    def test_update_valid_row_partial(self):
        """
        Test Updating a valid row(partial)
        """
        self.valid_payload = {
            'chrom': 'chrX',
        }
        # get API response
        response = self.client.patch(reverse('vcfrow-detail',kwargs={'id': self.row1.id}),data=json.dumps(self.valid_payload),
            content_type='application/json',HTTP_AUTHORIZATION=self.secret)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        row = VcfRow.objects.get(id='rs123456')
        self.assertEqual(self.valid_payload["chrom"],row.chrom)

    def test_update_multiple_row(self):
        """
        Test Updating multiple valid rows
        """
        self.valid_payload = {
            'chrom': 'chrX',
            'pos': 123456,
            'id':'rs123459',
            'ref':"G",
            'alt':"A"
        }
        # get API response
        response = self.client.put(reverse('vcfrow-detail',kwargs={'id': self.row2.id}),data=json.dumps(self.valid_payload),
            content_type='application/json',HTTP_AUTHORIZATION=self.secret)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        row = VcfRow.objects.filter(id='rs123459')
        serializer = VcfRowSerializer(row, many=True)
        self.assertEqual(OrderedDict(self.valid_payload),OrderedDict(serializer.data[0]))

    def test_update_invalid_row(self):
        """
        Test Updating a nonexistent row
        """
        self.valid_payload = {
            'chrom': 'chrX',
            'pos': 123456,
            'id':'rs123456789',
            'ref':"G",
            'alt':"A"
        }
        # get API response
        response = self.client.put(reverse('vcfrow-detail',kwargs={'id': 'rs123456789'}),data=json.dumps(self.valid_payload),
            content_type='application/json',HTTP_AUTHORIZATION=self.secret)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        
    def test_update_invalid_row_chrom(self):
        """
        Test Updating a valid row with invalid chrom
        """
        self.valid_payload = {
            'chrom': 'chrB',
            'pos': 123456,
            'id':'rs123456',
            'ref':"G",
            'alt':"A"
        }
        # get API response
        response = self.client.put(reverse('vcfrow-detail',kwargs={'id': self.row1.id}),data=json.dumps(self.valid_payload),
            content_type='application/json',HTTP_AUTHORIZATION=self.secret)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_invalid_row_pos(self):
        """
        Test Updating a valid row with invalid pos
        """
        self.valid_payload = {
            'chrom': 'chrX',
            'pos': -1,
            'id':'rs123456',
            'ref':"G",
            'alt':"A"
        }
        # get API response
        response = self.client.put(reverse('vcfrow-detail',kwargs={'id': self.row1.id}),data=json.dumps(self.valid_payload),
            content_type='application/json',HTTP_AUTHORIZATION=self.secret)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
    def test_update_invalid_row_id(self):
        """
        Test Updating a valid row with invalid id
        """
        self.valid_payload = {
            'chrom': 'chrX',
            'pos': 123377,
            'id':'rrs123456',
            'ref':"G",
            'alt':"A"
        }
        # get API response
        response = self.client.put(reverse('vcfrow-detail',kwargs={'id': self.row1.id}),data=json.dumps(self.valid_payload),
            content_type='application/json',HTTP_AUTHORIZATION=self.secret)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_invalid_row_ref(self):
        """
        Test Updating a valid row with invalid ref
        """
        self.valid_payload = {
            'chrom': 'chrX',
            'pos': 123377,
            'id':'rs123456',
            'ref':"M",
            'alt':"A"
        }
        # get API response
        response = self.client.put(reverse('vcfrow-detail',kwargs={'id': self.row1.id}),data=json.dumps(self.valid_payload),
            content_type='application/json',HTTP_AUTHORIZATION=self.secret)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
    def test_update_invalid_row_alt(self):
        """
        Test Updating a valid row with invalid alt
        """
        self.valid_payload = {
            'chrom': 'chrX',
            'pos': 123377,
            'id':'rs123456',
            'ref':"A",
            'alt':"M"
        }
        # get API response
        response = self.client.put(reverse('vcfrow-detail',kwargs={'id': self.row1.id}),data=json.dumps(self.valid_payload),
            content_type='application/json',HTTP_AUTHORIZATION=self.secret)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_valid_row_unauth(self):
        """
        Test Updating a valid row with the wrong secret
        """
        self.valid_payload = {
            'chrom': 'chrX',
            'pos': 123456,
            'id':'rs123456',
            'ref':"G",
            'alt':"A"
        }
        # get API response
        response = self.client.put(reverse('vcfrow-detail',kwargs={'id': self.row1.id}),data=json.dumps(self.valid_payload),
            content_type='application/json',HTTP_AUTHORIZATION="Wrong_secret")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
