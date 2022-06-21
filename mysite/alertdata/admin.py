from django.contrib import admin
from .models import Aircraft, AuthGroup, AuthGroupPermissions, AuthPermission, AuthUser, AuthUserGroups, RealtimeAlert
from .models import AuthUserUserPermissions, DjangoAdminLog, DjangoContentType, DjangoMigrations, DjangoSession, Shelter, ShelterAcceptVillage, ShelterDisaster
admin.site.register(Aircraft)
admin.site.register(AuthGroup)
admin.site.register(AuthGroupPermissions)
admin.site.register(AuthPermission)
admin.site.register(AuthUserGroups)
admin.site.register(AuthUserUserPermissions)
admin.site.register(DjangoAdminLog)
admin.site.register(DjangoContentType)
admin.site.register(DjangoMigrations)
admin.site.register(DjangoSession)
admin.site.register(RealtimeAlert)
admin.site.register(Shelter)
admin.site.register(ShelterAcceptVillage)
admin.site.register(ShelterDisaster)