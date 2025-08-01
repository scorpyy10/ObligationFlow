from django.contrib import admin

from .models import *


# Register your models here.
admin.site.register(Document)
admin.site.register(DocumentResponse)
admin.site.register(ObligationMetadata)
admin.site.register(RiskTrackingRecord)
admin.site.register(Milestone)

class Document(admin.ModelAdmin):
    pass