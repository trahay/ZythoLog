from django.contrib import admin

from .models import Beer, Brewery, Photo, Tasting


class PhotoInline(admin.TabularInline):
    model = Photo
    extra = 0


@admin.register(Brewery)
class BreweryAdmin(admin.ModelAdmin):
    search_fields = ["name"]


@admin.register(Beer)
class BeerAdmin(admin.ModelAdmin):
    list_display = ["name", "brewery", "style", "abv"]
    search_fields = ["name", "brewery__name", "style"]
    list_filter = ["style"]


@admin.register(Tasting)
class TastingAdmin(admin.ModelAdmin):
    list_display = ["beer", "date", "author_display", "rating"]
    search_fields = ["beer__name", "beer__brewery__name", "author_name", "user__username"]
    list_filter = ["date"]
    inlines = [PhotoInline]
