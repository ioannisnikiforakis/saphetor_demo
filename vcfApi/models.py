"""
Contains the Django ORM models
"""
from django.db import models
from django.db import transaction

class Vcf(models.Model):
    """
    This Model represents a VCF file. We can easily support multiple files 
    by exposing it as endpoint. 
    NOTE: For the scope of this prototype only one File is supported/allowed
    """

    date_created = models.DateTimeField(auto_now_add=True)
    name = models.CharField(max_length=250)
    fullpath = models.TextField()
    needs_update = models.BooleanField(blank=True,default=False)
    is_updating = models.BooleanField(blank=True,default=False)
    date_modified = models.DateTimeField(auto_now=True)

    def set_updating(self, value):
        """
        This function allows setting the is_updating flag atomically. 
        This flag prevents multiple file update functions to run in parallel
        
        Args:
            value(bool): The boolean value indicating that an update process is currently running.
        
        Returns:
            vcf(Vcf): The updated instance
        """
        with transaction.atomic():
            vcf = Vcf.objects.select_for_update().get(id=self.id)
            if vcf and value is not None:
                vcf.is_updating = value
                vcf.save()
        return vcf

    def set_needsupdate(self, value):
        """
        This function allows setting the needs_update flag atomically. 
        This flag indicates that a file's contents contain changes that need 
        to be transferred to the file
        
        Args:
            value(bool): The boolean value indicating that an update process is currently running.
        
        Returns:
            vcf(Vcf): The updated instance
        """
        with transaction.atomic():
            vcf = Vcf.objects.select_for_update().get(id=self.id)
            if vcf and value is not None:
                vcf.needs_update = value
                vcf.save()
        return vcf

class VcfRow(models.Model):
    """
    This Model represents a row/line in a VCF file.
    """
    class Meta:
        """
        Model Meta class.
        Sets the ordering for now.
        """
        ordering = ["line_id"]

    row_id = models.BigAutoField(primary_key=True)
    line_id = models.BigIntegerField(null=True)
    # date_created = models.DateTimeField(auto_now_add=True)
    vcf = models.ForeignKey(Vcf, on_delete=models.CASCADE)
    chrom = models.CharField(max_length=150)
    pos = models.PositiveIntegerField()
    id = models.TextField(null=True)
    ref = models.CharField(max_length=150)
    alt = models.TextField(null=True)
    dirty = models.BooleanField(blank=True,default=False)
    # date_modified = models.DateTimeField(auto_now=True)

class Deleted(models.Model):
    """
    This Model represents a deleted row/line in a VCF file.
    The relevant Celery task will use it to modify the source file allowing the
    main table to be cleared immediatelly. After the file is modified the lines on 
    this table will be deleted.
    """
    row_id = models.BigIntegerField(null=True)
    line_id = models.BigIntegerField(null=True)