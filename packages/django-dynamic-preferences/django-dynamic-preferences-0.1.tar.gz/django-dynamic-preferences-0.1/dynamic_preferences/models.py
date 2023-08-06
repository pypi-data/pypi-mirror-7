"""
Preference models, queryset and managers that handle the logic for persisting preferences.
"""

from django.db import models
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.db.models.query import QuerySet
from utils import update
from django.conf import settings
from django.utils.functional import cached_property
from dynamic_preferences.registries import user_preferences_registry, site_preferences_registry, global_preferences_registry

class PreferenceSite(Site):

    class Meta:
        proxy = True
        app_label = 'dynamic_preferences'


class PreferenceUser(User):
    class Meta:
        proxy = True
        app_label = 'dynamic_preferences'


class BasePreferenceModel(models.Model):
    """
    A base model with common logic for all preferences models.
    """

    #: The section under which the preference is declared
    section = models.TextField(max_length=255, db_index=True, blank=True, null=True, default=None)

    #: a name for the preference
    name = models.TextField(max_length=255, db_index=True)

    #: a value, serialized to a string. This field should not be accessed directly, use :py:attr:`BasePreferenceModel.value` instead
    raw_value = models.TextField(null=True, blank=True)

    #: Keep a reference to the whole preference registry.
    #: In order to map the Preference Model Instance to the Preference object.
    registry = None

    class Meta:
        abstract = True
        app_label = 'dynamic_preferences'


    def __init__(self, *args, **kwargs):
        # Check if the model is already saved in DB

        v = kwargs.pop("value", None)

        super(BasePreferenceModel, self).__init__(*args, **kwargs)

        new = self.pk is None

        if new:
            if v is not None:
                self.value = v
            else:
                self.value = self.preference.default



    @cached_property
    def preference(self):
        return self.registry.get(section=self.section, name=self.name)

    def set_value(self, value):
        """
            Save serialized self.value to self.raw_value
        """
        self.raw_value = self.preference.serializer.serialize(value)

    def get_value(self):
        """
            Return deserialized self.raw_value
        """
        return self.preference.serializer.deserialize(self.raw_value)

    value = property(get_value, set_value)

    def __unicode__(self):
        return self.preference.identifier()

class GlobalPreferenceModel(BasePreferenceModel):

    registry = global_preferences_registry

    class Meta:
        unique_together = ('section', 'name')
        app_label = 'dynamic_preferences'

        verbose_name = "global preference"
        verbose_name_plural = "global preferences"


class UserPreferenceModel(BasePreferenceModel):

    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="preferences")
    registry = user_preferences_registry

    class Meta:
        unique_together = ('user', 'section', 'name')
        app_label = 'dynamic_preferences'
        verbose_name = "user preference"
        verbose_name_plural = "user preferences"

class SitePreferenceModel(BasePreferenceModel):

    site = models.ForeignKey(Site, related_name="preferences")
    registry = site_preferences_registry

    class Meta:
        unique_together = ('site', 'section', 'name')
        app_label = 'dynamic_preferences'
        verbose_name = "site preference"
        verbose_name_plural = "site preferences"


global_preferences = GlobalPreferenceModel.objects
site_preferences = SitePreferenceModel.objects
user_preferences = UserPreferenceModel.objects