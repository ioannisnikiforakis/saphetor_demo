"""
This module Contains various tests for the views POST functionality
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

class CreateVcfRowTest(TestCase):
    """ Test module for the Create VcfRow API """

    def setUp(self):
        """
        DB Setup
        """
        self.vcf = Vcf.objects.create(name='file1.vcf', fullpath='path/to/file/file1.vcf')
        self.secret = settings.PREDEFINED_SECRET

    def test_create_valid_row(self):
        """
        Test Creating a valid row
        """
        self.valid_payload = {
            'chrom': 'chrX',
            'pos': 123456,
            'id':'rs123456',
            'ref':"G",
            'alt':"A"
        }
        # get API response
        response = self.client.post(reverse('vcfrow-list'),data=json.dumps(self.valid_payload),
            content_type='application/json',HTTP_AUTHORIZATION=self.secret)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(OrderedDict(response.data),OrderedDict(self.valid_payload))
        row = VcfRow.objects.get(id='rs123456')
        serializer = VcfRowSerializer(row, many=False)
        self.assertEqual(OrderedDict(response.data),OrderedDict(serializer.data))

    def test_create_valid_row_nofile(self):
        """
        Test Creating a valid row without a file previously imported
        """
        Vcf.objects.all().delete()
        self.valid_payload = {
            'chrom': 'chrX',
            'pos': 123456,
            'id':'rs123456',
            'ref':"G",
            'alt':"A"
        }
        # get API response
        response = self.client.post(reverse('vcfrow-list'),data=json.dumps(self.valid_payload),
            content_type='application/json',HTTP_AUTHORIZATION=self.secret)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_invalid_row_chrom(self):
        """
        Test Creating an invalid chrom row
        """
        self.valid_payload = {
            'chrom': 'chrB',
            'pos': 123456,
            'id':'rs123456',
            'ref':"G",
            'alt':"A"
        }
        # get API response
        response = self.client.post(reverse('vcfrow-list'),data=json.dumps(self.valid_payload),
            content_type='application/json',HTTP_AUTHORIZATION=self.secret)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_invalid_row_pos(self):
        """
        Test Creating an invalid pos row
        """
        self.valid_payload = {
            'chrom': 'chrY',
            'pos': -1,
            'id':'rs123456',
            'ref':"G",
            'alt':"A"
        }
        # get API response
        response = self.client.post(reverse('vcfrow-list'),data=json.dumps(self.valid_payload),
            content_type='application/json',HTTP_AUTHORIZATION=self.secret)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_invalid_row_id(self):
        """
        Test Creating an invalid id row
        """
        self.valid_payload = {
            'chrom': 'chrY',
            'pos': 123456,
            'id':'rrs123456',
            'ref':"G",
            'alt':"A"
        }
        # get API response
        response = self.client.post(reverse('vcfrow-list'),data=json.dumps(self.valid_payload),
            content_type='application/json',HTTP_AUTHORIZATION=self.secret)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_invalid_row_ret(self):
        """
        Test Creating an invalid ret row
        """
        self.valid_payload = {
            'chrom': 'chrY',
            'pos': 123456,
            'id':'rrs123456',
            'ref':"M",
            'alt':"A"
        }
        # get API response
        response = self.client.post(reverse('vcfrow-list'),data=json.dumps(self.valid_payload),
            content_type='application/json',HTTP_AUTHORIZATION=self.secret)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_invalid_row_alt(self):
        """
        Test Creating an invalid alt row
        """
        self.valid_payload = {
            'chrom': 'chrY',
            'pos': 123456,
            'id':'rrs123456',
            'ref':"G",
            'alt':"M"
        }
        # get API response
        response = self.client.post(reverse('vcfrow-list'),data=json.dumps(self.valid_payload),
            content_type='application/json',HTTP_AUTHORIZATION=self.secret)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_valid_row_unauth(self):
        """
        Test Creating a valid row with the wrong auth secret
        """
        self.valid_payload = {
            'chrom': 'chrY',
            'pos': 123456,
            'id':'rs123456',
            'ref':"G",
            'alt':"A"
        }
        # get API response
        response = self.client.post(reverse('vcfrow-list'),data=json.dumps(self.valid_payload),
            content_type='application/json',HTTP_AUTHORIZATION="Wrong_secret")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
