from massmedia import models #import Collection,CollectionRelation,Image,Flash,Video,Audio
from massmedia.templatetags.media_widgets import show_media
from django.shortcuts import render_to_response,get_object_or_404
from django.conf import settings
from django.http import Http404,HttpResponse
from django.contrib.contenttypes.models import ContentType


def widget(reqeust, id, type):
    try:
        assert hasattr(models,type.capitalize())
        model = getattr(models,type.capitalize())
    except AssertionError:
        raise Http404
    try:
        return render_to_response('massmedia/inline.html',{
            'media':model.objects.get(pk=id),
            'type':type
        })
    except model.DoesNotExist:
        return HttpResponse('%s #%s not found'%(type,id))

def list_by_type(request,type):
    try:
        assert hasattr(models,type.capitalize())
        model = getattr(models,type.capitalize())
    except AssertionError:
        raise Http404
    return render_to_response('massmedia/list.html',{
        'objects': model.objects.filter(
            public=True,
            sites__id__exact=settings.SITE_ID
        )
    })

def list_by_collection(request,id):
    return render_to_response('massmedia/list.html',{
        'objects': [x.content_object for x in models.CollectionRelation.objects.filter(
            collection=get_object_or_404(models.Collection, pk=id),
            collection__public=True,
            collection__sites__id__exact=settings.SITE_ID
        )]
    })

def list_by_collection_by_type(request,id,type):
    return render_to_response('massmedia/list.html',{
        'objects': [x.content_object for x in models.CollectionRelation.objects.filter(
            collection=get_object_or_404(models.Collection, pk=id),
            collection__public=True,
            collection__sites__id__exact=settings.SITE_ID,
            content_type=ContentType.objects.get(name=type),
        )]
    })
    
def list(request):
    return render_to_response('massmedia/list_types.html',{
        'collections':models.Collection.objects.filter(
            public=True,
            sites__id__exact=settings.SITE_ID
        )
    })