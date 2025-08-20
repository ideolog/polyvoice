from django.contrib import admin
from .models import Project, Channel, Post, PostSchedule, ProjectMembership

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'description', 'created_at')
    search_fields = ('name',)
    list_filter = ('created_at',)
    ordering = ('-created_at',)


@admin.register(ProjectMembership)
class ProjectMembershipAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'project', 'role', 'joined_at')
    search_fields = ('user__email', 'project__name')
    list_filter = ('role', 'joined_at')
    ordering = ('-joined_at',)


@admin.register(Channel)
class ChannelAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'type', 'project', 'created_at')
    search_fields = ('name', 'project__name')
    list_filter = ('type', 'created_at')
    ordering = ('-created_at',)


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('id', 'project', 'status', 'created_at')
    search_fields = ('project__name', 'content')
    list_filter = ('status', 'created_at')
    ordering = ('-created_at',)


@admin.register(PostSchedule)
class PostScheduleAdmin(admin.ModelAdmin):
    list_display = ('id', 'post', 'channel', 'scheduled_time', 'published_at')
    search_fields = ('post__content', 'channel__name')
    list_filter = ('scheduled_time', 'published_at')
    ordering = ('-scheduled_time',)
