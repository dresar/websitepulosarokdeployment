from django.contrib import admin
from .models import (
    BusinessCategory, Business, BusinessOwner, BusinessProduct, 
    BusinessFinance, UKM, Koperasi, BUMG, Aset, LayananJasa, 
    BusinessPageHeader, JenisKoperasi
)


@admin.register(BusinessCategory)
class BusinessCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description']
    ordering = ['name']


@admin.register(Business)
class BusinessAdmin(admin.ModelAdmin):
    list_display = ['name', 'business_type', 'status', 'category', 'created_at']
    list_filter = ['business_type', 'status', 'category', 'created_at']
    search_fields = ['name', 'description']
    ordering = ['-created_at']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(BusinessOwner)
class BusinessOwnerAdmin(admin.ModelAdmin):
    list_display = ['business', 'owner', 'ownership_percentage', 'is_primary']
    list_filter = ['is_primary', 'created_at']
    search_fields = ['business__name', 'owner__nama']


@admin.register(BusinessProduct)
class BusinessProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'business', 'price', 'is_active']
    list_filter = ['is_active', 'business__business_type']
    search_fields = ['name', 'business__name', 'description']
    ordering = ['-created_at']


@admin.register(BusinessFinance)
class BusinessFinanceAdmin(admin.ModelAdmin):
    list_display = ['business', 'initial_capital', 'monthly_revenue', 'monthly_expenses']
    list_filter = ['created_at']
    search_fields = ['business__name']
    ordering = ['-created_at']


@admin.register(UKM)
class UKMAdmin(admin.ModelAdmin):
    list_display = ['nama_usaha', 'pemilik', 'jenis_usaha', 'skala_usaha', 'status']
    list_filter = ['status', 'skala_usaha', 'jenis_usaha']
    search_fields = ['nama_usaha', 'pemilik', 'jenis_usaha', 'produk_utama']
    ordering = ['-created_at']


@admin.register(Koperasi)
class KoperasiAdmin(admin.ModelAdmin):
    list_display = ['nama', 'nomor_badan_hukum', 'ketua', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['nama', 'ketua', 'sekretaris', 'bendahara']
    ordering = ['-created_at']


@admin.register(BUMG)
class BUMGAdmin(admin.ModelAdmin):
    list_display = ['nama', 'nomor_sk', 'direktur', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['nama', 'direktur', 'nomor_sk']
    ordering = ['-created_at']


@admin.register(Aset)
class AsetAdmin(admin.ModelAdmin):
    list_display = ['name', 'business', 'value', 'is_active']
    list_filter = ['is_active', 'business__business_type']
    search_fields = ['name', 'business__name', 'description']
    ordering = ['-created_at']


@admin.register(LayananJasa)
class LayananJasaAdmin(admin.ModelAdmin):
    list_display = ['nama', 'penyedia', 'kategori', 'harga_min', 'status']
    list_filter = ['status', 'kategori']
    search_fields = ['nama', 'penyedia', 'kategori']
    ordering = ['-created_at']


@admin.register(BusinessPageHeader)
class BusinessPageHeaderAdmin(admin.ModelAdmin):
    list_display = ['title', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['title', 'subtitle']


@admin.register(JenisKoperasi)
class JenisKoperasiAdmin(admin.ModelAdmin):
    list_display = ['nama', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['nama', 'deskripsi']
