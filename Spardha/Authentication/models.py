from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, Group


class AccountManager(BaseUserManager):
    def create_user(self, username, email,  password=None):
        if not username:
            raise ValueError("The username must be set")
        if not email:
            raise ValueError("The email must be set")

        user = self.model(username=username)
        user.email = email
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password):
        user = self.create_user(
            password=password,
            username=username,
            email=email,
        )
        user.is_admin = True
        user.is_staff = True
        user.is_superuser = True
        user.is_active = True
        user.save(using=self._db)
        return user


class UserAccount(AbstractBaseUser):
    username = models.CharField(max_length=100, unique=True)
    email = models.EmailField(verbose_name="email", max_length=60, unique=True)
    date_joined = models.DateTimeField(verbose_name="date joined", auto_now_add=True)
    is_admin = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)
    name = models.CharField(max_length=100)
    institution_name = models.CharField(max_length=200, blank=False, null=False)
    designation = models.CharField(max_length=100, blank=False, null=False)
    phone_no = models.CharField(max_length=10, blank=False, null=False)
    group = models.ForeignKey(Group, on_delete=models.CASCADE ,blank=True, null=True)

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["email"]

    objects = AccountManager()

    def __str__(self):
        if self.is_admin:
            return "{} (admin)".format(self.username)
        else:
            return f"{self.name}"

    # Checking permissions
    def has_perm(self, perm, obj=None):
        if self.is_admin:
            return True
        if self.is_staff and perm.split('.')[1] in self.get_all_permissions():
            return True
        else: 
            print(self.get_all_permissions())
        return False
    
    # return all the user permission
    def get_all_permissions(self, obj=None):
        all_perm=[]
        if self.group is None:
            return all_perm
        for perm in self.group.permissions.all():
            all_perm.append(perm.codename)
        return all_perm

    # Does this user have permission to view this app?
    def has_module_perms(self, app_label):
        return True

