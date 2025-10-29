"""
The Celery tasks that will perform the necessary File operations.
These are spawned by the Django Signals module
"""
import os
import vcfpy
from vcfpy import Record as VcfRecord
from celery import shared_task
from django.db.models import F
from vcfApi.models import Vcf
from vcfApi.models import VcfRow
from vcfApi.models import Deleted
from vcfApi import logger
import time
# import gzip

@shared_task
def modify_file_rows(file_id):
    """
    Modify a VCF file that has undergone changes
    
    Args:
        file_id(int): The VCF file entities int PK on our DB.
    """
    time.sleep(1)
    vcf_file = None
    try:
        vcf_file = Vcf.objects.get(id=file_id)
    except Exception as err:
        logger.logException(err)
    if vcf_file:
        try:
            vcf_file = vcf_file.set_needsupdate(False)
            needsUpdate = True
            while needsUpdate:
                logger.info(f"Modifying VCF file:{file_id}")
                # TODO This is a first simplified implementation that needs looking
                # into and optimizing... To make this production ready we would need to 
                # implement Event Sourcing i.e. and proper handling in a sidecar process...
                # Get all the rows that are dirty by line order for now
                dirtyrows = VcfRow.objects.filter(dirty=True).order_by('line_id')
                deletedrows = Deleted.objects.all().order_by('line_id')
                reader = vcfpy.Reader.from_path(vcf_file.fullpath)
                copy_path = vcf_file.fullpath[:vcf_file.fullpath.index(".")]+"_copy.vcf"
                
                logger.info(reader.header)
                
                logger.info(copy_path)
                writer = vcfpy.Writer.from_path(copy_path, reader.header)
                # Get the dirty lines
                dirty_lines = {row.line_id:row for row in dirtyrows}
                deleted_lines = [row.line_id for row in deletedrows]
                logger.info(dirty_lines)
                line_cnt = 0
                # TODO this is a temp hack to make vcfpy play nice...
                row_format = None
                rowcalls = None
                for record in reader:
                    line_cnt+=1
                    row_format = record.FORMAT
                    rowcalls = record.calls
                    if line_cnt in dirty_lines:
                        row = dirty_lines[line_cnt]
                        # Modify record before writing
                        logger.info(f"Modifying {row.row_id} for line {line_cnt}")
                        record.CHROM = row.chrom
                        record.POS = row.pos
                        record.ID = [row.id]
                        record.REF = row.ref
                        record.ALT = [vcfpy.Substitution(type_="SNV",value=row.alt)]
                    if line_cnt not in deleted_lines:
                        writer.write_record(record)
                # Write any new lines that may have been added
                for row in dirtyrows:
                    if row.line_id > line_cnt:
                        logger.info(f"Adding {row.row_id} for line {row.line_id}")
                        rc = VcfRecord(CHROM=row.chrom, POS=row.pos, ID=[row.id], REF=row.ref,
                            ALT=[vcfpy.Substitution(type_="SNV",value=row.alt)], QUAL=None,
                                FILTER=[], INFO={}, FORMAT=row_format, calls=rowcalls)
                        writer.write_record(rc)
                # Now gz the copy file and delete the original
                os.remove(vcf_file.fullpath)
                # TODO if the original was not gz change the path and name to gz
                # TODO This seems to mess up something for the parser
                # with open(copy_path, 'rb') as copy_file:
                #     with gzip.open(vcf_file.fullpath, 'wb') as zipped_file:
                #         zipped_file.writelines(copy_file)
                # TODO for now we leave uncompressed due to weird vcfpy errors...
                os.rename(copy_path,copy_path.replace("_copy",""))
                Vcf.objects.filter(id=file_id).update(fullpath=copy_path.replace("_copy",""))
                # Check if an update was requested while in the process
                vcf_file = Vcf.objects.get(id=file_id)
                needsUpdate = vcf_file.needs_update
                if not needsUpdate:
                    # Set the rows back to clean
                    dirty_idq = dirtyrows.values('row_id')
                    dirty_ids = [i['row_id'] for i in dirty_idq]
                    logger.info(dirty_ids)
                    VcfRow.objects.filter(row_id__in=dirty_ids).update(dirty=False)
                    # Handle deleted lines
                    for dl in deletedrows:
                        logger.info(f"Deleted:{dl.line_id}")
                        VcfRow.objects.filter(line_id__gt=dl.line_id).update(line_id=F('line_id')-1)
                        Deleted.objects.filter(line_id__gt=dl.line_id).update(line_id=F('line_id')-1)
                        dl.delete()
                else:
                    vcf_file = vcf_file.set_needsupdate(False)
        except Exception as err:
            logger.error(f"Error Modifying VCF file:{vcf_file.name}!")
            logger.logException(err)
        finally:
            vcf_file.set_updating(False)
    logger.info(f"Modifying VCF file:{file_id} completed")
    return 'success'
