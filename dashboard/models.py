from django.db import models
import uuid

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
    domain_name = models.CharField(max_length=100)
    description = models.TextField(max_length=500)
    api_key = models.CharField(max_length=150)
    api_secret = models.CharField(max_length=150)
    access_token = models.CharField(max_length=150)
    access_token_secret = models.CharField(max_length=50)
    created_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return self.name

class Country(models.Model):
    abbr = models.CharField(max_length=3)

    def __str__(self):
        return self.abbr

class Post(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    platform = models.ForeignKey(SocialMediaPlatform, on_delete=models.CASCADE)
    username = models.CharField(max_length=255)
    post_id = models.CharField(max_length=255, unique=True)
    likes = models.JSONField(default=list)
    num_comments = models.JSONField(default=list)
    shares = models.JSONField(default=list)
    post_date = models.DateField()
    content = models.TextField()
    user_provided_id = models.CharField(max_length=255)
    last_updated = models.DateTimeField(auto_now=True)
    positive_score = models.FloatField(default=0.0)
    neutral_score = models.FloatField(default=0.0)
    bad_score = models.FloatField(default=0.0)
    frequency = models.IntegerField(default=0)
    comments = models.JSONField(default=list)  # Assuming comments are stored as a JSON list
    likes_growth_rates = models.JSONField(default=list)
    shares_growth_rates = models.JSONField(default=list)
    num_comments_growth_rates = models.JSONField(default=list)
    switch_status = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.username} {self.post_id}"
