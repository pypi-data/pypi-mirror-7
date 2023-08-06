# -*- coding: utf-8 -*-

from pytz import utc, timezone as pytz_timezone
import wtforms
import bleach
from flask import json

from .widgets import TinyMce3, TinyMce4, DateTimeInput, HiddenMultiInput

__all__ = ['SANITIZE_TAGS', 'SANITIZE_ATTRIBUTES',
    'TinyMce3Field', 'TinyMce4Field', 'RichTextField', 'DateTimeField', 'HiddenMultiField', 'MarkdownField', 'ImgeeField']


# Default tags and attributes to allow in HTML sanitization
SANITIZE_TAGS = ['p', 'br', 'strong', 'em', 'sup', 'sub', 'h3', 'h4', 'h5', 'h6', 'ul', 'ol', 'li', 'a', 'blockquote', 'code']
SANITIZE_ATTRIBUTES = {'a': ['href', 'title', 'target']}


class TinyMce3Field(wtforms.fields.TextAreaField):
    """
    Rich text field using TinyMCE 3.
    """
    widget = TinyMce3()

    def __init__(self,
            # WTForms fields
            label=u'',
            validators=None,
            filters=(),
            description=u'',
            id=None,
            default=None,
            widget=None,
            _form=None,
            _name=None,
            _prefix='',

            # Additional fields
            content_css=None,
            linkify=True, nofollow=True,
            tinymce_options=None,
            sanitize_tags=None, sanitize_attributes=None, **kwargs):

        super(TinyMce3Field, self).__init__(label=label, validators=validators, filters=filters,
            description=description, id=id, default=default, widget=widget, _form=_form, _name=_name,
            _prefix=_prefix, **kwargs)

        if tinymce_options is None:
            tinymce_options = {}
        else:
            # Clone the dict to preserve local edits
            tinymce_options = dict(tinymce_options)

        # Set defaults for TinyMCE
        tinymce_options.setdefault('theme', "advanced")
        tinymce_options.setdefault('plugins', "")
        tinymce_options.setdefault('theme_advanced_buttons1',
            "bold,italic,|,sup,sub,|,bullist,numlist,|,link,unlink,|,blockquote,|,removeformat,code")
        tinymce_options.setdefault('theme_advanced_buttons2', "")
        tinymce_options.setdefault('theme_advanced_buttons3', "")
        tinymce_options.setdefault('blockformats', "p,h3,h4,h5,h6,blockquote,dt,dd")
        tinymce_options.setdefault('width', "100%")
        tinymce_options.setdefault('height', "159")
        tinymce_options.setdefault('valid_elements',
            "p,br,strong/b,em/i,sup,sub,h3,h4,h5,h6,ul,ol,li,a[!href|title|target],blockquote,code")
        tinymce_options.setdefault('theme_advanced_toolbar_location', "top")
        tinymce_options.setdefault('theme_advanced_toolbar_align', "left")
        tinymce_options.setdefault('theme_advanced_statusbar_location', "bottom")
        tinymce_options.setdefault('theme_advanced_resizing', True)
        tinymce_options.setdefault('theme_advanced_path', False)
        tinymce_options.setdefault('relative_urls', False)

        # Remove options that cannot be set by callers
        tinymce_options.pop('content_css', None)
        tinymce_options.pop('script_url', None)
        tinymce_options.pop('setup', None)

        if sanitize_tags is None:
            sanitize_tags = SANITIZE_TAGS
        if sanitize_attributes is None:
            sanitize_attributes = SANITIZE_ATTRIBUTES

        self.linkify = linkify
        self.nofollow = nofollow
        self.tinymce_options = tinymce_options

        self._content_css = content_css
        self.sanitize_tags = sanitize_tags
        self.sanitize_attributes = sanitize_attributes

    @property
    def content_css(self):
        if callable(self._content_css):
            return self._content_css()
        else:
            return self._content_css

    def process_formdata(self, valuelist):
        super(TinyMce3Field, self).process_formdata(valuelist)
        # Sanitize data
        self.data = bleach.clean(self.data,
            tags=self.sanitize_tags,
            attributes=self.sanitize_attributes)
        if self.linkify:
            if self.nofollow:
                self.data = bleach.linkify(self.data)
            else:
                self.data = bleach.linkify(self.data, callbacks=[])


