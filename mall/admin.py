from django.contrib import admin
from markdownx.admin import MarkdownxModelAdmin

from .models import Product, Category, Tag, Comment, Publisher

admin.site.register(Product, MarkdownxModelAdmin)
admin.site.register(Comment)

class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug':('name', )}

admin.site.register(Category, CategoryAdmin)

class PublisherAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}

admin.site.register(Publisher, PublisherAdmin)

class TagAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug':('name', )}

admin.site.register(Tag, TagAdmin)
