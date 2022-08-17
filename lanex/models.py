from django.db import models
from django.template.defaultfilters import slugify
from django.contrib.auth.models import User
from registration.signals import user_registered
import uuid

'''
THe language model with its fields.
A default image is provided for each language initially if no other image is supplied
  and the names of languages are meant to be unique.
'''
class Language(models.Model):
    name = models.CharField(max_length=128, unique=True)
    slug = models.SlugField(unique=True)
    picture = models.ImageField(upload_to='languages', default='languages/lan.jpg')
    
    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super(Language, self).save(*args, **kwargs)

    def __str__(self):
        return self.name


'''
The language request model and its associated fields.
Request IDs are unique and randomly generated using UUID, in addition to being used as slugs.
'''
class LanguageRequest(models.Model):
    language = models.ForeignKey(Language, on_delete=models.CASCADE)
    title = models.CharField(max_length=128)
    views = models.IntegerField(default=0)
    slug = models.SlugField(unique=True)
    request_id = models.CharField(max_length=128,primary_key=True)
    suggested_date = models.DateField(null=True, blank=True, help_text='Format- MM/DD/YY (extra HH:MM)')
    location = models.CharField(max_length=512)
    creator = models.ForeignKey(User, on_delete=models.CASCADE)
    description = models.CharField(max_length=1024)
    completed = models.BooleanField(default=False)
    picture = models.ImageField(upload_to='requests', blank=True)

    def save(self, *args, **kwargs):
        self.request_id = str(uuid.uuid4().int)
        self.slug = slugify(self.request_id)
        super(LanguageRequest, self).save(*args, **kwargs)

    def __str__(self):
        return self.title

'''
Model for the user profile, comprising the registered user, a profile image and a slug.
A default profile image is provided initially.
'''
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    picture = models.ImageField(upload_to='profile_images', default='profile_images/default.jpg')
    slug = models.SlugField(unique=True)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.user.username)
        super(UserProfile, self).save(*args, **kwargs)

    def __str__(self):
        return self.user.username


'''
A model for the comments, including ordering by creation time.
'''
class Comment(models.Model):
    request = models.ForeignKey(LanguageRequest,on_delete=models.CASCADE,related_name='comments')
    creator = models.ForeignKey(User, on_delete=models.CASCADE)
    body = models.TextField()
    created_on = models.DateTimeField(auto_now_add=True)
    active = models.BooleanField(default=True)

    class Meta:
        ordering = ['created_on']

    def __str__(self):
        return 'Comment {} by {}'.format(self.body, self.name)


'''
Creates a profile for the user after the authenticated user is created.
'''
def createUserProfile(sender, user, request, **kwargs):
    UserProfile.objects.get_or_create(user=user)
    
user_registered.connect(createUserProfile)