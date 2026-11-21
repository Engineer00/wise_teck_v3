from django.conf import settings
from django.conf.urls.static import static
from django.templatetags.static import static as static_url
from django.urls import include, path, re_path
from django.views.generic import RedirectView

from core import views

urlpatterns = [
    path("admin/", include("core.adminpanel.urls")),  # Wise-Teck admin panel (the original site's panel)
    re_path(
        r"^adminpanel/(?P<rest>.*)$", RedirectView.as_view(url="/admin/%(rest)s", query_string=True, permanent=False)
    ),  # the original site's address
    path("robots.txt", views.robots_txt, name="robots_txt"),
    # old browsers and crawlers ask for /favicon.ico
    path("favicon.ico", RedirectView.as_view(url=static_url("img/favicon.png"), permanent=True)),
    path("sitemap.xml", views.sitemap_xml, name="sitemap_xml"),
    path("preview/page/<int:pk>/", views.preview_page, name="preview_page"),
    path("preview/version/<int:pk>/", views.preview_revision, name="preview_revision"),
    path("blog/<slug:slug>/", views.blog_detail, name="blog_detail"),
    path("success-stories/<slug:slug>/", views.story_detail, name="story_detail"),
    path("", views.page, name="home"),
    path("<slug:slug>/", views.page, name="page"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

handler404 = "core.views.not_found"
