from django.contrib import admin
from davvy.models import *
from django import forms

class PropInline(admin.TabularInline):
    model = Prop

class ResourceAdminForm(forms.ModelForm):
    class Meta:
        model = Resource
        widgets = {
            'file':forms.TextInput(attrs={'size':'64'})
        }

class ResourceAdmin(admin.ModelAdmin):
    list_display = ('__unicode__', 'displayname', 'user')
    form = ResourceAdminForm
    inlines = [ PropInline ]
    

admin.site.register(Resource, ResourceAdmin)
admin.site.register(Prop)
