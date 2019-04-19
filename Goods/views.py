from django.core.paginator import Paginator
from django.shortcuts import render, redirect
from django.urls import reverse

from .models import *
# Create your views here.

#主页
def index(request):
    #查询每个种类３个新品和４个最多浏览的信息
    book_data_new = Goods.objects.get_goods_by_type(BOOK_DATA,limit=3,sort='new')
    book_data_hot = Goods.objects.get_goods_by_type(BOOK_DATA,limit=4,sort='hot')
    phone_digital_new = Goods.objects.get_goods_by_type(PHONE_DIGITAL,limit= 3, sort='new')
    phone_digital_hot = Goods.objects.get_goods_by_type(PHONE_DIGITAL, limit=4, sort='hot')
    vehicle_new = Goods.objects.get_goods_by_type(VEHICLE, limit=3, sort='new')
    vehicle_hot = Goods.objects.get_goods_by_type(VEHICLE, limit=4, sort='hot')
    beauty_clothes_new = Goods.objects.get_goods_by_type(BEAUTY_CLOTHES, limit=3, sort='new')
    beauty_clothes_hot = Goods.objects.get_goods_by_type(BEAUTY_CLOTHES, limit=4, sort='hot')
    hoby_speciality_new = Goods.objects.get_goods_by_type(HOBY_SPECIALITY, limit=3, sort='new')
    hoby_speciality_hot = Goods.objects.get_goods_by_type(HOBY_SPECIALITY, limit=4, sort='hot')
    general_merchandise_new = Goods.objects.get_goods_by_type(GENERAL_MERCHANDISE, limit=3, sort='new')
    general_merchandise_hot = Goods.objects.get_goods_by_type(GENERAL_MERCHANDISE, limit=4, sort='hot')
    
    context = {
        'book_data_new': book_data_new,
        'book_data_hot': book_data_hot,
        'phone_digital_new': phone_digital_new,
        'phone_digital_hot': phone_digital_hot,
        'vehicle_new': vehicle_new,
        'vehicle_hot': vehicle_hot,
        'beauty_clothes_new': beauty_clothes_new,
        'beauty_clothes_hot': beauty_clothes_hot,
        'hoby_speciality_new': hoby_speciality_new,
        'hoby_speciality_hot': hoby_speciality_hot,
        'general_merchandise_new': general_merchandise_new,
        'general_merchandise_hot': general_merchandise_hot,
    }

    return render(request,'goods/index.html',context)

#商品详情页面
def detail(request,goods_id):
    goods = Goods.objects.get_goods_by_id(goods_id=goods_id)
    #如果商品不存在则跳转回首页
    if goods is None:
        return redirect(reverse('goods:index'))

    #新品推荐
    goods_li = Goods.objects.get_goods_by_type(type_id=goods.type_id,limit=2,sort='new')
    #当前商品类型
    type_title = GOODS_TYPE[goods.type_id]
    #定义上下文
    context = {'goods':goods,'goods_li':goods_li,'type_title':type_title}
    #使用模板
    return render(request,'goods/detail.html',context)

def list(request,type_id,page):
    #获取排序方式
    sort = request.GET.get('sort','default')
    #判断type_id是否合法
    if int(type_id) not in GOODS_TYPE.keys():
        return redirect(reverse('goods:index'))
    #根据种类id和排序方式查询商品
    goods_li = Goods.objects.get_goods_by_type(type_id=type_id,sort=sort)

    #分页
    paginator = Paginator(goods_li,1)
    #获取分页后的总页数
    num_pages = paginator.num_pages
    #获取第page页的数据
    if page == '' or int(page)>num_pages:
        page = 1
    else:
        page = int(page)
    goods_li = paginator.page(page)

    #页码控制
    # 1.总页数<5, 显示所有页码
    # 2.当前页是前3页，显示1-5页
    # 3.当前页是后3页，显示后5页 10 9 8 7
    # 4.其他情况，显示当前页前2页，后2页，当前页
    if num_pages<5:
        pages = range(1,num_pages+1)
    elif num_pages<=3:
        pages = range(1,6)
    elif num_pages - page <= 2:
        pages = range(num_pages-4,num_pages+1)
    else:
        pages = range(page-2,page+3)

    #新品推荐
    goods_new = Goods.objects.get_goods_by_type(type_id=type_id,limit=2,sort='new')
    #定义上下文
    type_title = GOODS_TYPE[int(type_id)]
    context = {
        'goods_li':goods_li,
        'goods_new':goods_new,
        'type_id':type_id,
        'sort':sort,
        'type_title':type_title,
        'pages':pages
    }

    #使用模板
    return render(request,'goods/list.html',context)