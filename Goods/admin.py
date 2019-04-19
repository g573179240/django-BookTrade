from django.contrib import admin

# Register your models here.
from django.contrib import admin
from Goods.models import Goods

class GoodsAdmin(admin.ModelAdmin):
    list_display = ('title','desc','price','type_id','create_time')
    list_editable = ('price',)
    search_fields = ('title',)
    list_filter = ('type_id',)
    date_hierarchy = 'create_time'
    fieldsets = (
        ('基本选项',{'fields':('title','desc')}),
        ('高级选项',{'fields':('price','type_id')}),
    )

admin.site.register(Goods,GoodsAdmin)