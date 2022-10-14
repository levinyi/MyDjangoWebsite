from django.contrib import admin

# Register your models here.

from .models import EndPoint, CompanyInfo, Data

class EndPointAdmin(admin.ModelAdmin):
    list_display = ('name','endpoint',)
    ordering = ('name','endpoint',)

class CompanyInfoAdmin(admin.ModelAdmin):
    list_display = ('name','endpoint','bucket','KeyID','KeySecret',)
    ordering = ('name','endpoint',)

class DataAdmin(admin.ModelAdmin):
    list_display = ('data_path', 'ctime', 'company', 'area')
    ordering = ('ctime',)

admin.site.register(EndPoint, EndPointAdmin)
admin.site.register(CompanyInfo, CompanyInfoAdmin)
admin.site.register(Data, DataAdmin)
