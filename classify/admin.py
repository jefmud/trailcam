from django.contrib import admin

from django.contrib.admin import DateFieldListFilter

from . import models

# site branding
brand = "WFU TrailCam"
admin.site.site_header = "{} Observations Database".format(brand)
admin.site.site_title = "{}".format(brand)
admin.site.index_title = "{}".format(brand)

#admin.site.register(models.Image)
admin.site.register(models.Site)
admin.site.register(models.Species)
admin.site.register(models.Person)
admin.site.register(models.ToDo)
#admin.site.register(models.Observation)

class CommentAdmin(admin.ModelAdmin):
    fields = ('image_tag','user','text',)
    readonly_fields = ('image_tag',)
    list_filter = ('user', 'text', ('modified_on', DateFieldListFilter))
    search_fields = ['text','user']

class ImageAdmin(admin.ModelAdmin):
    # these administrative models allow us to add the image_tag (which is a presentation field that derives from image)
    fields = ('image_tag', 'image_date','url', 'site', 'date')
    readonly_fields = ('image_tag','url','image_date','site','date')
    list_display = ['site','date','url']
    list_filter = ('site',('date',DateFieldListFilter))
    search_fields = ['date','url']
    
class ObservationAdmin(admin.ModelAdmin):
    # see ImageAdmin model
    fields = ('image_tag', 'site', 'date_str', 'species', 'count', 'females', 'males', 'young', 'person',)
    readonly_fields = ('image_tag', 'site', 'date_str')
    search_fields = ['date_str']
    list_display = ['site','date_str','person','count','males','females']
    list_filter = ('site','person',)
    
admin.site.register(models.Image, ImageAdmin)
admin.site.register(models.Observation, ObservationAdmin)
admin.site.register(models.Comment, CommentAdmin)