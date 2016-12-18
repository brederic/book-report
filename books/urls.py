from django.conf.urls import url

from . import views

urlpatterns = [
    # ex: /books/
    url(r'^$', views.index, name='index'),
    # ex: /books/5/
    url(r'^(?P<book_id>[0-9]+)/$', views.detail, name='detail'),
    url(r'^new/(?P<book_id>[0-9]+)/$', views.new_review, name='new-review'),
    url(r'^used/(?P<book_id>[0-9]+)/$', views.used_review, name='used-review'),
    # ex: /books/5/results/
    url(r'^(?P<book_id>[0-9]+)/results/$', views.results, name='results'),
    # ex: /books/5/vote/
    url(r'^(?P<book_id>[0-9]+)/list/$', views.list_book, name='list'),
    url(r'^charts/(?P<book_id>[0-9]+).png$', views.simple_chart, name='chart'),
    url(r'^charts/review/(?P<book_id>[0-9]+)-(?P<condition>[0-9]).png$', views.book_chart, name='book-chart'),
    url(r'^(?P<book_id>[0-9]+)/compare/$', views.compare, name='compare'),
    url(r'^search$', views.search, name='search'),

]
