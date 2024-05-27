from django.db import models
from django.contrib.postgres.fields import ArrayField

MEDIA_CHOICES = (
    ('Textual', 'Textual'),
    ('Photographic', 'Photographic'),
    ('Video', 'Video'),
    ('Audio', 'Audio'),
    ('Live', 'Live'),
)

class SocialMediaPlatform(models.Model):
    logo = models.ImageField(upload_to="images/")
    name = models.CharField(max_length=50)
    domain_name =  models.CharField(max_length=100)
    description =  models.TextField(max_length=500)
    api_key =  models.CharField(max_length=150)
    api_secret =  models.CharField(max_length=150)
    access_token =  models.CharField(max_length=150)
    access_token_secret =  models.CharField(max_length=50)
    created_at =  models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return self.name
    

class Country(models.Model):
    abbr = models.CharField(max_length=3)

    def __str__(self):
        return self.abbr

class Post(models.Model):
    platform_id = models.PositiveIntegerField()
    user_id = models.CharField(max_length=255)
    username = models.CharField(max_length=255)
    post_id = models.CharField(max_length=255)
    content = models.TextField()
    content_type = models.CharField(max_length=255)
    post_date = models.DateTimeField()
    url = models.URLField()
    country = models.CharField(max_length=255)
    likes = ArrayField(models.IntegerField())
    shares = ArrayField(models.IntegerField())
    num_comments = ArrayField(models.IntegerField())
    comments = models.JSONField()
    last_updated = models.DateField(auto_now=True)

    def __str__(self):
        return f"{self.platform_id} {self.index_id} {self.content_type}"

