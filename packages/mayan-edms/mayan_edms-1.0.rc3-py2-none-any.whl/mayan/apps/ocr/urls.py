from django.conf.urls import patterns, url

urlpatterns = patterns('ocr.views',
    url(r'^document/(?P<document_id>\d+)/submit/$', 'submit_document', (), 'submit_document'),
    url(r'^document/multiple/submit/$', 'submit_document_multiple', (), 'submit_document_multiple'),
    url(r'^queue/document/list/$', 'queue_document_list', (), 'queue_document_list'),
    url(r'^queue/document/(?P<queue_document_id>\d+)/delete/$', 'queue_document_delete', (), 'queue_document_delete'),
    url(r'^queue/document/multiple/delete/$', 'queue_document_multiple_delete', (), 'queue_document_multiple_delete'),
    url(r'^queue/document/(?P<queue_document_id>\d+)/re-queue/$', 're_queue_document', (), 're_queue_document'),
    url(r'^queue/document/multiple/re-queue/$', 're_queue_multiple_document', (), 're_queue_multiple_document'),

    url(r'^queue/(?P<document_queue_id>\d+)/enable/$', 'document_queue_enable', (), 'document_queue_enable'),
    url(r'^queue/(?P<document_queue_id>\d+)/disable/$', 'document_queue_disable', (), 'document_queue_disable'),

    url(r'^document/all/clean_up/$', 'all_document_ocr_cleanup', (), 'all_document_ocr_cleanup'),)
