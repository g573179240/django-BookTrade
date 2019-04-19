import datetime
from django.http import JsonResponse
from django.shortcuts import render, redirect

# Create your views here.
from django.urls import reverse
from django_redis import get_redis_connection
from django.db import transaction
from Function.decorators import login_required
from Goods.models import Goods
from Order.models import OrderInfo, OrderGoods
from Users.models import Address


@login_required
def order_place(request):
    '''显示订单提交页面'''
    goods_ids = request.POST.getlist('goods_ids')
    if not all(goods_ids):
        return redirect(reverse('Cart:show'))

    passport_id = request.session.get('passport_id')
    addr = Address.objects.get_default_address(passport_id=passport_id)

    goods_li = []
    total_count = 0
    total_price =0
    conn = get_redis_connection('default')
    cart_key = "cart_%d" % passport_id

    for id in goods_ids:
        goods = Goods.objects.get_goods_by_id(goods_id=id)
        #从redis中获取用户要购买商品数目
        count = conn.hget(cart_key,id)
        goods.count = count
        #计算商品小计
        amount = int(count)*goods.price
        goods.amout = amount
        goods_li.append(goods)
        #累计计算商品总数目和总金额
        total_count += int(count)
        total_price += goods.amount
    # 商品运费和实际付款
    transit_price = 10
    total_pay = total_price + transit_price
    goods_ids = ','.join(goods_ids)
    #组织模板
    context = {
        "addr":addr,
        "goods_li":goods_li,
        "total_count":total_count,
        "total_price":total_price,
        "transit_price":transit_price,
        "total_pay":total_pay,
        "goods_ids":goods_ids
    }
    return render(request,'order/place_order.html',context)

@transaction.atomic
def order_commit(request):
    '''生成订单'''
    #验证用户是否登录
    if not request.session.has_key('is_login'):
        return JsonResponse({"res":0,"errmsg":"用户未登录"})
    #接收数据
    addr_id = request.POST.get('addr_id')
    pay_method = request.POST.get('pay_method')
    goods_ids = request.POST.get('goods_ids')

    #数据校验
    if not all([addr_id,pay_method,goods_ids]):
        return JsonResponse({"res":1,"errmsg":"数据不完整"})
    try:
        addr = Address.objects.get(id=addr_id)
    except Exception as e:
        return JsonResponse({"res":2,"errmsg":"地址信息错误"})

    if int(pay_method) not in OrderInfo.PAY_METHODS_ENUM.values():
        return JsonResponse({'res':3,"errmsg":"不支持支付方式"})
    #订单创建
    #组织订单信息
    passport_id = request.session.get('passport_id')
    #自动生成订单id
    order_id = datetime.now().strftime('%Y%m%d%H%M%S')+str(passport_id)
    transit_price = 10
    total_count = 0
    total_price = 0

    #创建一个保存点
    sid = transaction.savepoint()
    try:
        #向OrderGoods中添加一条信息
        order = OrderInfo.objects.create(
            orderid =order_id,
            passport_id = passport_id,
            addr_id = addr_id,
            total_count = total_count,
            total_price = total_price,
            transit_price = transit_price,
            pay_method = pay_method)

        #向OrderInfo中添加信息
        goods_ids = goods_ids.split(',')
        conn = get_redis_connection('default')
        cart_key = 'cart_%d' % passport_id
        #遍历用户购买的商品的信息
        for id in goods_ids:
            goods = Goods.objects.get_goods_by_id(goods_id=id)
            if goods is None:
                transaction.savepoint_rollback(sid)
                return JsonResponse({"res":4,"errmsg":"商品信息错误"})
            #获取用户购买商品数量
            count = conn.hget(cart_key,id)
            #判断商品库存
            if int(count)>goods.stock:
                transaction.savepoint_rollback(sid)
                return JsonResponse({"res":5,"errmsg":"商品库存不存在"})
            #创建一条订单商品记录
            OrderGoods.objects.create(order_id=order_id,
                                      goods_id = id,
                                      count = count,
                                      price = goods.price)
            #增加商品销量，减少商品库岑
            goods.sales += int(count)
            goods.stock -= int(count)
            goods.save()

            #累计计算商品的总数目和总额
            total_count += int(count)
            total_price += int(count)*goods.price
        #更新商品总数目和总金额
        order.total_count = total_count
        order.total_price = total_price
        order.save()
    except Exception as e:
        transaction.savepoint_rollback(sid)
        return JsonResponse({"res":7,"errmsg":"服务器错误"})
    #清除购物车对应记录
    conn.hdel(cart_key,*goods_ids)
    #事物提交
    transaction.savepoint_commit(sid)
    return JsonResponse({"res":6})





























