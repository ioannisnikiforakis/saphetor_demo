"""
This is an importer command module that, when called by the relevant script, inserts
all the VCF file data to our database.
"""
import os
import vcfpy
from django.core.management.base import BaseCommand
from vcfApi.models import Vcf
from vcfApi.models import VcfRow
from vcfApi import logger
MAX_BULK_LINES = 1000

def insert_vcf_file(vcf_filename,vcf_source_path):
    """
    This function will read the indicated VCF file via VCFpy.
    It will then insert it to the associated database.
    
    Args:
        vcf_filename(str): The name of the file
        vcf_source_path(str): The full path of the file
    """
    cnt=0
    try:
        # Open file, this will read in the header
        reader = vcfpy.Reader.from_path(vcf_source_path)
        # Create a new VCF entry. Delete the old first for this basic assignemt implementation
        Vcf.objects.all().delete()
        vcf_file = Vcf(name=vcf_filename,fullpath=vcf_source_path)
        vcf_file.save()

        ritems = []
        for record in reader:
            cnt+=1
            # Add record to the db also setting the correct line numbers
            alt = [alt.value for alt in record.ALT]
            row = VcfRow(line_id=cnt,vcf_id=vcf_file.id,chrom=record.CHROM,pos=record.POS,
                id=";".join(record.ID),ref=record.REF,alt="".join(alt))
            ritems.append(row)
            if len(ritems) >= MAX_BULK_LINES:
                VcfRow.objects.bulk_create(ritems,ignore_conflicts=True)
                ritems = []
        if len(ritems) > 0:
            VcfRow.objects.bulk_create(ritems,ignore_conflicts=True)
            ritems = []
    except Exception as err:
        logger.error(f"Error while inserting file{vcf_source_path}!")
        logger.logException(err)
    finally:
        logger.info(f"Final count of lines processed:{cnt}")

class Command(BaseCommand):

    """This command class is utilized by Django via manage.py"""

    help = 'DB Update command. Inserts a filepath set on the VCF_FILE_SOURCE env variable'

    def handle(self, *args, **options):
        """
        This function implements the importing functionality sourcing the path 
        from preset (by bash script) environment variables
        """
        logger.info('Starting DB Updater...')
        vcf_filename = None
        if 'VCF_FILE_SOURCE' in os.environ:
            vcf_source_path = os.environ['VCF_FILE_SOURCE']
            logger.info(f"Importing path:{vcf_source_path}")
            vcf_filename = vcf_source_path
            if 'VCF_FILE_NAME' in os.environ:
                vcf_filename = os.environ['VCF_FILE_NAME']
            if vcf_source_path and os.path.isfile(vcf_source_path):
                insert_vcf_file(vcf_filename,vcf_source_path)
            else:
                logger.error('Indicated source file is invalid. Exiting...')
                return
        else:
            logger.error('No source file recorded the Environment. Exiting...')
            return
