from django.http import JsonResponse
from django.shortcuts import render
from Function.decorators import login_required
from Goods.models import *
from django_redis import get_redis_connection

# Create your views here.
#前端发送过来的数据：商品id 商品数目　goods_id goods_count

@login_required
def cart_add(request):
    '''向购物车添加数据'''

    # 接收数据
    goods_id = request.POST.get('goods_id')
    goods_count = request.POST.get('goods_count')

    # 进行数据校验
    if not all([goods_id,goods_count]):
        return JsonResponse({"res":1,"errmsg":"数据不完整"})
    goods = Goods.objects.get_goods_by_id(goods_id=goods_id)
    if goods is None:
        # 商品不存在
        return JsonResponse({"res":2,"errmsg":"商品不存在"})
    try:
        count = int(goods_count)
    except Exception as e:
        #商品数目不合法
        return JsonResponse({"res":3,"errmsg":"商品数量必须为数字"})

    #添加商品到购物车
    # 为每个用户的购物车记录用一条hash数据保存，格式cart_用户id:商品id　商品数量
    conn = get_redis_connection('default')
    cart_key = 'cart_%d' % request.session.get('passport_id')
    res = conn.hget(cart_key,goods_id)
    if res is None:
        #如果用户的购物车中没有添加商品，则添加数据
        res = count
    else:
        # 如果用户的购物车已经添加过商品，则累计商品数目
        res = int(res)+count

    #判断商品的库存
    if res>goods.stock:
        return JsonResponse({"res":4,"errmsg":"商品库存不足"})
    else:
        conn.hset(cart_key,goods_id,res)

    return JsonResponse({"res":5})

@login_required
def cart_count(request):
    '''获取用户购物车中商品的数目'''

    # 计算购物车商品数量
    conn = get_redis_connection('default')
    cart_key = 'cart_%d' % request.session.get('passport_id')
    # 显示商品条目数
    res = 0
    res_list = conn.hvals(cart_key)

    for i in res_list:
        res+=int(i)
    return JsonResponse({"res":res})

@login_required
def cart_show(request):
    passport_id = request.session.get('passport_id')
    # 获取用户购物车记录
    conn = get_redis_connection('default')
    cart_key = 'cart_%d' % passport_id
    res_dict = conn.hgetall(cart_key)

    goods_li = []
    total_count = 0
    total_price = 0

    for id,count in res_dict.items():
        goods = Goods.objects.get_goods_by_id(goods_id=id)
        goods.count = count
        goods.amout = int(count)*goods.price
        goods_li.append(goods)

        total_count += int(count)
        total_price += int(count)*goods.price

    context = {
        "goods_li":goods_li,
        "total_count":total_count,
        "total_price":total_price,
    }

    return render(request,'cart/cart.html',context)

@login_required
def cart_del(request):
    goods_id = request.POST.get('goods_id')
    #校验商品是否存放
    if not all([goods_id]):
        return JsonResponse({"res":1,"errmsg":"数据不完整"})
    goods = Goods.objects.get_goods_by_id(goods_id=goods_id)
    if goods is None:
        return JsonResponse({"res":2,"errmsg":"商品不存在"})
    #删除购物车商品信息
    conn = get_redis_connection('default')
    cart_key = "cart_%d" % request.session.get('passport_id')
    conn.hdel(cart_key,goods_id)
    return JsonResponse({"res":3})

@login_required
def cart_update(request):
    '''更新购物车商品的数量'''
    #接收数据
    goods_id = request.POST.get('goods_id')
    goods_count = request.POST.get('goods_count')
    #校验数据
    if not all([goods_id,goods_count]):
        return JsonResponse({"res":1,"errmsg":"数据不完整"})
    goods = Goods.objects.get_goods_by_id(goods_id = goods_id)

    if goods is None:
        return JsonResponse({"res":2,"errmsg":"商品不存在"})
    try:
        goods_count = int(goods_count)
    except Exception as e:
        return JsonResponse({"res":3,"errmsg":"商品数目必须为数字"})

    #更新操作
    conn = get_redis_connection('default')
    cart_key = 'cart_%d' % request.session.get('passport_id')
    #判断商品库存
    if goods_count > goods.stock:
        return JsonResponse({"res":4,"errmsg":"商品库存不足"})
    conn.hset(cart_key,goods_id,goods_count)
    return JsonResponse({"res":5})

















