import uuid
import hmac
from hashlib import sha1
from django.db import models
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from cloudengine.auth.models import Token


class CloudApp(models.Model):
    name = models.CharField(max_length=20, unique=True)
    key = models.CharField("App ID", max_length=40, primary_key=True)
    created = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.key:
            self.key = self.generate_key()
        return super(CloudApp, self).save(*args, **kwargs)

    def generate_key(self):
        unique = uuid.uuid4()
        return hmac.new(unique.bytes, digestmod=sha1).hexdigest()
    
    def __str__(self):
        return unicode(self.name)


class CloudAPI(models.Model):
    date = models.DateField()
    count = models.IntegerField()
    app = models.ForeignKey(CloudApp)
    


class AppSettings(models.Model):
    app = models.OneToOneField(CloudApp)
    verify_emails = models.BooleanField(default=False)
    
    def __str__(self):
        return unicode(self.app)    


'''
Create a single API authentication token once for the admin.
'''
@receiver(post_save, sender=User)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    token = Token.objects.all()
    if not token:
        token = Token.objects.create()
        token.save()
