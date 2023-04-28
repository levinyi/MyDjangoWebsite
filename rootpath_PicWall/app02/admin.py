from django.contrib import admin
from app02.models import Tools, Data

# Register your models here.
class ToolsAdmin(admin.ModelAdmin):
    list_display = ('tools_name','tools_desc',)
    ordering = ('-tools_name',)


class DataAdmin(admin.ModelAdmin):
    list_display = ('data_path','area',)
    ordering = ('data_path',)

admin.site.register(Tools,ToolsAdmin)
admin.site.register(Data, DataAdmin)
# Register your models here.
