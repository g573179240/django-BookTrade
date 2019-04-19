from Goods import views
from django.conf.urls import url
urlpatterns = [
    url(r'^$',views.index,name='index'),#首页
    url(r'^goods/(?P<goods_id>\d+)/$',views.detail,name='detail'),#详情页
    url(r'^list/(?P<type_id>\d+)/(?P<page>\d+)/$'                            ,views.list,name='list'),#列表页
]