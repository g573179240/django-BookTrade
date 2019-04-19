from django.core.paginator import Paginator
from django.db.models import Model
from django.http import JsonResponse
from django.shortcuts import render, redirect,reverse

from Function.decorators import login_required
from Order.models import *
from Users.models import *
import re

# Create your views here.

#进入到注册页面
def register(request):
    return render(request,'users/register.html')

#提交注册页的表单
def register_handle(request):
    #获取数据
    username = request.POST.get('user_name')
    password = request.POST.get('pwd')
    email = request.POST.get('email')
    #校正数据
    # 数据有空
    if not all([username,password,email]):
        return render(request,'users/register.html',{'errmsg':'参数不能为空'})
    # 判断邮箱是否合法
    if not re.match(r'^[a-z0-9][\w\.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$',email):
        return render(request,'users/register.html',{'errmsg':'邮箱不正确'})
    #业务处理，向系统中添加账户
    try:
        Passport.objects.add_one_passport(
            username=username,
            password=password,
            email=email
        )
    #打印异常
    except Exception as e:
        print("e:",e)
        return render(request,'users/register.html',{'errmsg':'用户名已存在'})
    #开发中，暂时注册完还是先返回注册页
    return redirect(reverse('goods:index'))

#显示登录页面
def login(request):
    #如果能从cookies中获取到username则表示点击过“保存用户名”
    if request.COOKIES.get('username'):
        username = request.COOKIES.get('username')
        checked = 'checked'
    else:
        username = ''
        checked = ''
    context = {
        'username':username,
        'checked':checked,
    }
    return render(request,'users/login.html',context)

#验证登录
def login_check(request):
    #1.获取数据
    username = request.POST.get('username')
    password = request.POST.get('password')
    remember = request.POST.get('remember')

    #2.验证数据
    if not all([username,password,remember]):
        #有数据为空
        return JsonResponse({"res":2})

    #3.进行处理：根据用户名和密码查找账户信息
    passport  = Passport.objects.get_one_passport(username=username,password=password)
    if passport:
        turn_to =reverse('goods:index')
        jres = JsonResponse({"res":1,"turn_to":turn_to})

        #是否记住用户名
        if remember == 'true':
            jres.set_cookie('username',username,max_age=7*24*3600)
        else:
            jres.delete_cookie('username')

        #记住用户的登录状态
        request.session['islogin'] = True
        request.session['username'] = username
        request.session['passport_id'] = passport.id
        return jres
    else:
        #用户名密码错误
        return JsonResponse({"res":0})

#登出
def logout(request):
    # 清除session信息
    request.session.flush()
    return redirect(reverse('goods:index'))

@login_required
def user(request):
    passport_id = request.session.get('passport_id')
    addr = Address.objects.get_default_address(passport_id=passport_id)
    goods_li = []
    context = {
        'addr':addr,
        'page':'user',
        'goods_li':goods_li,
    }
    return render(request,'users/user_center_info.html',context)

@login_required
def address(request):
    '''编辑收货地址功能'''
    passport_id = request.session.get('passport_id')
    if request.method == 'GET':
         #查询用户的默认地址
         addr = Address.objects.get_default_address(passport_id=passport_id)
         return render(request,'users/user_center_site.html',{'addr':addr,'page':'address'})
    else:
        recipient_name = request.POST.get('username')
        recipient_addr = request.POST.get('addr')
        zip_code = request.POST.get('zip_code')
        recipient_phone = request.POST.get('phone')

        # 验证
        if not all([recipient_addr,recipient_name,recipient_phone,zip_code]):
            return render(request,'users/user_center_site.html',{{"errmsg":'参数不能为空'}})
        #添加收货地址
        Address.objects.add_one_address(passport_id=passport_id,
                                        recipient_name=recipient_name,
                                        recipient_addr = recipient_addr,
                                        zip_code = zip_code,
                                        recipient_phone = recipient_phone)
        #返回应答
        return redirect(reverse('user:address'))

@login_required
def order(request,page):
    #查询用户的订单信息
    passport_id = request.session.get('passport_id')
    #获取订单信息
    order_li = OrderInfo.objects.filter(passport_id=passport_id)
    for order in order_li:
        order_id = order.order_id
        order_goods_li = OrderGoods.objects.filter(order_id = order_id)
        #获取商品小计
        for order_goods in order_goods_li:
            count = order_goods.count
            price = order_goods.price
            amout = count * price
            #保存小计
            order_goods.amout = amout
        #给order对象动态增加一个order_goods_li，保存订单中商品的信息
        order.order_goods_li = order_goods_li
    #每页显示３个
    paginator = Paginator(order_li,3)
    num_pages = paginator.num_pages

    if not page:
        page = 1
    if page == '' or int(page)>num_pages:
        page = 1
    else:
        page = int(page)
    order_li = paginator.page(page)

    if num_pages<5:
        pages = range(1,num_pages + 1)
    elif page<=3:
        pages = range(1,6)
    elif num_pages-page<=2:
        pages = range(num_pages-4,num_pages+1)
    else:
        pages = range(page-2,page+3)

    context = {
        "order_li":order_li,
        "pages":pages,
    }

    return render(request,'users/user_center_order.html',context)




















