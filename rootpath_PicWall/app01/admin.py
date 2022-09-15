from django.contrib import admin
from app02.models import Tools

# Register your models here.
class ToolsAdmin(admin.ModelAdmin):
    list_display = ('tools_name','tools_desc',)
    ordering = ('-tools_name',)


admin.site.register(Tools,ToolsAdmin)