"""Django's built-in admin (/django-admin/), kept as a fallback. The main panel is /admin/ (adminpanel_views)."""
from django.contrib import admin

from .models import (BlogPost, ContactMessage, FooterColumn, FooterLink, Item, NavItem, Page, Program, Redirect,
                     Revision, Section, Service, SiteSettings, SuccessStory, TeamMember)


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ["name", "email", "phone", "interest", "created_at", "is_read"]
    list_filter = ["is_read", "interest"]
    list_editable = ["is_read"]
    search_fields = ["name", "email", "phone", "message"]
    readonly_fields = ["name", "email", "phone", "interest", "message", "page", "created_at"]

    def has_add_permission(self, request):
        return False


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        return not SiteSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False


class NavChildInline(admin.TabularInline):
    model = NavItem
    fk_name = "parent"
    extra = 0
    fields = ["label", "url", "order", "is_active"]
    verbose_name_plural = "Drop-down links"


@admin.register(NavItem)
class NavItemAdmin(admin.ModelAdmin):
    list_display = ["label", "url", "order", "is_active"]
    list_editable = ["order", "is_active"]
    inlines = [NavChildInline]

    def get_queryset(self, request):
        return super().get_queryset(request).filter(parent__isnull=True)


class FooterLinkInline(admin.TabularInline):
    model = FooterLink
    extra = 0


@admin.register(FooterColumn)
class FooterColumnAdmin(admin.ModelAdmin):
    list_display = ["title", "order"]
    list_editable = ["order"]
    inlines = [FooterLinkInline]


@admin.register(Program)
class ProgramAdmin(admin.ModelAdmin):
    list_display = ["title", "link_url", "order", "is_active"]
    list_editable = ["order", "is_active"]


class SectionInline(admin.TabularInline):
    model = Section
    extra = 0
    fields = ["order", "layout", "eyebrow", "title", "is_active"]
    show_change_link = True


@admin.register(Page)
class PageAdmin(admin.ModelAdmin):
    list_display = ["title", "slug", "is_active"]
    inlines = [SectionInline]


class ItemInline(admin.StackedInline):
    model = Item
    extra = 0


@admin.register(Section)
class SectionAdmin(admin.ModelAdmin):
    list_display = ["__str__", "layout", "page", "order", "is_active"]
    list_filter = ["page", "layout"]
    list_editable = ["order", "is_active"]
    search_fields = ["title", "eyebrow", "body"]
    inlines = [ItemInline]


@admin.register(Redirect)
class RedirectAdmin(admin.ModelAdmin):
    list_display = ["old_path", "new_path", "permanent", "hits", "is_active"]
    search_fields = ["old_path", "new_path"]


@admin.register(Revision)
class RevisionAdmin(admin.ModelAdmin):
    list_display = ["object_repr", "reason", "user", "created_at"]
    list_filter = ["content_type"]
    readonly_fields = ["content_type", "object_id", "object_repr", "reason", "data", "user", "created_at"]

    def has_add_permission(self, request):
        return False


for model in (SuccessStory, TeamMember, BlogPost, Service):
    admin.site.register(model)
