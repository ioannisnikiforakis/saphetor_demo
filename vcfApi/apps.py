"""
The Configuration of the VcfApi application is included here
"""
from django.apps import AppConfig

class VcfapiConfig(AppConfig):
    """
    This is the configuration class referenced in the process settings.
    Note: We include the signals.py file here to enable these signals to fire 
    on the regsitered events. 
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'vcfApi'

    def ready(self):
        """
        Add necessary extra imports for the app here
        """
        import vcfApi.signals

class VcfprocConfig(AppConfig):
    """
    This is the configuration class referenced in the proc process settings.
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'vcfApi'
    
    def ready(self):
        """
        Add necessary extra imports for the app here
        """
        pass
