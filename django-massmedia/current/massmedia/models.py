from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.template.defaultfilters import slugify
from django.conf import settings
from django.core.files.base import ContentFile
from django.template.loader import get_template
from django.template import TemplateDoesNotExist,Template,Context
from massmedia import settings as appsettings
from cStringIO import StringIO
import mimetypes
import os
import zipfile

# Patch mimetypes w/ any extra types
mimetypes.types_map.update(appsettings.EXTRA_MIME_TYPES)

try:
    import cPickle as pickle
except ImportError:
    import pickle
try:
    from iptcinfo import IPTCInfo
    iptc = 1
except ImportError:
    iptc = 0
    
try:
    # Try to use http://code.google.com/p/django-categories/
    from categories.models import Category
except ImportError:
    # Otherwise use dummy category
    class Category(models.Model):
        name = models.CharField(max_length=150)
        def __unicode__(self): return self.name
        
try:
    import Image as PilImage
except ImportError:
    try:
        from PIL import Image as PilImage
    except ImportError:
        PilImage = 0

try:
    from hachoir_core.error import HachoirError
    from hachoir_core.stream import InputStreamError
    from hachoir_parser import createParser
    from hachoir_metadata import extractMetadata
except ImportError:
    extractMetadata = None


def parse_metadata(path):
    try:
        parser = createParser(unicode(path))
    except InputStreamError:           
        return
    if not parser:
        return
    try:
        metadata = extractMetadata(parser, appsettings.INFO_QUALITY)
    except HachoirError:
        return
    if not metadata:
        return
    data = {}
    text = metadata.exportPlaintext(priority=None, human=False)           
    for line in text:
        if not line.strip().startswith('-'):
            key = line.strip().lower().split(':')[0]
            value = []
        else:
            key = line.strip().split('- ')[1].split(': ')[0]
            value = line.split(key)[1][2:]
            if key in data:
                if hasattr(data[key],'__iter__'):
                    value = data[key] + [value]
                else:
                    value = [data[key],value]
        if value:
            data[key] = value
    return data

class PickledObjectField(models.Field):
     """ Django snippet - http://www.djangosnippets.org/snippets/513/  """
     __metaclass__ = models.SubfieldBase

     def to_python(self, value):
         try:
             return pickle.loads(str(value))
         except:
             # If an error was raised, just return the plain value
             return value

     def get_db_prep_save(self, value):
         if value is not None:
             value = pickle.dumps(value)
         return str(value)

     def get_internal_type(self):
         return 'TextField'

     def get_db_prep_lookup(self, lookup_type, value):
         if lookup_type == 'exact':
             value = self.get_db_prep_save(value)
             return super(PickledObjectField, self).get_db_prep_lookup(lookup_type, value)
         elif lookup_type == 'in':
             value = [self.get_db_prep_save(v) for v in value]
             return super(PickledObjectField, self).get_db_prep_lookup(lookup_type, value)
         else:
             raise TypeError('Lookup type %s is not supported.' %  lookup_type)

