from django.db import models
from BaseModel.base_model import BaseModel
from Function.get_hash import *

class PassportManager(models.Manager):
    # 添加账户信息
    def add_one_passport(self,username,password,email):
        passport = self.create(username=username,password=get_hash(password),email=email)
        return passport
    # 查找账户信息 根据用户名和密码查找
    def get_one_passport(self,username,password):
        try:
            passport = self.get(username=username,password=get_hash(password))
        #如果找不到则返回用户不存在
        except self.model.DoesNotExist:
            passport = None
        return passport

class AddressManager(models.Manager):
    # 查询指定用户默认收货地址
    def get_default_address(self,passport_id):
        try:
            addr = self.get(passport_id=passport_id,is_default=True)
        except self.model.DoesNotExist:
            #没有默认地址
            addr = None
        return addr
    # 添加收货地址
    def add_one_address(self,passport_id,recipient_name,recipient_addr,zip_code,recipient_phone):
        # 判断是否有默认收货地址
        addr = self.get_default_address(passport_id=passport_id)
        if addr:
            is_default = False
        else:
            is_default = True
        #添加一个地址
        addr = self.create(passport_id=passport_id,
                           recipient_name=recipient_name,
                           recipient_addr=recipient_addr,
                           recipient_phone=recipient_phone,
                           zip_code=zip_code,
                           is_default=is_default)
        return addr

class Passport(BaseModel):
    # 通行证
    username = models.CharField(max_length=30,unique=True,verbose_name='用户名称')
    password = models.CharField(max_length=50,verbose_name='用户密码')
    email = models.EmailField(verbose_name='用户邮箱')
    is_active = models.BooleanField(default=False,verbose_name='激活状态')

    #通行证管理
    objects = PassportManager()

    class Meta:
        db_table = 's_user_account'

class Address(BaseModel):
    recipient_name = models.CharField(max_length=20,verbose_name='收件人')
    recipient_addr = models.CharField(max_length=256,verbose_name='收件地址')
    zip_code = models.CharField(max_length=6,verbose_name='邮政编码')
    recipient_phone = models.CharField(max_length=11,verbose_name='联系电话')
    is_default = models.BooleanField(default=False,verbose_name='是否默认')
    passport = models.ForeignKey('Passport',verbose_name='账户')

    objects = AddressManager()

    class Meta:
        db_table = 's_user_address'
