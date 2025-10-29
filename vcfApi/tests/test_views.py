"""
This module Contains various tests for the views GET functionality
"""
from rest_framework import status
from django.test import TestCase
from django.urls import reverse
from vcfApi.models import Vcf
from vcfApi.models import VcfRow
from vcfApi.serializers import VcfRowSerializer

class GetListVcfRowTest(TestCase):
    """ Test module for the GET VcfRowList API """

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
        row4 = VcfRow.objects.create(vcf_id=self.vcf.id,chrom='chr2', pos=1235,
            id='rs1234',ref='A',alt='G')
        row5 = VcfRow.objects.create(vcf_id=self.vcf.id,chrom='chr2', pos=1236,
            id='rs12345',ref='G',alt='A')
        row6 = VcfRow.objects.create(vcf_id=self.vcf.id,chrom='chr2', pos=1237,
            id='rs12345678',ref='A',alt='T')

    def test_get_valid_all_rows(self):
        """
        Test Get all valid rows
        """
        # get API response
        response = self.client.get(reverse('vcfrow-list'))
        # get data from db
        rows = VcfRow.objects.all()
        serializer = VcfRowSerializer(rows, many=True)
        # Check the response and status code
        response_data = response.data
        self.assertEqual(len(response_data['results']), len(rows))
        self.assertEqual(response_data['results'], serializer.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_valid_multiple_rows(self):
        """
        Test Get multiple valid rows by chrom filter
        """
        # get API response
        response = self.client.get(reverse('vcfrow-list',query={"chrom":self.row2.chrom}))

        # get data from db
        rows = VcfRow.objects.filter(chrom=self.row2.chrom)
        serializer = VcfRowSerializer(rows, many=True)
        # Check the response and status code
        response_data = response.data
        self.assertEqual(len(response_data['results']), len(rows))
        self.assertEqual(response_data['results'], serializer.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_valid_multiple_rows_next(self):
        """
        Test Get valid rows via next link
        """
        # get API response
        response = self.client.get(reverse('vcfrow-list',query={"page_size":2}))
        # Check the response and status code
        response_data = response.data
        self.assertNotEqual(response_data['next'],None)
        self.assertEqual(len(response_data['results']), 2)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.get(response_data['next'])
        self.assertEqual(len(response_data['results']), 2)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_valid_multiple_rows_previous(self):
        """
        Test Get valid rows via previous link
        """
        # get API response
        response = self.client.get(reverse('vcfrow-list',query={"page_size":2,'page':2}))
        # Check the response and status code
        response_data = response.data
        self.assertNotEqual(response_data['previous'],None)
        self.assertEqual(len(response_data['results']), 2)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.get(response_data['previous'])
        self.assertEqual(len(response_data['results']), 2)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_invalid_rows(self):
        """
        Test Get invalid rows via non existent id
        """
        # get API response
        response = self.client.get(reverse('vcfrow-list',query={"id":"rs999999"}))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_no_rows(self):
        """
        Test Get with empty table
        """
        # get API response
        VcfRow.objects.all().delete()
        response = self.client.get(reverse('vcfrow-list'))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_invalidaccept(self):
        """
        Test Get valid rows with invalid accept
        """
        # get API response
        response = self.client.get(reverse('vcfrow-list'),HTTP_ACCEPT="Wrong/value")
        self.assertEqual(response.status_code, status.HTTP_406_NOT_ACCEPTABLE)

    def test_get_acceptxml(self):
        """
        Test Get valid rows with xml accept
        """
        # get API response
        response = self.client.get(reverse('vcfrow-list'),HTTP_ACCEPT="application/xml")
        # get data from db
        rows = VcfRow.objects.all()
        # Check the response and status code
        response_data = response.data
        self.assertEqual(len(response_data['results']), len(rows))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_acceptjson(self):
        """
        Test Get valid rows with json accept
        """
        # get API response
        response = self.client.get(reverse('vcfrow-list'),HTTP_ACCEPT="application/json")
        # get data from db
        rows = VcfRow.objects.all()
        # Check the response and status code
        response_data = response.data
        self.assertEqual(len(response_data['results']), len(rows))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_acceptbackslash(self):
        """
        Test Get valid rows with */* accept
        """
        # get API response
        response = self.client.get(reverse('vcfrow-list'),HTTP_ACCEPT="*/*")
        # get data from db
        rows = VcfRow.objects.all()
        # Check the response and status code
        response_data = response.data
        self.assertEqual(len(response_data['results']), len(rows))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_etag(self):
        """
        Test Get valid rows then check that 304 is return when If-None-Match=<previous_etag>
        """
        # get API response
        response = self.client.get(reverse('vcfrow-list'))
        # get data from db
        rows = VcfRow.objects.all()
        serializer = VcfRowSerializer(rows, many=True)
        # Check the response and status code
        response_data = response.data
        self.assertEqual(len(response_data['results']), len(rows))
        self.assertEqual(response_data['results'], serializer.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        etag_header = response.get('Etag')
        self.assertNotEqual(etag_header, None)
        response = self.client.get(reverse('vcfrow-list'),HTTP_IF_NONE_MATCH=etag_header)
        self.assertEqual(response.status_code, status.HTTP_304_NOT_MODIFIED)

    def test_get_etag_changed(self):
        """
        Test Get valid rows then check that 200 is return when If-None-Match=<previous_etag> 
        and a change has occured
        """
        # get API response
        response = self.client.get(reverse('vcfrow-list'))
        # get data from db
        rows = VcfRow.objects.all()
        serializer = VcfRowSerializer(rows, many=True)
        # Check the response and status code
        response_data = response.data
        self.assertEqual(len(response_data['results']), len(rows))
        self.assertEqual(response_data['results'], serializer.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        etag_header = response.get('Etag')
        self.assertNotEqual(etag_header, None)
        self.row1.pos = 12346
        self.row1.save()
        response = self.client.get(reverse('vcfrow-list'),HTTP_IF_NONE_MATCH=etag_header)
        response_data = response.data
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotEqual(response.get('Etag'),etag_header)

    def test_get_etag_paged(self):
        """
        Test Get valid rows then check that 304 is return when If-None-Match=<previous_etag>
        for paged results
        """
        # get API response
        response = self.client.get(reverse('vcfrow-list',query={"page_size":2}))
        # Check the response and status code
        response_data = response.data
        self.assertNotEqual(response_data['next'],None)
        self.assertEqual(len(response_data['results']), 2)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        etag_header = response.get('Etag')
        self.assertNotEqual(etag_header, None)
        response = self.client.get(reverse('vcfrow-list',query={"page_size":2}),
            HTTP_IF_NONE_MATCH=etag_header)
        self.assertEqual(response.status_code, status.HTTP_304_NOT_MODIFIED)

class GetDetailVcfRowTest(TestCase):
    """ Test module for the GET VcfRowDetail API """

    def setUp(self):
        """
        DB Setup
        """
        self.vcf = Vcf.objects.create(name='file1.vcf', fullpath='path/to/file/file1.vcf')
        self.row1 = VcfRow.objects.create(vcf_id=self.vcf.id,chrom='chr1', pos=12345,
            id='rs123456',ref='G',alt='A')
        self.row2 = VcfRow.objects.create(vcf_id=self.vcf.id,chrom='chr1', pos=12346,
            id='rs123459',ref='A',alt='G')
        row3 = VcfRow.objects.create(vcf_id=self.vcf.id,chrom='chr1', pos=12346,
            id='rs123459',ref='G',alt='T')
        row4 = VcfRow.objects.create(vcf_id=self.vcf.id,chrom='chr1', pos=12347,
            id='rs123459',ref='A',alt='T')

    def test_get_valid_single_row(self):
        """
        Test Get valid single row
        """
        # get API response
        response = self.client.get(reverse('vcfrow-detail',kwargs={'id': self.row1.id}))
        # get data from db
        row = VcfRow.objects.get(id=self.row1.id)
        serializer = VcfRowSerializer(row, many=False)
        # Check the response and status code
        response_data = response.data
        self.assertEqual(len(response_data['results']), 1)
        self.assertEqual(response_data['results'][0], serializer.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_valid_multiple_rows(self):
        """
        Test Get valid multiple rows
        """
        # get API response
        response = self.client.get(reverse('vcfrow-detail',kwargs={'id': self.row2.id}))
        # get data from db
        rows = VcfRow.objects.filter(id=self.row2.id)
        serializer = VcfRowSerializer(rows, many=True)
        # Check the response and status code
        response_data = response.data
        self.assertEqual(len(response_data['results']), len(rows))
        self.assertEqual(response_data['results'], serializer.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_invalid_row(self):
        """
        Test Get invalid row via nonexistent id
        """
        # get API response
        response = self.client.get(reverse('vcfrow-detail',kwargs={'id': "rs9999999"}))
        # Check the response and status code
        response_data = response.data
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_single_row_invalidaccept(self):
        """
        Test Get valid row with invalid accept
        """
        # get API response
        response = self.client.get(reverse('vcfrow-detail',kwargs={'id': self.row1.id}),
            HTTP_ACCEPT="Wrong/value")
        self.assertEqual(response.status_code, status.HTTP_406_NOT_ACCEPTABLE)

    def test_get_single_row_acceptxml(self):
        """
        Test Get valid row with xml accept
        """
        # get API response
        response = self.client.get(reverse('vcfrow-detail',kwargs={'id': self.row1.id}),
            HTTP_ACCEPT="application/xml")
        # get data from db
        row = VcfRow.objects.get(id=self.row1.id)
        serializer = VcfRowSerializer(row, many=False)
        # Check the response and status code
        response_data = response.data
        self.assertEqual(len(response_data['results']), 1)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_single_row_acceptjson(self):
        """
        Test Get valid row with json accept
        """
        # get API response
        response = self.client.get(reverse('vcfrow-detail',kwargs={'id': self.row1.id}),
            HTTP_ACCEPT="application/json")
        # get data from db
        row = VcfRow.objects.get(id=self.row1.id)
        serializer = VcfRowSerializer(row, many=False)
        # Check the response and status code
        response_data = response.data
        self.assertEqual(len(response_data['results']), 1)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_single_row_acceptbackslash(self):
        """
        Test Get valid row with */* accept
        """
        # get API response
        response = self.client.get(reverse('vcfrow-detail',kwargs={'id': self.row1.id}),
            HTTP_ACCEPT="*/*")
        # get data from db
        row = VcfRow.objects.get(id=self.row1.id)
        serializer = VcfRowSerializer(row, many=False)
        # Check the response and status code
        response_data = response.data
        self.assertEqual(len(response_data['results']), 1)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_single_row_etag(self):
        """
        Test Get valid row then check that 304 is return when If-None-Match=<previous_etag>
        """
        # get API response
        response = self.client.get(reverse('vcfrow-detail',kwargs={'id': self.row1.id}))
        # get data from db
        row = VcfRow.objects.get(id=self.row1.id)
        serializer = VcfRowSerializer(row, many=False)
        # Check the response and status code
        response_data = response.data
        self.assertEqual(len(response_data['results']), 1)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        etag_header = response.get('Etag')
        self.assertNotEqual(etag_header, None)
        response = self.client.get(reverse('vcfrow-detail',kwargs={'id': self.row1.id}),
            HTTP_IF_NONE_MATCH=etag_header)
        self.assertEqual(response.status_code, status.HTTP_304_NOT_MODIFIED)

    def test_get_single_row_etag_changed(self):
        """
        Test Get valid row then check that 200 is return when If-None-Match=<previous_etag> 
        and a change has occured
        """
        # get API response
        response = self.client.get(reverse('vcfrow-detail',kwargs={'id': self.row1.id}))
        # get data from db
        row = VcfRow.objects.get(id=self.row1.id)
        serializer = VcfRowSerializer(row, many=False)
        # Check the response and status code
        response_data = response.data
        self.assertEqual(len(response_data['results']), 1)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        etag_header = response.get('Etag')
        self.assertNotEqual(etag_header, None)
        self.row1.pos = 12346
        self.row1.save()
        response = self.client.get(reverse('vcfrow-detail',kwargs={'id': self.row1.id}),
            HTTP_IF_NONE_MATCH=etag_header)
        response_data = response.data
        self.assertEqual(len(response_data['results']), 1)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotEqual(response.get('Etag'),etag_header)

    def test_get_valid_multiple_rows_next(self):
        """
        Test Get valid rows via next link
        """
        # get API response
        response = self.client.get(reverse('vcfrow-detail',kwargs={'id': self.row2.id},
            query={"page_size":1}))
        # Check the response and status code
        response_data = response.data
        self.assertEqual(len(response_data['results']), 1)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotEqual(response_data['next'],None)
        response = self.client.get(response_data['next'])
        self.assertEqual(len(response_data['results']), 1)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_valid_multiple_rows_previous(self):
        """
        Test Get valid rows via previous link
        """
        # get API response
        response = self.client.get(reverse('vcfrow-detail',kwargs={'id': self.row2.id},
            query={"page_size":1,"page":2}))
        # Check the response and status code
        response_data = response.data
        self.assertEqual(len(response_data['results']), 1)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotEqual(response_data['previous'],None)
        response = self.client.get(response_data['previous'])
        self.assertEqual(len(response_data['results']), 1)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
