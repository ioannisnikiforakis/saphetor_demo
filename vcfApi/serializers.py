"""
Contains Django DRF serializers to be used by the API views
"""
import re
from rest_framework import serializers
from vcfApi.models import Vcf
from vcfApi.models import VcfRow
MAX_CHROM_NUM = 22
VALID_CHROM = re.compile(r'^chr((\d){1,2}+$|[XYM]?+$)')
VALID_ID = re.compile(r'^rs[0-9]+$')
GEN_ALLOWED_VALUES = ['A','C','G','T','.']

class VcfRowSerializer(serializers.ModelSerializer):
    """This is the serializer class for the VcfRow model. Used by the VcfRowsList Class."""
    class Meta:
        """
        This metaclass contains the necessary information to associate the model with the serializer
        """
        model = VcfRow
        fields = ['chrom', 'pos', 'id', 'ref', 'alt']

    def validate_chrom(self, value):
        """
        Check that the chrom field adheres to specs
        """
        m = VALID_CHROM.match(value)
        if not m:
            raise serializers.ValidationError("CHROM name not valid! Please use a string prefixed "
            "with chr and followed by numbers 1 to 22 or one of letters X,Y,M [Case Sensitive]")

        offset = m.groups(0)
        if offset[0] and offset[0] not in ['X','Y','M']:
            num = 0
            try:
                num = int(offset[0])
            except Exception:
                pass
            if num > MAX_CHROM_NUM or num < 1:
                raise serializers.ValidationError("CHROM name not valid! "
                " Please use a string prefixed with chr and followed by numbers"
                    " 1 to 22 or one of letters X,Y,M [Case Sensitive]")

        return value

    def validate_pos(self, value):
        """
        Check that the pos field adheres to specs
        """
        if value < 1:
            raise serializers.ValidationError("POS value not valid! Needs to be a positive integer")
        return value

    def validate_id(self, value):
        """
        Check that the id field adheres to specs
        """
        if not VALID_ID.match(value):
            raise serializers.ValidationError("ID value not valid! Needs to be a string starting "
                "with rs followed by an integer number i.e. rs314418")
        return value

    def validate_ref(self, value):
        """
        Check that the ref field adheres to specs
        """
        if value not in GEN_ALLOWED_VALUES:
            raise serializers.ValidationError("REF value not valid! Needs to be A,C,G,T or .")
        return value

    def validate_alt(self, value):
        """
        Check that the alt field adheres to specs
        """
        if value not in GEN_ALLOWED_VALUES:
            raise serializers.ValidationError("ALT value not valid! Needs to be A,C,G,T or .")
        return value

    def create(self, validated_data):
        """
        Handle the creation of a new VcfRow via POST
        """
        # Note: In this assignment we assume/support only one
        # Vcf file on the db. So all rows belong to it...
        
        vcf_files = Vcf.objects.all()
        if len(vcf_files) > 0:
            vcf_file = vcf_files[0]
            line_id = 1
            try:
                last_row = VcfRow.objects.latest('line_id')
                if last_row and last_row.line_id:
                    line_id = last_row.line_id + 1
            except:
                pass
            row = VcfRow(line_id=line_id,vcf_id=vcf_file.id,chrom=validated_data.get('chrom')
                    ,pos=validated_data.get('pos'),id=validated_data.get('id'),
                        ref=validated_data.get('ref') ,alt=validated_data.get('alt'),
                            dirty=True)
            row.save()
            return row
        error = {'message': 'No Vcf File was initialised in the db!'}
        raise serializers.ValidationError(error)
