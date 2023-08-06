# -*- coding: utf-8 -*-
from django.conf import settings

CMS_CASCADE_BOOTSTRAP3_BREAKPOINT = getattr(settings, 'CMS_CASCADE_BOOTSTRAP3_BREAKPOINT', 'lg')
CMS_CASCADE_LEAF_PLUGINS = getattr(settings, 'CMS_CASCADE_LEAF_PLUGINS', [])

if not 'TextPlugin' in CMS_CASCADE_LEAF_PLUGINS:
    try:
        import djangocms_text_ckeditor
        CMS_CASCADE_LEAF_PLUGINS.append('TextPlugin')
    except ImportError:
        pass
if not 'FilerImagePlugin' in CMS_CASCADE_LEAF_PLUGINS:
    try:
        import filer
        CMS_CASCADE_LEAF_PLUGINS.append('FilerImagePlugin')
    except ImportError:
        pass
