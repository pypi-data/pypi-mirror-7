#!/usr/bin/env python
# -*- coding: utf-8 -*-

from notmm.utils.urlmap import RegexURLMap, url

try:
    from notmm.utils.django_settings import SettingsProxy
    settings = SettingsProxy('local_settings', autoload=True).get_settings()
    
except ImportError:
    from django.conf import settings

from notmm.release import VERSION
render_to_response = 'blogengine.template.direct_to_template'

extra_context = {
    #'settings': settings,
    'local_version': VERSION,
    'media_url': settings.MEDIA_URL 
}

#import pdb; pdb.set_trace()
urlpatterns = RegexURLMap()

urlpatterns.add_routes('',   
   url(r'(?P<path>\w+.(gif|png|jpg|ico))$', \
    'helloworld.views.image_handler', {
        'document_root' : settings.MEDIA_ROOT }
   )
)

urlpatterns.add_routes('',
   # Frontdoor (a simple generic view)
   url(r'^$|index.html$', render_to_response, {
        'template_name': 'default/index.mako',
        'extra_context': extra_context
   })
   )
#urlpatterns.commit()
#print len(urlpatterns)
