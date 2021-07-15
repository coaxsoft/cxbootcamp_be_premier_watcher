import uuid

from django.db import models
from django.utils.text import slugify

from static_content.utils import upload_to


class Premier(models.Model):
    user = models.ForeignKey('authentication.User', models.CASCADE, null=True, blank=True,
                             help_text="The user that added the premier")
    name = models.CharField(max_length=255, help_text="The name of the Premier")
    url = models.SlugField(unique=True, max_length=255, help_text="Relative url of the Premier")
    description = models.TextField(null=True, blank=True)
    logo = models.ImageField(upload_to=upload_to, null=True, blank=True, help_text="The logo of the Premier")

    is_active = models.BooleanField(default=False, help_text="Designates whether to display Premier on web-site or not")

    premier_at = models.DateTimeField(help_text="The time when the premier is released")
    last_updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'premiers'
        indexes = [
            models.Index(fields=['premier_at'])
        ]
        ordering = ('-id',)

    def save(self, *args, **kwargs):
        if self.id:
            self.url = self._build_url()
        else:
            self.url = f"rand:{uuid.uuid4()}"

        super().save(*args, **kwargs)

        if self.url.startswith("rand:"):
            self.url = self._build_url()
            self.save()

    def __str__(self):
        return f"{self.id}, {self.name}"

    def _build_url(self):
        return f"{self.id}-{slugify(self.name)}"
