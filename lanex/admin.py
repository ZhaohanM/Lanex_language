from django.contrib import admin
from lanex.models import Language, LanguageRequest, UserProfile, Comment

class LanguageAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug':('name',)}

class RequestAdmin(admin.ModelAdmin):
    list_display = ['title', 'language', 'description']

class CommentAdmin(admin.ModelAdmin):
    list_display = ('creator', 'body', 'request', 'created_on', 'active')
    list_filter = ('active', 'created_on')
    search_fields = ('creator', 'body')
    actions = ['approve_comments']

    def approve_comments(self, request, queryset):
        queryset.update(active=True)

admin.site.register(Comment, CommentAdmin)

admin.site.register(Language, LanguageAdmin)
admin.site.register(LanguageRequest, RequestAdmin)
admin.site.register(UserProfile)