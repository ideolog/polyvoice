from django.contrib import admin


from .models import Project, Channel, Post

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'user', 'tone', 'frequency', 'created_at')
    search_fields = ('name', 'user__email')
    list_filter = ('tone', 'frequency', 'created_at')
    ordering = ('-created_at',)

@admin.register(Channel)
class ChannelAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'type', 'project', 'created_at')
    search_fields = ('name', 'project__name')
    list_filter = ('type', 'created_at')
    ordering = ('-created_at',)

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('id', 'project', 'channel', 'status', 'scheduled_time', 'published_at', 'created_at')
    search_fields = ('content', 'project__name')
    list_filter = ('status', 'created_at')
    ordering = ('-created_at',)
