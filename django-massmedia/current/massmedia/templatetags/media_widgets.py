from django import template
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from massmedia.models import VoxantVideo, CollectionRelation

register = template.Library()

class MassMediaNode(template.Node):
    def __init__(self, *args):
        assert len(args)
        self.args = list(args)
    
    def render(self, context):
        self.args[0] = context.get(self.args[0],self.args[0])
        if isinstance(self.args[0], basestring):
            try:
                self.args[0] = VoxantVideo.objects.get(slug=self.args[0])
            except VoxantVideo.DoesNotExist:
                return ''
        return self.args[0].get_template().render(
            template.RequestContext(context['request'], {
                'media':self.args[0],
            })
        )
def show_media(parser, token):
    return MassMediaNode(*token.contents.split()[1:])
    
register.tag(show_media)


class MediaByTypeNode(template.Node):
    def __init__(self, collection, ctype, var_name):
        self.collection = template.Variable(collection)
        self.ctype = ctype
        self.var_name = var_name
    def render(self, context):
        try:
            ctype = ContentType.objects.get(name=self.ctype)
        except ContentType.DoesNotExist:
            context[self.var_name] = []
            return ''
        
        context[self.var_name] = [x.content_object for x in CollectionRelation.objects.filter(
                                        collection=self.collection.resolve(context),
                                        collection__public=True,
                                        collection__sites__id__exact=settings.SITE_ID,
                                        content_type=ContentType.objects.get(name=self.ctype),
                                    ) if x.content_object.public is True]
        return ''

@register.tag('get_media_by_type')
def do_media_by_type(parser, token):
    """
    Usage:
    
        {% get_media_by_type [collection] [type] as [var_name] %}
        
    Example:
    
        {% get_media_by_type object.media massmedia.image as images %}
        
    """
    try:
        tag_name, collection, ctype, junk, var_name = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError, "%r tag requires exactly four arguments" % token.contents.split()[0]
    return MediaByTypeNode(collection, ctype, var_name)