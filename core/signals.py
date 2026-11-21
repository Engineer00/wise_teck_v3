"""Keep old links working: when a page, blog post or success story gets a new web address (slug),
a permanent (301) redirect from the old address is added automatically (Admin → Redirects)."""

from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

from .models import BlogPost, Page, Redirect, SuccessStory

TRACKED = (Page, BlogPost, SuccessStory)


@receiver(pre_save)
def remember_old_url(sender, instance, **kwargs):
    if sender not in TRACKED or not instance.pk:
        return
    old = sender.objects.filter(pk=instance.pk).first()
    instance._old_url = old.get_absolute_url() if old is not None and not getattr(old, "draft_of_id", None) else None


@receiver(post_save)
def redirect_old_url(sender, instance, created, **kwargs):
    if sender not in TRACKED or created or getattr(instance, "draft_of_id", None):
        return
    old, new = getattr(instance, "_old_url", None), instance.get_absolute_url()
    if not old or old == new:
        return
    Redirect.objects.filter(old_path=new).delete()  # the new address is a real page again
    Redirect.objects.filter(new_path=old).update(
        new_path=new
    )  # no redirect chains: earlier redirects go straight to the new address
    Redirect.objects.update_or_create(old_path=old, defaults={"new_path": new, "permanent": True, "is_active": True})
