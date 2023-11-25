from django.contrib import admin
from .models import Inquiry, InquiryGeneSeqValidation, Tools, Result

# Register your models here.
class ToolsAdmin(admin.ModelAdmin):
    list_display = ('tools_name','tools_desc','tools_freq')
    list_filter = ('tools_freq',)

class ResultAdmin(admin.ModelAdmin):
    list_display = ('unique_id','tools_name','project_name','result_path','status','user_ip','created_at','end_time')
    list_filter = ('end_time',)

class InquiryGeneSeqValidationAdmin(admin.ModelAdmin):
    list_display = ('user','inquiry_id','gene_name','seq5NC','seq3NC','seqAA','forbid_seq')
    list_filter = ('user',)

class InquiryAdmin(admin.ModelAdmin):
    list_display = ('id','user','gene_number','validated_number','create_date','status')
    list_filter = ('user',)
admin.site.register(Tools, ToolsAdmin)
admin.site.register(Result, ResultAdmin)
admin.site.register(InquiryGeneSeqValidation, InquiryGeneSeqValidationAdmin)
admin.site.register(Inquiry, InquiryAdmin)