# -*- coding: utf-8 -*-
from django.db import models
from django.core.exceptions import ObjectDoesNotExist
from jsonfield.fields import JSONField
from cms.models import CMSPlugin


class CascadeElement(CMSPlugin):
    """
    The container to hold additional bootstrap elements.
    """
    cmsplugin_ptr = models.OneToOneField(CMSPlugin, related_name='+', parent_link=True)
    context = JSONField(null=True, blank=True, default={})

    def __unicode__(self):
        return self.plugin_class.get_identifier(self)

    @property
    def plugin_class(self):
        if not hasattr(self, '_plugin_class'):
            self._plugin_class = self.get_plugin_class()
        return self._plugin_class

    @property
    def tag_type(self):
        return self.plugin_class.tag_type

    @property
    def css_classes(self):
        css_classes = self.plugin_class.get_css_classes(self)
        return ' '.join(css_classes)

    @property
    def inline_styles(self):
        inline_styles = self.plugin_class.get_inline_styles(self)
        return ' '.join(['{0}: {1};'.format(*s) for s in inline_styles.items() if s[1]])

    @property
    def data_options(self):
        data_options = self.plugin_class.get_data_options(self)
        return ' '.join(['data-{0}={1}'.format(*o) for o in data_options.items() if o[1]])

    def get_full_context(self):
        """
        Return the context recursively, from the root element down to the current element.
        """
        context = {}
        try:
            parent = CascadeElement.objects.get(id=self.parent_id)
            context = parent.get_full_context()
        except ObjectDoesNotExist:
            pass
        context.update(self.context or {})
        return context
