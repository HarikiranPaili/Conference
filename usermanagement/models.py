from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import Group




# Create your models here.

class User(AbstractUser):
    phone = models.BigIntegerField(null=True,blank=True)
    first_name = models.CharField(max_length=150,null=True,blank=True)
    last_name = models.CharField(max_length=150,null=True,blank=True)
    gender=models.CharField(max_length=30,null=True,blank=True)
    designation=models.CharField(max_length=100,null=True,blank=True)
    campus = models.CharField(max_length=100, null=True,blank=True)
    institution = models.CharField(max_length=100,null=True,blank=True)
    department = models.CharField(max_length=100, null=True,blank=True)
    u_id = models.CharField(max_length=15,null=True,blank=True)
    flag_counter = models.BooleanField(default=False)
    supervisor_name = models.CharField(max_length=30, null=True,blank=True)
    supervisor_email = models.EmailField(max_length=30, null=True,blank=True)
    supervisor_emp_id = models.CharField(max_length=30, null=True,blank=True)

    groups = models.ManyToManyField(
        Group,
        verbose_name=('groups'),
        blank=True,
        help_text=(
            'The groups this user belongs to. A user will get all permissions '
            'granted to each of their groups.'
        ),
        related_name="user",
        related_query_name="user",
        through="UserGroups"
    )

    class Meta:
        db_table = "auth_user"

    def __str__(self):
        return str(self.username)


class UserGroups(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="userOf")
    group = models.ForeignKey(Group, on_delete=models.CASCADE,related_name="groupOf")
    role = models.CharField(max_length=50)
    is_active = models.BooleanField(default=False)
    is_default = models.BooleanField(default=False)
    is_block = models.BooleanField(default=False)

    class Meta:
        db_table = "user_groups"

