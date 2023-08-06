from __future__ import unicode_literals
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.utils.encoding import python_2_unicode_compatible
from django.contrib.staticfiles.storage import staticfiles_storage


@python_2_unicode_compatible
class BaseTag(object):
    """
    Base Tag behaviour
    """
    tag_name = ""
    self_closed = True  # Defines if should close itself < />
    meta_name = ""
    meta_content = ""
    tag_value = ""

    def print_tag(self):
        """
        Builds tag as text for printing
        :return: text
        """
        if not isinstance(self, BaseTag):
            raise TypeError("Tag must be of class simple-seo.tags.BaseTag")

        # print_attrs = ""
        # for attr_name, attr_value in iteritems(self._attributes):
        #     print_attrs += " %s=\"%s\"" % (attr_name, attr_value)

        if self.self_closed:
            if self.meta_name and self.meta_content:
                return "<%s name='%s' content='%s' />" % (self.tag_name, self.meta_name, self.meta_content)
            else:
                return "<%s/>" % self.tag_name
        else:
            if self.meta_name and self.meta_content:
                return "<%s name='%s' content='%s'>%s</%s>" % (self.tag_name, self.meta_name, self.meta_content, self.tag_value, self.tag_name)
            else:
                return "<%s>%s</%s>" % (self.tag_name, self.tag_value, self.tag_name)

    def __str__(self):
        raise NotImplementedError("Must implement tag output __str__()")

    def __len__(self):
        raise NotImplementedError("Must implement tag output __len__()")


class TitleTag(BaseTag):
    """
    Title Tag class
    """

    def __init__(self, *args, **kwargs):
        self.tag_name = "title"
        self.self_closed = False
        if 'value' in kwargs:
            if len(kwargs['value']) > 68:
                self.tag_value = kwargs['value'][:68]
            else:
                self.tag_value = kwargs['value']

    def __str__(self):
        return self.tag_value

    def __len__(self):
        return len(self.tag_value)


class BaseMetatag(BaseTag):
    """
    Base Meta Tag
    """

    def __init__(self, *args, **kwargs):
        self.tag_name = 'meta'
        self.self_closed = True
        if 'name' in kwargs:
            self.meta_name = kwargs['name']

    def __str__(self):
        return self.meta_content

    def __len__(self):
        return len(self.meta_content)


class MetaTag(BaseMetatag):
    """
    Meta Tag class
    """

    def __init__(self, *args, **kwargs):
        super(MetaTag, self).__init__(*args, **kwargs)
        if 'value' in kwargs:
            if kwargs['value'] and len(kwargs['value']) > 255:
                self.meta_content = kwargs['value'][:255]
            else:
                self.meta_content = kwargs['value']


class ImageMetaTag(BaseMetatag):
    """
    Image Meta Tag class
    """

    def __init__(self, *args, **kwargs):
        super(ImageMetaTag, self).__init__(*args, **kwargs)
        if 'value' in kwargs:
            if kwargs['value']:
                if isinstance(kwargs['value'], InMemoryUploadedFile):
                    rel_path = kwargs['path'] + kwargs['value'].name
                    self._inmemoryuploadedfile = kwargs['value']
                else:
                    self._inmemoryuploadedfile = None
                    rel_path = kwargs['value']
                if staticfiles_storage:
                    self.meta_content = staticfiles_storage.url(rel_path)
                else:
                    self.meta_content = rel_path
    @property
    def url(self):
        return self.meta_content

    def __str__(self):
        return str(self.meta_content)


class KeywordsTag(BaseMetatag):
    """
    Keywords Meta Tag class
    """

    def _clean(self, value):
        if value:
            return value.replace('"', '&#34;').replace("\n", ", ").strip()
        else:
            return value

    def __init__(self, *args, **kwargs):
        super(KeywordsTag, self).__init__(*args, **kwargs)
        if 'value' in kwargs:
            if kwargs['value'] and len(kwargs['value']) > 255:
                self.meta_content = self._clean(kwargs['value'][:255])
            else:
                self.meta_content = self._clean(kwargs['value'])
