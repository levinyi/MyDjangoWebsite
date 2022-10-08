from django.contrib import admin
from .models import Tools

# Register your models here.
class ToolsAdmin(admin.ModelAdmin):
    list_display = ('tools_name','tools_desc','tools_freq')
    list_filter = ('tools_freq',)

admin.site.register(Tools, ToolsAdmin)