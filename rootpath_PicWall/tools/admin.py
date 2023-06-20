from django.contrib import admin
from .models import Tools, Result

# Register your models here.
class ToolsAdmin(admin.ModelAdmin):
    list_display = ('tools_name','tools_desc','tools_freq')
    list_filter = ('tools_freq',)

class ResultAdmin(admin.ModelAdmin):
    list_display = ('unique_id','tools_name','project_name','result_path','status','user_ip','created_at','end_time')
    list_filter = ('end_time',)

admin.site.register(Tools, ToolsAdmin)
admin.site.register(Result, ResultAdmin)