from django.contrib.auth.mixins import UserPassesTestMixin
from django.core.exceptions import PermissionDenied

class AdminRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.role == 'admin'

class ViewerPermissionMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_authenticated