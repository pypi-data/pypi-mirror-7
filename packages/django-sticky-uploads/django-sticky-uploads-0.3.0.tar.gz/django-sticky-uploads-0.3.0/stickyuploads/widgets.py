from __future__ import unicode_literals

from django import forms
from django.core.urlresolvers import reverse_lazy
from django.utils.safestring import mark_safe

from . import __version__
from .utils import open_stored_file 


class StickyUploadWidget(forms.ClearableFileInput):
    """Customize file uploader widget to handle AJAX upload and preserve value."""

    class Media(object):
        js = (
            'stickyuploads/js/django-uploader.bundle.min.js?v=%s' % __version__,
        )

    def __init__(self, *args, **kwargs):
        self.url = kwargs.pop('url', reverse_lazy('sticky-upload-default'))
        super(StickyUploadWidget, self).__init__(*args, **kwargs)

    def get_hidden_name(self, name):
        """Get expected hidden name from the original field name."""
        return '_' + name

    def value_from_datadict(self, data, files, name):
        """Returns uploaded file from serialized value."""
        upload = super(StickyUploadWidget, self).value_from_datadict(data, files, name)
        if upload is not None:
            # File was posted or cleared as normal
            return upload
        else:
            # Try the hidden input
            hidden_name = self.get_hidden_name(name)
            value = data.get(hidden_name, None)
            if value is not None:
                upload = open_stored_file(value, self.url)
                if upload is not None:
                    setattr(upload, '_seralized_location', value)
        return upload

    def render(self, name, value, attrs=None):
        """Include a hidden input to stored the serialized upload value."""
        location = getattr(value, '_seralized_location', '')
        if location and not hasattr(value, 'url'):
            value.url = '#'
        attrs = attrs or {}
        attrs.update({'data-upload-url': self.url})
        parent = super(StickyUploadWidget, self).render(name, value, attrs=attrs)
        hidden_name = self.get_hidden_name(name)
        hidden = forms.HiddenInput().render(hidden_name, location)
        return mark_safe(parent + hidden)