class Media(models.Model):
    title = models.CharField(max_length=255,unique=True)
    slug = models.SlugField(unique=True)
    creation_date = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(User, blank=True, null=True, limit_choices_to={'is_staff':True})
    one_off_author = models.CharField('one-off author', max_length=100, blank=True)
    credit = models.CharField(max_length=150, blank=True)
    caption = models.TextField(blank=True)
    metadata = PickledObjectField(blank=True)
    sites = models.ManyToManyField(Site,related_name='%(class)s_sites')
    categories = models.ManyToManyField(Category, blank=True)
    reproduction_allowed = models.BooleanField("we have reproduction rights for this media", default=True)
    public = models.BooleanField(help_text="this media is publicly available", default=True)
    external_url = models.URLField(blank=True,null=True,help_text="If this URLField is set, the media will be pulled externally")
    mime_type = models.CharField(max_length=150,blank=True,null=True)
    width = models.IntegerField(blank=True, null=True, help_text="The width of the widget for the media")
    height = models.IntegerField(blank=True, null=True, help_text="The height of the widget for the media")
    
    widget_template = models.CharField(max_length=255,blank=True,null=True,
                help_text='The template name used to generate the widget (defaults to mime_type layout)')

    class Meta:
        ordering = ('-creation_date',)
        abstract = True
        
    def __unicode__(self):
        return self.title

    def get_absolute_url(self):
        if self.external_url:
            return self.external_url
        if hasattr(self,'file') and getattr(self,'file',None):
            return self.absolute_url((
                settings.MEDIA_URL,
                self.creation_date.strftime("%Y/%b/%d"),
                os.path.basename(self.file.path)))
        return ''
        
    def absolute_url(self, format):
        raise NotImplementedError
    
    def save(self, *args, **kwargs):
        if self.file and not self.mime_type:
            self.mime_type = mimetypes.guess_type(self.file.path)[0]
        if not(self.metadata) and self.file and extractMetadata:
            self.metadata = parse_metadata(self.file.path) or ''
        super(Media, self).save(*args, **kwargs)
    
    
    def get_mime_type(self):
        if self.mime_type:
            return self.mime_type
        if self.metadata and 'mime_type' in self.metadata:
            return self.metadata['mime_type']
        return
    
    def get_template(self):
        mime_type = self.get_mime_type()
        if self.widget_template:
            if appsettings.TEMPLATE_MODE == appsettings.FILE_SYSTEM:
                return get_template(self.widget_template)
            else:
                return MediaTemplate.objects.get(name=self.widget_template).template()
        elif mime_type is None:
            if appsettings.TEMPLATE_MODE == appsettings.FILE_SYSTEM:
                if isinstance(self, VoxantVideo):
                    return get_template('massmedia/voxant.html')
                else:
                    return get_template('massmedia/generic.html')
            else:
                return MediaTemplate.objects.get(mimetype='').tempate()
        else:
            if appsettings.TEMPLATE_MODE == appsettings.FILE_SYSTEM:
                try:
                    return get_template('massmedia/%s.html'%mime_type)
                except TemplateDoesNotExist:
                    try:
                        return get_template('massmedia/%s/generic.html'%mime_type.split('/')[0])
                    except TemplateDoesNotExist:
                        return get_template('massmedia/generic.html')
            else:
                try:
                    return MediaTemplate.objects.get(mimetype=mime_type)
                except MediaTemplate.DoesNotExist:
                    try:
                        return MediaTemplate.objects.get(mimetype=mime_type.split('/')[0])
                    except MediaTemplate.DoesNotExist:
                        return MediaTemplate.objects.get(mimetype='').tempate()
       
    def render_template(self): 
        return self.get_template().render(Context({
            'media':self,
            'MEDIA_URL':settings.MEDIA_URL
        }))
        
class Image(Media):
    file = models.ImageField(upload_to='img/%Y/%b/%d', blank=True, null=True)
    
    def save(self, *args, **kwargs):
        if iptc:
            try:
                data.update(IPTCInfo(path).__dict__['_data'])
            except:
                pass
        super(Image, self).save(*args, **kwargs)
    
    def thumb(self):
        if self.file:
            thumbnail = '%s.thumb%s'%os.path.splitext(self.file.path)
            thumburl = thumbnail[len(settings.MEDIA_ROOT)-1:]
            if not os.path.exists(thumbnail):
                im = PilImage.open(self.file)
                im.thumbnail(appsettings.THUMB_SIZE,PilImage.ANTIALIAS)
                im.save(thumbnail,im.format)
            return '<a href="%s"><img src="%s%s"/></a>'%\
                        (self.get_absolute_url(),settings.MEDIA_URL,thumburl)
        elif self.external_url:
            return '<a href="%s"><img src="%s"/></a>'%\
                        (self.get_absolute_url(),self.get_absolute_url())
    thumb.allow_tags = True
    thumb.short_description = 'Thumbnail'
    
    def absolute_url(self, format):
        return "%simg/%s/%s" % format

