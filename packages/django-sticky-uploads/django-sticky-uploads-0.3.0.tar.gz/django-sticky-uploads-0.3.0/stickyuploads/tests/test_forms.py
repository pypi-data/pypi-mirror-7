from __future__ import unicode_literals

from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils import unittest

from mock import patch

from ..forms import UploadForm
from ..utils import serialize_upload
from .base import MockStorage


class UploadFormTestCase(unittest.TestCase):
    """Default upload form logic."""

    def test_basic_stash(self):
        """
        Stash file using the passed storage.
        """
        data = {}
        files = {'upload': SimpleUploadedFile('test.jpg', content=b'X')}
        form = UploadForm(data=data, files=files)
        storage = MockStorage()
        result = form.stash(storage, '/upload/default/')
        expected = {
            'filename': 'test.jpg',
            'url': '/uploads/test.jpg',
            'stored': serialize_upload('test.jpg', storage, '/upload/default/'),
        }
        self.assertEqual(result, expected)

    def test_invalid_stash(self):
        """
        Stash result should be empty when form is not valid.
        """
        form = UploadForm(data={}, files={})
        storage = MockStorage()
        result = form.stash(storage, '/upload/default/')
        self.assertEqual(result, {})

    def test_stash_url(self):
        """
        Stash result should contain url if implement by
        the storage class otherwise None.
        """
        data = {}
        files = {'upload': SimpleUploadedFile('test.jpg', content=b'X')}
        form = UploadForm(data=data, files=files)
        storage = MockStorage()
        with patch.object(storage, 'url') as mock_url:
            mock_url.side_effect = NotImplementedError
            result = form.stash(storage, '/upload/default/')
        expected = {
            'filename': 'test.jpg',
            'url': None,
            'stored': serialize_upload('test.jpg', storage, '/upload/default/'),
        }
        self.assertEqual(result, expected)