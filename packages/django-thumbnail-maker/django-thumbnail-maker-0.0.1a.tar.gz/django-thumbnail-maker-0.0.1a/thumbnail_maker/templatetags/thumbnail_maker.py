import re
from django.conf import settings
from django.template import Library, TemplateSyntaxError
from sorl.thumbnail import default
from sorl.thumbnail.images import DummyImageFile
from sorl.thumbnail.templatetags.thumbnail import ThumbnailNode


register = Library()

kw_pat = re.compile(r'^(?P<key>[\w]+)=(?P<value>.+)$')


class UseThumbnailNode(ThumbnailNode):
    error_msg = 'Syntax error. Expected: ' \
                '``usethumbnail source thumbname as var``'

    def __init__(self, parser, token):
        bits = token.split_contents()
        if len(bits) != 5 or bits[-2] != 'as':
            raise TemplateSyntaxError(self.error_msg)
        self.file_ = parser.compile_filter(bits[1])
        self.geometry = parser.compile_filter(bits[2])
        self.options = {}
        self.as_var = bits[-1]
        self.nodelist_file = parser.parse(('empty', 'endusethumbnail',))
        if parser.next_token().contents == 'empty':
            self.nodelist_empty = parser.parse(('endusethumbnail',))
            parser.delete_first_token()

    def _render(self, context):
        file_ = self.file_.resolve(context)
        geometry = self.geometry.resolve(context)
        geometry, options = file_.field.thumbs.get(geometry)
        if hasattr(settings, 'THUMBNAIL_DUMMY'):
            thumbnail = DummyImageFile(geometry)
        elif file_:
            thumbnail = default.backend.get_thumbnail(
                file_, geometry, **options
            )
        else:
            return self.nodelist_empty.render(context)
        context.push()
        context[self.as_var] = thumbnail
        output = self.nodelist_file.render(context)
        context.pop()
        return output

    def __repr__(self):
        return "<UseThumbnailNode>"


@register.tag
def usethumbnail(parser, token):
    return UseThumbnailNode(parser, token)
