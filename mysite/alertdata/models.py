from django.db import models


class Aircraft(models.Model):
    city = models.CharField(max_length=45)
    category = models.CharField(max_length=45, blank=True, null=True)
    number = models.CharField(max_length=45, blank=True, null=True)
    village = models.CharField(max_length=45, blank=True, null=True)
    address = models.CharField(max_length=255)
    longtitude = models.DecimalField(primary_key=True, max_digits=65, decimal_places=30)
    latitude = models.DecimalField(max_digits=30, decimal_places=27)
    capacity = models.CharField(max_length=45)
    basement = models.CharField(max_length=45, blank=True, null=True)
    unit = models.CharField(max_length=45, blank=True, null=True)
    note = models.CharField(max_length=45, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'aircraft'
        unique_together = (('longtitude', 'latitude', 'city', 'capacity', 'address'),)


class AlertLocation(models.Model):
    alert = models.OneToOneField('RealtimeAlert', models.DO_NOTHING, primary_key=True)
    location = models.CharField(max_length=100)
    category = models.CharField(max_length=45, blank=True, null=True)
    event = models.CharField(max_length=45, blank=True, null=True)
    urgency = models.CharField(max_length=45, blank=True, null=True)
    severity = models.CharField(max_length=45, blank=True, null=True)
    certainty = models.CharField(max_length=45, blank=True, null=True)
    effective = models.CharField(max_length=45, blank=True, null=True)
    expires = models.CharField(max_length=45, blank=True, null=True)
    sendername = models.CharField(db_column='senderName', max_length=45, blank=True, null=True)  # Field name made lowercase.
    headline = models.CharField(max_length=255, blank=True, null=True)
    description = models.CharField(max_length=255, blank=True, null=True)
    web = models.CharField(max_length=255, blank=True, null=True)
    serverity_level = models.CharField(max_length=45, blank=True, null=True)
    alert_criteria = models.CharField(max_length=45, blank=True, null=True)
    alert_color = models.CharField(max_length=45, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'alert_location'
        unique_together = (('alert', 'location'),)


class AuthGroup(models.Model):
    name = models.CharField(unique=True, max_length=150)

    class Meta:
        managed = False
        db_table = 'auth_group'


class AuthGroupPermissions(models.Model):
    id = models.BigAutoField(primary_key=True)
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)
    permission = models.ForeignKey('AuthPermission', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_group_permissions'
        unique_together = (('group', 'permission'),)


class AuthPermission(models.Model):
    name = models.CharField(max_length=255)
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING)
    codename = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'auth_permission'
        unique_together = (('content_type', 'codename'),)


class AuthUser(models.Model):
    password = models.CharField(max_length=128)
    last_login = models.DateTimeField(blank=True, null=True)
    is_superuser = models.IntegerField()
    username = models.CharField(unique=True, max_length=150)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    email = models.CharField(max_length=254)
    is_staff = models.IntegerField()
    is_active = models.IntegerField()
    date_joined = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'auth_user'


class AuthUserGroups(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_user_groups'
        unique_together = (('user', 'group'),)


class AuthUserUserPermissions(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    permission = models.ForeignKey(AuthPermission, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_user_user_permissions'
        unique_together = (('user', 'permission'),)


class DjangoAdminLog(models.Model):
    action_time = models.DateTimeField()
    object_id = models.TextField(blank=True, null=True)
    object_repr = models.CharField(max_length=200)
    action_flag = models.PositiveSmallIntegerField()
    change_message = models.TextField()
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING, blank=True, null=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'django_admin_log'


class DjangoContentType(models.Model):
    app_label = models.CharField(max_length=100)
    model = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'django_content_type'
        unique_together = (('app_label', 'model'),)


class DjangoMigrations(models.Model):
    id = models.BigAutoField(primary_key=True)
    app = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    applied = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_migrations'


class DjangoSession(models.Model):
    session_key = models.CharField(primary_key=True, max_length=40)
    session_data = models.TextField()
    expire_date = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_session'


class RealtimeAlert(models.Model):
    alert_id = models.AutoField(primary_key=True)
    identifier = models.CharField(max_length=100, blank=True, null=True)
    sender = models.CharField(max_length=80, blank=True, null=True)
    sent = models.CharField(max_length=45, blank=True, null=True)
    status = models.CharField(max_length=45, blank=True, null=True)
    msgtype = models.CharField(db_column='msgType', max_length=45, blank=True, null=True)  # Field name made lowercase.
    scope = models.CharField(max_length=45, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'realtime_alert'


class Shelter(models.Model):
    shelter_id = models.IntegerField(primary_key=True)
    city = models.CharField(max_length=255, db_collation='utf8_general_ci', blank=True, null=True)
    village = models.CharField(max_length=45, db_collation='utf8_general_ci', blank=True, null=True)
    address = models.CharField(max_length=255, db_collation='utf8_general_ci', blank=True, null=True)
    longtitude = models.DecimalField(max_digits=10, decimal_places=7, blank=True, null=True)
    latitude = models.DecimalField(max_digits=10, decimal_places=7, blank=True, null=True)
    name = models.CharField(max_length=255, db_collation='utf8_general_ci', blank=True, null=True)
    capacity = models.IntegerField(blank=True, null=True)
    manager_name = models.CharField(max_length=255, db_collation='utf8_general_ci', blank=True, null=True)
    manager_phone = models.CharField(max_length=45, blank=True, null=True)
    indoor = models.CharField(max_length=10, db_collation='utf8_general_ci', blank=True, null=True)
    outdoor = models.CharField(max_length=10, db_collation='utf8_general_ci', blank=True, null=True)
    suitable_for_weak = models.CharField(max_length=10, db_collation='utf8_general_ci', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'shelter'


class ShelterAcceptVillage(models.Model):
    shelter = models.OneToOneField(Shelter, models.DO_NOTHING, primary_key=True)
    accept_village = models.CharField(max_length=255)

    class Meta:
        managed = False
        db_table = 'shelter_accept_village'
        unique_together = (('shelter', 'accept_village'),)


class ShelterDisaster(models.Model):
    shelter = models.OneToOneField(Shelter, models.DO_NOTHING, primary_key=True)
    disaster = models.CharField(max_length=45)

    class Meta:
        managed = False
        db_table = 'shelter_disaster'
        unique_together = (('shelter', 'disaster'),)
