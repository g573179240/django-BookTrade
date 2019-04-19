from django.db import models
from BaseModel.base_model import *
from tinymce.models import HTMLField
from Goods.enums import *
# Create your models here.

class GoodsManager(models.Manager):
    # sort = 'new' 按照创建时间排序
    # sort = 'hot' 按照关注度排序
    # sort = 'price' 按照价格进行排序
    # sort = 'default' 默认排序
    def get_goods_by_type(self,type_id,limit=None,sort='default'):
        if sort == 'new':
            order_by = ('-create_time',)
        elif sort == 'price':
            order_by = ('price',)
        elif sort == 'hot':
            order_by = ('-views',)
        else:
            order_by = ('-pk',)
            #按照primary_key降序排列
        #查询结果
        goods_li = self.filter(type_id=type_id).order_by(*order_by)
        #查看结果集的限制
        if limit:
            goods_li = goods_li[:limit]
        return goods_li

    def get_goods_by_id(self,goods_id):
        try:
            goods = self.get(id=goods_id)
        except self.model.DoesNotExist:
            goods = None
        return goods


class Goods(BaseModel):
    goods_type_choices = ((k,v) for k,v in GOODS_TYPE.items())
    trade_way_choices = ((k,v) for k,v in TRADE_WAY.items())
    status_choices = ((k,v) for k,v in STATUS_CHOICE.items())
    title = models.CharField(max_length=20,verbose_name='宝贝名称')
    desc = models.CharField(max_length=200,verbose_name='宝贝简介')
    detail = HTMLField(verbose_name='商品详情')
    image = models.ImageField(upload_to='Goods',verbose_name='图片')
    price = models.DecimalField(max_digits=10,decimal_places=2,verbose_name='价格')
    type_id = models.SmallIntegerField(default=PHONE_DIGITAL,choices=goods_type_choices,verbose_name='分类')
    trade_way = models.SmallIntegerField(default=MAIL,choices = trade_way_choices,verbose_name='交易方式')
    stock = models.IntegerField(default=1,verbose_name='数量')
    sales = models.IntegerField(default=0,verbose_name='销量')
    views = models.IntegerField(default=0,verbose_name='浏览数量')
    status = models.SmallIntegerField(default=ONLINE,choices=status_choices,verbose_name='状态')

    objects = GoodsManager()

    def __str__(self):
        return self.title

    class Meta:
        db_table = 's_goods'
        verbose_name = '宝贝'
        verbose_name_plural = '宝贝'