class TinyMce4Field(wtforms.fields.TextAreaField):
    """
    Rich text field using TinyMCE 4.
    """
    widget = TinyMce4()

    def __init__(self,
            # WTForms fields
            label=u'',
            validators=None,
            filters=(),
            description=u'',
            id=None,
            default=None,
            widget=None,
            _form=None,
            _name=None,
            _prefix='',

            # Additional fields
            content_css=None,
            linkify=True, nofollow=True,
            tinymce_options=None,
            sanitize_tags=None, sanitize_attributes=None, **kwargs):

        super(TinyMce4Field, self).__init__(label=label, validators=validators, filters=filters,
            description=description, id=id, default=default, widget=widget, _form=_form, _name=_name,
            _prefix=_prefix, **kwargs)

        if tinymce_options is None:
            tinymce_options = {}
        else:
            # Clone the dict to preserve local edits
            tinymce_options = dict(tinymce_options)

        # Set defaults for TinyMCE
        tinymce_options.setdefault('plugins', "autolink autoresize link lists paste searchreplace")
        tinymce_options.setdefault('toolbar', "bold italic | bullist numlist | link unlink | searchreplace undo redo")
        tinymce_options.setdefault('width', "100%")
        tinymce_options.setdefault('height', "400")
        tinymce_options.setdefault('valid_elements',
            "p,br,strong/b,em/i,sup,sub,h3,h4,h5,h6,ul,ol,li,a[!href|title|target],blockquote,code")
        tinymce_options.setdefault('statusbar', False)
        tinymce_options.setdefault('menubar', False)
        tinymce_options.setdefault('resize', True)

        # Remove options that cannot be set by callers
        tinymce_options.pop('content_css', None)
        tinymce_options.pop('script_url', None)
        tinymce_options.pop('setup', None)

        if sanitize_tags is None:
            sanitize_tags = SANITIZE_TAGS
        if sanitize_attributes is None:
            sanitize_attributes = SANITIZE_ATTRIBUTES

        self.linkify = linkify
        self.nofollow = nofollow
        self.tinymce_options = tinymce_options

        self._content_css = content_css
        self.sanitize_tags = sanitize_tags
        self.sanitize_attributes = sanitize_attributes

    @property
    def content_css(self):
        if callable(self._content_css):
            return self._content_css()
        else:
            return self._content_css

    def process_formdata(self, valuelist):
        super(TinyMce4Field, self).process_formdata(valuelist)
        # Sanitize data
        self.data = bleach.clean(self.data,
            tags=self.sanitize_tags,
            attributes=self.sanitize_attributes)
        if self.linkify:
            if self.nofollow:
                self.data = bleach.linkify(self.data)
            else:
                self.data = bleach.linkify(self.data, callbacks=[])


#: Compatibility name
RichTextField = TinyMce3Field


class DateTimeField(wtforms.fields.DateTimeField):
    """
    A text field which stores a `datetime.datetime` matching a format.
    """
    widget = DateTimeInput()

    def __init__(self, label=None, validators=None,
            format='%Y-%m-%d %I:%M%p', timezone=None, **kwargs):
        super(DateTimeField, self).__init__(label, validators, **kwargs)
        self.format = format
        self.timezone = timezone
        self._timezone_converted = None

    @property
    def timezone(self):
        return self._timezone

    @timezone.setter
    def timezone(self, value):
        self._timezone = value
        if value:
            self.tz = pytz_timezone(value)
        else:
            self.tz = utc

    def _value(self):
        if self.data:
            if self.timezone:
                if self.data.tzinfo is None:
                    data = self.tz.normalize(utc.localize(self.data).astimezone(self.tz))
                else:
                    data = self.tz.normalize(self.data.astimezone(self.tz))
            else:
                data = self.data
            value = data.strftime(self.format)
        else:
            value = ''
        return value

    def process_formdata(self, valuelist):
        super(DateTimeField, self).process_formdata(valuelist)
        self._timezone_converted = False

    def pre_validate(self, form):
        if self._timezone_converted is False:
            # Convert from user timezone back to UTC, then discard tzinfo
            self.data = self.tz.localize(self.data).astimezone(utc).replace(tzinfo=None)
            self._timezone_converted = True


class HiddenMultiField(wtforms.fields.TextField):
    """
    A hidden field that stores multiple comma-separated values, meant to be
    used as an Ajax widget target. The optional ``separator`` parameter
    can be used to specify an alternate separator character (default ``','``).
    """
    widget = HiddenMultiInput()

    def __init__(self, *args, **kwargs):
        self.separator = kwargs.pop('separator', ',')
        super(HiddenMultiField, self).__init__(*args, **kwargs)

    def _value(self):
        if self.data:
            return self.separator.join(self.data)
        else:
            return ''

    def process_formdata(self, valuelist):
        super(HiddenMultiField, self).process_formdata(valuelist)
        if not self.data:
            self.data = []  # Calling ''.split(',') will give us [''] which is not "falsy"
        else:
            self.data = self.data.split(self.separator)


class MarkdownField(wtforms.TextAreaField):
    """
    TextArea field which has class='markdown'.
    """
    def __call__(self, **kwargs):
        c = kwargs.pop('class', '') or kwargs.pop('class_', '')
        kwargs['class'] = "%s %s" % (c, 'markdown') if c else 'markdown'
        return super(MarkdownField, self).__call__(**kwargs)


class ImgeeField(wtforms.TextField):
    """
    A TextField, which lets the user choose image from Imgee. The field is filled
    with the url of the image chosen.

    Example usage:
    image = ImgeeField(label='Logo', description='Your company logo here',
            validators=[validators.Required()],
            profile='foo', img_label='logos', img_size='100x75')
        )
    """
    def __init__(self, label='', validators=None, profile=None, img_label=None, img_size=None, **kwargs):
        super(ImgeeField, self).__init__(label, validators, **kwargs)
        self.profile = profile
        self.img_label = img_label
        self.img_size = img_size

    def __call__(self, **kwargs):
        c = kwargs.pop('class', '') or kwargs.pop('class_', '')
        kwargs['class'] = "%s %s" % (c, 'imgee-url-holder') if c else 'imgee-url-holder'
        if self.profile:
            kwargs['data-profile'] = self.profile
        if self.img_label:
            kwargs['data-img-label'] = self.img_label
        if self.img_size:
            kwargs['data-img-size'] = self.img_size
        return super(ImgeeField, self).__call__(**kwargs)

