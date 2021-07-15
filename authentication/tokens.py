import six
from django.contrib.auth.tokens import PasswordResetTokenGenerator


class _TokenGenFactory(PasswordResetTokenGenerator):
    def _make_hash_value(self, user, timestamp):
        return (
            six.text_type(user.email) + six.text_type(timestamp) +
            six.text_type(user.is_active)
        )


TokenGenerator = _TokenGenFactory()
