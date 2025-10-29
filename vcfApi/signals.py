"""
This module contains signals that Django will fire when entities are Created, 
Modified or Deleted. The functions associated with those signals will then 
spawn Celery Tasks that will perform the necessary operations on the source file
"""
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.db.models.signals import post_delete
from vcfApi.models import Vcf
from vcfApi.models import VcfRow
from vcfApi.models import Deleted
from vcfApi import logger
from vcfApi.tasks import modify_file_rows

VCFROW_CMP_POST_SAVE_UUID = "VCFROW_CMP_POST_SAVE_UUID1x"
VCFROW_CMP_POST_DELETE_UUID = "VCFROW_CMP_POST_DELETE_UUID1x"

@receiver(post_delete, sender=VcfRow,weak=False,dispatch_uid=VCFROW_CMP_POST_DELETE_UUID)
def handle_vcfrowpostdelete(sender, **kwargs):
    """
    This function is executed after a VcfRow entity is deleted.
    """
    instance = kwargs['instance']
    if instance.row_id:
        # We need to record this row to the deleted table
        # After that we will call the Celery task that will modify the file
        try:
            drow = Deleted(row_id=instance.row_id,line_id=instance.line_id)
            drow.save()
            vcf_file = Vcf.objects.get(id=instance.vcf_id)
            if vcf_file and not vcf_file.needs_update:
                vcf_file = vcf_file.set_needsupdate(True)
            if vcf_file and not vcf_file.is_updating:
                try:
                    vcf_file = vcf_file.set_updating(True)
                    modify_file_rows.delay(instance.vcf_id)
                except Exception as err:
                    logger.error("Error while trying to start the Celery file modify task!")
                    logger.logException(err)
                    vcf_file.set_updating(False)
        except Exception as err:
            logger.error("Error in signal handle_vcfrowpostdelete!")
            logger.logException(err)

@receiver(post_save, sender=VcfRow,weak=False,dispatch_uid=VCFROW_CMP_POST_SAVE_UUID)
def handle_vcfrowpostsave(sender, **kwargs):
    """
    This function is executed after a VcfRow entity is saved, 
    either on POST(Creation) or PUT/PATCH(Edit)
    """
    instance = kwargs['instance']
    created = kwargs['created']

    if instance.row_id:
        if created:
            logger.info(f"handle_vcfrowpostsave: row Created: {instance.row_id}")
        else:
            logger.info(f"handle_vcfrowpostsave: row {instance.row_id} Modified")
        try:
            VcfRow.objects.filter(row_id=instance.row_id).update(dirty=True)
            vcf_file = Vcf.objects.get(id=instance.vcf_id)
            if vcf_file and not vcf_file.needs_update:
                vcf_file = vcf_file.set_needsupdate(True)
            if vcf_file and not vcf_file.is_updating:
                try:
                    vcf_file = vcf_file.set_updating(True)
                    modify_file_rows.delay(instance.vcf_id)
                except Exception as err:
                    logger.error("Error while trying to start the Celery file modify task!")
                    logger.logException(err)
                    vcf_file.set_updating(False)
        except Exception as err:
            logger.error("Error in signal handle_vcfrowpostsave!")
            logger.logException(err)
