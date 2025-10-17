from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models.signals import post_save
from django.utils.text import slugify
from shortuuid.django_fields import ShortUUIDField
import uuid


# Create your models here.
class User(AbstractUser):
     username = models.CharField(max_length=150, unique=True)
     email = models.EmailField(unique=True)
     full_name = models.CharField(max_length=150, blank=True, null=True)

     USERNAME_FIELD = 'email'
     REQUIRED_FIELDS = ['username']

     def __str__(self):
         return self.username

     def save(self, *args, **kwargs):
         email_username,mobile = self.email.split('@')
         # Suppose rizon@gmail.com --> email_username = rizon, mobile = gmail.com
         if self.full_name == "" or self.full_name is None: 
             self.full_name = email_username
         if self.username =="" or self.username is None:
             self.username = email_username
         super(User, self).save(*args, **kwargs)


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    image = models.FileField(upload_to='images/', default='default/default.png', blank=True, null=True)
    full_name = models.CharField(max_length=150, blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    about = models.TextField(blank=True, null=True)
    author=models.BooleanField(default=False)
    country = models.CharField(max_length=100, blank=True, null=True)
    facebook = models.URLField(blank=True, null=True)
    twitter = models.URLField(blank=True, null=True)

    def __str__(self):
        return self.user.username
    
    def save(self, *args, **kwargs):
        # Suppose rizon@gmail.com --> email_username = rizon, mobile = gmail.com
        if self.full_name == "" or self.full_name is None: 
            self.full_name = self.user.full_name
        if self.user.username =="" or self.user.username is None:
            self.user.username = self.user.full_name
            
        super(Profile, self).save(*args, **kwargs)
        
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()

post_save.connect(create_user_profile, sender=User)
post_save.connect(save_user_profile, sender=User)

class Category(models.Model):
    title=models.CharField(max_length=150)
    image=models.FileField(upload_to='images/', default='default/default.png', blank=True, null=True)
    slug=models.SlugField(unique=True,null=True,blank=True)

    def __str__(self):
        return self.title
    # class Meta:
    #     verbose_name_plural = "Categories"

    def save(self, *args, **kwargs):
        if self.slug=="" or self.slug==None:
            self.slug=slugify(self.title)
        super(Category,self).save(*args,**kwargs)
    def post_count(self):
        return Post.objects.filter(category=self).count()



class Post(models.Model):
     
     STATUS=(
         ('Active','Active'),
         ('Draft','Draft'),
         ('Disabled','Disabled'),
     )

     user=models.ForeignKey(User,on_delete=models.CASCADE)
     profile=models.ForeignKey(Profile,on_delete=models.CASCADE,null=True,blank=True)
     category=models.ForeignKey(Category,on_delete=models.CASCADE,null=True,blank=True)
     title=models.CharField(max_length=200)
     description=models.TextField()
     image=models.FileField(upload_to='posts/', default='default/default.png', blank=True, null=True)
     status=models.CharField(max_length=50,choices=STATUS,default='Active')
     views=models.IntegerField(default=0)
     likes=models.ManyToManyField(User,related_name='likes_user',blank=True)
     slug=models.SlugField(unique=True,null=True,blank=True)
     date=models.DateTimeField(auto_now_add=True)

     def __str__(self):
        return self.title
     class Meta:
         ordering = ['-date']
         verbose_name_plural = "Posts"

     def save(self, *args, **kwargs):
         if self.slug == "" or self.slug is None:
             self.slug = slugify(self.title)+"-"+ ShortUUIDField().uuid()[:2]
         super(Post, self).save(*args, **kwargs)


class Comment(models.Model):
    post=models.ForeignKey(Post,on_delete=models.CASCADE)
    name=models.CharField(max_length=150)
    email=models.EmailField(max_length=150)
    comment=models.TextField(null=True,blank=True)
    reply=models.TextField(null=True,blank=True)
    date=models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.post.title
    class Meta:
        ordering = ['-date']
        verbose_name_plural = "Comments"

class Bookmark(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    post=models.ForeignKey(Post,on_delete=models.CASCADE)
    date=models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.post.title
    class Meta:
        ordering = ['-date']
        verbose_name_plural = "Bookmarks"

class Notification(models.Model):
    NOTI_TYPE=(
        ('Like','Like'),
        ('Comment','Comment'),
        ('Bookmark','Bookmark'),
    )
    user=models.ForeignKey(User,on_delete=models.CASCADE,related_name='notification_user')
    post=models.ForeignKey(Post,on_delete=models.CASCADE)
    type=models.CharField(max_length=50,choices=NOTI_TYPE)
    seen=models.BooleanField(default=False)
    date=models.DateTimeField(auto_now_add=True)


    def __str__(self):
        if self.post:
            return self.post.title
        else:
            return "Notification"
    class Meta:
        ordering = ['-date']
        verbose_name_plural = "Notifications"