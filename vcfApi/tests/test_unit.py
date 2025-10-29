"""
Test various Helper functions and methods
"""
import os
import vcfpy
# import tempfile
from django.test import TestCase
# from django.test import override_settings
import vcfApi.query as query
from vcfApi.models import Vcf
from vcfApi.management.commands.update_db import insert_vcf_file 

VALID_METADICT_SAMPLE = {'TERM_PROGRAM': 'Apple_Terminal', 'TERM': 'xterm-256color', 'SHELL': '/bin/bash',
'TMPDIR': '/var/folders/8b/4k6l5n6j1xv1lts_4kmnmxc00000gn/T/', 'TERM_PROGRAM_VERSION': '453',
    'OLDPWD': '/Users/ioannisnikiforakis/git/saphetor', 'TERM_SESSION_ID': '894118DF-11CF-47E3-96E5-F60FFDE81B78',
        'USER': 'ioannisnikiforakis', 'SSH_AUTH_SOCK': '/private/tmp/com.apple.launchd.TPVLGLQwzj/Listeners',
        'VIRTUAL_ENV': '/Users/ioannisnikiforakis/git/saphetor/env_shaphetor',
         'SECURITYSESSIONID': '186a2', 'VIRTUAL_ENV_PROMPT': '(env_shaphetor) ',
            'SUPERVISOR_PROCESS_NAME': 'vcfapi', 'SUPERVISOR_GROUP_NAME': 'vcfapi',
             'DJANGO_SETTINGS_MODULE': 'saph_assignment.settings', 'TZ': 'UTC', 'RUN_MAIN': 'true',
              'SERVER_NAME': '8.1.168.192.in-addr.arpa', 'GATEWAY_INTERFACE': 'CGI/1.1',
               'SERVER_PORT': '8000', 'REMOTE_HOST': '', 'CONTENT_LENGTH': '', 'SCRIPT_NAME': '',
                'SERVER_PROTOCOL': 'HTTP/1.1', 'SERVER_SOFTWARE': 'WSGIServer/0.2',
                 'REQUEST_METHOD': 'GET', 'PATH_INFO': '/vcfapi/VcfRows', 'QUERY_STRING': 'pos=122318', 
                 'REMOTE_ADDR': '127.0.0.1', 'CONTENT_TYPE': 'application/json', 
                 'HTTP_HOST': '127.0.0.1:8000', 'HTTP_ACCEPT_ENCODING': 'gzip, deflate',
                  'HTTP_CONNECTION': 'keep-alive', 'HTTP_USER_AGENT': 'HTTPie/3.2.4',
                   'HTTP_ACCEPT': 'application/json',}

class TestQueryFunctions(TestCase):
    """
    Test the Query model HTTP helper functions here
    """     
    def test_filter_query_empty_metadict_filterset(self):
        """
        Test the filter_query function with empty metadict and filterset
        """
        metadict = {}
        filterset = {}
        result = query.filter_query(metadict,filterset)
        self.assertEqual(result,{})

    def test_filter_query_valid_metadict_no_filterset(self):
        """
        Test the filter_query function with empty filterset
        """
        metadict = VALID_METADICT_SAMPLE
        filterset = {}
        result = query.filter_query(metadict,filterset)
        self.assertEqual(result,{})

    def test_filter_query_valid_metadict_filterset(self):
        """
        Test the filter_query function with valid metadict and filterset
        """
        metadict = VALID_METADICT_SAMPLE
        filterset = {'chrom':['exact'], 'pos':['exact'],'id':['exact','isnull']
            ,'ref':['exact'],'alt':['exact']}
        result = query.filter_query(metadict,filterset)
        self.assertEqual(result,{'pos': '122318'})

    def test_filter_query_valid_metadict_filterset_multiple(self):
        """
        Test the filter_query function with valid metadict and filterset
         with more than one parameter
        """
        metadict = VALID_METADICT_SAMPLE
        metadict['QUERY_STRING'] = 'pos=122318&ref=G'
        filterset = {'chrom':['exact'], 'pos':['exact'],'id':['exact','isnull']
            ,'ref':['exact'],'alt':['exact']}
        result = query.filter_query(metadict,filterset)
        self.assertEqual(result,{'pos': '122318','ref': 'G'})

    def test_filter_query_valid_metadict_filterset_multiple_isnull(self):
        """
        Test the filter_query function with valid metadict and filterset
         with more than one parameter
        """
        metadict = VALID_METADICT_SAMPLE
        metadict['QUERY_STRING'] = 'pos=122318&ref__isnull=G'
        filterset = {'chrom':['exact'], 'pos':['exact'],'id':['exact','isnull']
            ,'ref':['exact','isnull'],'alt':['exact']}
        result = query.filter_query(metadict,filterset)
        self.assertEqual(result,{'pos': '122318','ref__isnull': 'G'})

class TestVcfModelMethods(TestCase):
    """
    Test some model methods for the Vcf File model
    """
    def setUp(self):
        """
        DB Setup
        """
        self.vcf = Vcf.objects.create(name='file1.vcf', fullpath='path/to/file/file1.vcf')

    def test_update_updating_field(self):
        """
        Test Updating a valid row is_updating field
        """
        self.assertEqual(self.vcf.is_updating,False)
        self.vcf = self.vcf.set_updating(True)
        self.assertEqual(self.vcf.is_updating,True)
        self.vcf = self.vcf.set_updating(False)
        self.assertEqual(self.vcf.is_updating,False)

    def test_update_needsupdate_field(self):
        """
        Test Updating a valid row needs_update field
        """
        self.assertEqual(self.vcf.needs_update,False)
        self.vcf = self.vcf.set_needsupdate(True)
        self.assertEqual(self.vcf.needs_update,True)
        self.vcf = self.vcf.set_needsupdate(False)
        self.assertEqual(self.vcf.needs_update,False)

# TODO See if we can convince vcfpy to read mock files. 
# Otherwise we need to find out how to construct a minimal acceptable 
# header for this test...
# class TestVcfImporting(TestCase):
#     """
#     Test the VCF file importer
#     """
#
#     @override_settings(MEDIA_ROOT=tempfile.gettempdir())
#     def test_vcf_fileimport(self):
#         """
#         Test Vcf importing in the DB via a mock file
#         """
#         temp_file = tempfile.NamedTemporaryFile()
#         header = vcfpy.Header(samples=vcfpy.SamplesInfos([]))
#         with vcfpy.Writer.from_path(temp_file.name, header) as writer:
#             record = vcfpy.Record(
#                 CHROM="chr1", POS=1, ID=["rs12345"], REF="G", ALT=[vcfpy.Substitution(type_="SNV",value="A")],
#                   QUAL=None, FILTER=[], INFO={}, FORMAT=[]
#             )
#             writer.write_record(record)
#
#         insert_vcf_file("tmp.vcf",temp_file.name)
#         print(Vcf.objects.all())
#         vcf_file = Vcf.objects.get(name="tmp.vcf")
#         vcfrow =  Vcf.objects.get(chrom="chr1")
#         self.assertEqual(vcfrow.id,"rs12345")
#         self.assertEqual(vcfrow.alt,"A")
#         temp_file.close()
