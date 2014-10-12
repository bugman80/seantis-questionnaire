from questionnaire.models import Subject
from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
  
  
def create_or_update_subject(sender, **kwargs):
    user_instance = kwargs.get('instance')
    default_values = {'givenname': user_instance.first_name,
                      'surname': user_instance.last_name,
                      'email': user_instance.email}
    if kwargs.get('created', False):
        Subject.objects.create(user=user_instance, **default_values)
    else:
        Subject.objects.filter(user=user_instance).update(**default_values)
  
post_save.connect(create_or_update_subject, sender=get_user_model(), dispatch_uid="create_or_update_subject")