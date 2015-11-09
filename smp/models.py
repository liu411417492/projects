from django.db import models
from django.contrib.auth.models import User
# Create your models here.
        
class Auther(models.Model):
    name = models.CharField(max_length= 30)
    institution = models.CharField(max_length= 30)
    acount = models.IntegerField(default = 0)
    
class Jounery(models.Model):
    J_name=models.CharField(max_length =30)
    jcount = models.IntegerField(default = 0)




class Paper(models.Model):
    user = models. ForeignKey(User)
    MauthorID = models.IntegerField(default = 0)
    auther =  models.ManyToManyField(Auther)
    jounery = models.ForeignKey(Jounery)
    timestamp = models.DateTimeField(auto_now_add=True)
    pdf = models.FileField(upload_to = './smp/static/upload')
    pdfname = models.CharField(max_length = 30)
