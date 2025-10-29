"""
This module Contains various tests for the views DELETE functionality
"""
import json
from rest_framework import status
from django.test import TestCase
from django.urls import reverse
from django.conf import settings
from vcfApi.models import Vcf
from vcfApi.models import VcfRow
from vcfApi.serializers import VcfRowSerializer

class DeleteVcfRowTest(TestCase):
    """ Test module for the Destroy VcfRow API """

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

    def test_delete_valid_row(self):
        """
        Test Deleting a valid row
        """
        # get API response
        response = self.client.delete(reverse('vcfrow-detail',kwargs={'id': self.row1.id}),
            content_type='application/json',HTTP_AUTHORIZATION=self.secret)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        rows = VcfRow.objects.filter(id='rs123456')
        self.assertEqual(len(rows),0)

    def test_delete_multiple_row(self):
        """
        Test Deleting a valid row
        """
        # get API response
        response = self.client.delete(reverse('vcfrow-detail',kwargs={'id': self.row2.id}),
            content_type='application/json',HTTP_AUTHORIZATION=self.secret)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        rows = VcfRow.objects.filter(id='rs123459')
        self.assertEqual(len(rows),0)

    def test_delete_invalid_row(self):
        """
        Test Deleting a nonexistent row
        """
        # get API response
        response = self.client.delete(reverse('vcfrow-detail',kwargs={'id': "rs999999"}),
            content_type='application/json',HTTP_AUTHORIZATION=self.secret)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_valid_row_unauth(self):
        """
        Test Deleting a valid row with the wrong secret
        """
        # get API response
        response = self.client.delete(reverse('vcfrow-detail',kwargs={'id': self.row1.id}),
            content_type='application/json',HTTP_AUTHORIZATION="Wrong_secret")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
