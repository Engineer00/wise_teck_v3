from django.urls import path

from . import adminpanel_views as views

urlpatterns = [
    path("login/", views.AdminLoginView.as_view(), name="adminpanel_login"),
    path("logout/", views.admin_logout, name="adminpanel_logout"),
    path("", views.dashboard, name="adminpanel_dashboard"),
    path("messages/<int:pk>/toggle-read/", views.contact_mark_read, name="adminpanel_contact_toggle_read"),
    path("pages/<int:pk>/create-draft/", views.page_create_draft, name="adminpanel_create_draft"),
    path("pages/<int:pk>/publish/", views.page_publish_draft, name="adminpanel_publish_draft"),
    path("versions/<int:pk>/restore/", views.revision_restore, name="adminpanel_restore"),
    path("versions/<int:pk>/as-draft/", views.revision_to_draft, name="adminpanel_version_draft"),
    path("<slug:resource>/", views.resource_list, name="adminpanel_list"),
    path("<slug:resource>/add/", views.resource_create, name="adminpanel_add"),
    path("<slug:resource>/<int:pk>/change/", views.resource_change, name="adminpanel_change"),
    path("<slug:resource>/<int:pk>/delete/", views.resource_delete, name="adminpanel_delete"),
]
