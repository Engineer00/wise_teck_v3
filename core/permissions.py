"""Who may open the admin panel and the staff-only previews."""

from django.contrib.auth.decorators import login_required, user_passes_test


def staff_required(view):
    """Signed-in staff only; everyone else goes to the admin sign-in page."""
    return login_required(login_url="adminpanel_login")(
        user_passes_test(lambda u: u.is_staff, login_url="adminpanel_login")(view)
    )
