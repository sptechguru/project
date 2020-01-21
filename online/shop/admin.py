from django.contrib import admin

# Register your models here.
from .models import Product, Contact, Orders,OrderUpdate

admin.site.register(Product)
admin.site.register(Contact)
admin.site.register(Orders)
admin.site.register(OrderUpdate)


# class ContactAdmin(admin.ModelAdmin):
# 	list_display = ('name','Email','date_created','last_modified','is_draft')
# admin.site.register(Contact,ContactAdmin)