class Video(Media):
    file = models.FileField(upload_to='video/%Y/%b/%d', blank=True, null=True)
    thumbnail = models.ForeignKey(Image, null=True, blank=True)
    
    def thumb(self):
        return self.thumbnail.thumb()
    thumb.allow_tags = True
    thumb.short_description = 'Thumbnail'
    
    def absolute_url(self, format):
        return "%svideo/%s/%s" % format

class VoxantVideo(Video):
    asset_id = models.CharField(max_length=255,help_text='Voxant video asset ID (the `a` parameter)')
    layout_id = models.CharField(max_length=255,help_text='Voxant video asset ID (the `m` parameter)')
    
    def absolute_url(self, format):
        return "%svoxantvideo/%s/%s" % format
    
class Audio(Media):
    file = models.FileField(upload_to='audio/%Y/%b/%d', blank=True, null=True)
    def absolute_url(self, format):
        return "%saudio/%s/%s" % format

class Flash(Media):
    file = models.FileField(upload_to='flash/%Y/%b/%d', blank=True, null=True)
    def absolute_url(self, format):
        return "%sflash/%s/%s" % format
    
   
class Collection(models.Model):
    creation_date = models.DateTimeField(auto_now_add=True)
    title = models.CharField(max_length=255, unique=True)
    slug = models.SlugField(unique=True)
    caption = models.TextField(blank=True)
    zip_file = models.FileField('Media files in a .zip', upload_to='tmp', blank=True,null=True,
                        help_text='Select a .zip file of media to upload into a the Collection.')
    public = models.BooleanField(help_text="this collection is publicly available", default=True)
    sites = models.ManyToManyField(Site)
    categories = models.ManyToManyField(Category, blank=True)
    
    class Meta:
        ordering = ['-creation_date']
        get_latest_by = 'creation_date'

    def __unicode__(self):
        return self.title
 
    def save(self, *args, **kwargs):
        super(Collection, self).save(*args, **kwargs)
        self.process_zipfile()
        
    def process_zipfile(self):
        if self.zip_file and os.path.isfile(self.zip_file.path):
            zip = zipfile.ZipFile(self.zip_file.path)
            if zip.testzip():
                raise Exception('"%s" in the .zip archive is corrupt.' % bad_file)
            for filename in zip.namelist():
                if filename.startswith('__'): # do not process meta files
                    continue
                data = zip.read(filename)
                size = len(data)
                if size:
                    title,ext = os.path.splitext(os.path.basename(filename))
                    ext = ext[1:]
                    slug = slugify(title)
                    if ext in appsettings.IMAGE_EXTS:
                        model = Image
                        try:
                            trial_image = PilImage.open(StringIO(data))
                            trial_image.load()
                            trial_image = PilImage.open(StringIO(data))
                            trial_image.verify()
                        except Exception:
                            continue
                    elif ext in appsettings.VIDEO_EXTS:
                        model = Video
                    elif ext in appsettings.AUDIO_EXTS:
                        model = Audio
                    elif ext in appsettings.FLASH_EXTS:
                        model = Flash
                    else:
                        raise TypeError, 'Unknown media extension %s'%ext
                    try:
                        media = model.objects.get(slug=slug) #XXX
                    except model.DoesNotExist:
                        media = model(title=title, slug=slug)
                        media.file.save(filename, ContentFile(data))                      
                        # XXX: Make site relations possible, send signals
                        media.sites.add(Site.objects.get_current())
                        CollectionRelation(content_object=media,collection=self).save()
            zip.close()
            os.remove(self.zip_file.path)
            self.zip_file.delete()
            super(Collection, self).save(*(), **{})

collection_limits = {'model__in':('image','audio','video','flash')}
class CollectionRelation(models.Model):
    collection = models.ForeignKey(Collection)
    content_type = models.ForeignKey(ContentType, limit_choices_to=collection_limits)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey('content_type', 'object_id')
    
    def __unicode__(self):
        return unicode(self.content_object)
        
class MediaTemplate(models.Model):
    name = models.CharField(max_length=255)
    mimetype = models.CharField(max_length=255,null=True,blank=True)
    content = models.TextField()
    
    def __unicode__(self):
        return self.name
    
    def template(self):
        return Template(self.content)
