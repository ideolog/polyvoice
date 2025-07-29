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
    ordering = ('-created_at',)
    list_display = ('id', 'project', 'status', 'created_at')
    search_fields = ('project__name', 'content')
    list_filter = ('status', 'created_at')
