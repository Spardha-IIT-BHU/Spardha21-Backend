from django.contrib.auth.models import Group, Permission
from django.db import models

# Create your models here.
class RightsSupport(models.Model):
            
    class Meta:
        
        managed = False  # No database table creation or deletion  \
                         # operations will be performed for this model. 
                
        default_permissions = () # disable "add", "change", "delete"
                                 # and "view" default permissions

        permissions = ( 
            ('view_manager', 'View manager app'),  
            ('export_all', 'Export all data'), 
            ('export_game', 'Export game data'), 
            ('export_user', 'Export user data'),  
        )


new_group, created = Group.objects.get_or_create(name='Special Access')