from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.db.models import Count, Q, Avg, Sum
from django.http import HttpResponse
from django.shortcuts import render
from django.urls import path
from django.utils import timezone
from django.utils.dateparse import parse_datetime
import csv
import json
from datetime import date, timedelta
from import_export.admin import ImportExportModelAdmin, ExportActionMixin
from import_export import resources
# BaseExportResource removed - not needed
from .models import (
    Dusun, Lorong, Penduduk, Family, DisabilitasType, 
    DisabilitasData, ReligionReference, ReferencesPageHeader, RW, RT
)
from .import_export import ImportExportManager


# Import/Export Resources
class DusunResource(resources.ModelResource):
    class Meta:
        model = Dusun
        fields = ('id', 'name', 'code', 'description', 'area_size', 'population_count', 'is_active')
        export_order = ('id', 'name', 'code', 'description', 'area_size', 'population_count', 'is_active')

class LorongResource(resources.ModelResource):
    class Meta:
        model = Lorong
        fields = ('id', 'nama_lorong', 'kode', 'dusun__name', 'ketua_lorong', 'description', 'length', 'house_count', 'is_active')
        export_order = ('id', 'nama_lorong', 'kode', 'dusun__name', 'ketua_lorong', 'description', 'length', 'house_count', 'is_active')

class PendudukResource(resources.ModelResource):
    class Meta:
        model = Penduduk
        fields = ('id', 'nik', 'name', 'gender', 'birth_place', 'birth_date', 'religion', 'education', 'occupation', 'marital_status', 'dusun__name', 'lorong__nama_lorong', 'address', 'phone_number', 'is_active', 'is_alive')
        export_order = ('id', 'nik', 'name', 'gender', 'birth_place', 'birth_date', 'religion', 'education', 'occupation', 'marital_status', 'dusun__name', 'lorong__nama_lorong', 'address', 'phone_number', 'is_active', 'is_alive')

class FamilyResource(resources.ModelResource):
    class Meta:
        model = Family
        fields = ('id', 'kk_number', 'head__name', 'family_status', 'total_members', 'total_income', 'dusun__name', 'lorong__nama_lorong', 'address', 'is_active')
        export_order = ('id', 'kk_number', 'head__name', 'family_status', 'total_members', 'total_income', 'dusun__name', 'lorong__nama_lorong', 'address', 'is_active')

class DisabilitasTypeResource(resources.ModelResource):
    class Meta:
        model = DisabilitasType
        fields = ('id', 'name', 'code', 'description', 'is_active')
        export_order = ('id', 'name', 'code', 'description', 'is_active')

class DisabilitasDataResource(resources.ModelResource):
    class Meta:
        model = DisabilitasData
        fields = ('id', 'penduduk__name', 'penduduk__nik', 'disability_type__name', 'severity', 'description', 'diagnosis_date', 'needs_assistance', 'is_active')
        export_order = ('id', 'penduduk__name', 'penduduk__nik', 'disability_type__name', 'severity', 'description', 'diagnosis_date', 'needs_assistance', 'is_active')

class ReligionReferenceResource(resources.ModelResource):
    class Meta:
        model = ReligionReference
        fields = ('id', 'name', 'code', 'is_active')
        export_order = ('id', 'name', 'code', 'is_active')


# Timezone-safe date filter
# Timezone-safe admin base class
class TimezoneSafeModelAdmin(admin.ModelAdmin):
    """Base admin class that handles timezone issues gracefully"""
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        # Handle timezone issues by using naive datetime filtering
        return qs
    
    def changelist_view(self, request, extra_context=None):
        try:
            return super().changelist_view(request, extra_context)
        except ValueError as e:
            if "invalid datetime value" in str(e).lower():
                # If timezone error occurs, redirect to a simple view
                from django.contrib import messages
                messages.warning(request, 'Date filtering temporarily disabled due to timezone configuration.')
                # Remove date filters from request
                if hasattr(request, 'GET'):
                    get_data = request.GET.copy()
                    for key in list(get_data.keys()):
                        if 'date' in key.lower():
                            get_data.pop(key)
                    request.GET = get_data
                return super().changelist_view(request, extra_context)
            raise e


@admin.register(Dusun)
class DusunAdmin(ImportExportModelAdmin):
    resource_class = DusunResource
    list_display = ['name', 'code', 'area_size', 'population_count', 'population_density', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'code', 'description']
    list_per_page = 15
    ordering = ['name']
    readonly_fields = ['created_at', 'updated_at', 'population_density']
    actions = ['update_population_count', 'export_as_csv', 'export_to_excel', 'export_to_csv', 'export_to_json', 'download_template_excel', 'bulk_export_all']
    
    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['export_actions'] = [
            {'name': 'export_to_excel', 'label': '📊 Export to Excel', 'description': 'Export selected items to Excel'},
            {'name': 'export_to_csv', 'label': '📄 Export to CSV', 'description': 'Export selected items to CSV'},
            {'name': 'export_to_json', 'label': '📋 Export to JSON', 'description': 'Export selected items to JSON'},
            {'name': 'download_template_excel', 'label': '📥 Download Template', 'description': 'Download Excel template'},
            {'name': 'bulk_export_all', 'label': '📦 Export All Data', 'description': 'Export all data to Excel'},
        ]
        return super().changelist_view(request, extra_context)
    
    def population_density(self, obj):
        if obj.area_size and obj.area_size > 0:
            density = obj.population_count / float(obj.area_size)
            return f"{density:.2f} jiwa/ha"
        return "N/A"
    population_density.short_description = 'Kepadatan Penduduk'
    
    def update_population_count(self, request, queryset):
        updated = 0
        for dusun in queryset:
            actual_count = Penduduk.objects.filter(
                dusun=dusun, is_active=True, is_alive=True
            ).count()
            dusun.population_count = actual_count
            dusun.save()
            updated += 1
        self.message_user(request, f'Updated population count for {updated} dusun(s)')
    update_population_count.short_description = "Update population count"
    
    def export_as_csv(self, request, queryset):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="dusun_export.csv"'
        writer = csv.writer(response)
        writer.writerow(['Name', 'Code', 'Area Size', 'Population Count', 'Description'])
        for obj in queryset:
            writer.writerow([obj.name, obj.code, obj.area_size, obj.population_count, obj.description])
        return response
    export_as_csv.short_description = "Export selected as CSV"
    
    fieldsets = (
        ('Informasi Dasar', {
            'fields': ('name', 'code', 'description')
        }),
        ('Data Wilayah', {
            'fields': ('area_size', 'population_count')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Lorong)
class LorongAdmin(ImportExportModelAdmin):
    resource_class = LorongResource
    list_display = ['nama_lorong', 'dusun', 'kode', 'ketua_lorong', 'length', 'house_count', 'is_active']
    list_filter = ['dusun', 'is_active', 'created_at']
    search_fields = ['nama_lorong', 'kode', 'ketua_lorong', 'dusun__name']
    list_per_page = 15
    ordering = ['dusun__name', 'nama_lorong']
    readonly_fields = ['created_at', 'updated_at']
    autocomplete_fields = ['dusun']
    actions = ['export_to_excel', 'export_to_csv', 'export_to_json', 'download_template_excel', 'bulk_export_all']
    
    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['export_actions'] = [
            {'name': 'export_to_excel', 'label': '📊 Export to Excel', 'description': 'Export selected items to Excel'},
            {'name': 'export_to_csv', 'label': '📄 Export to CSV', 'description': 'Export selected items to CSV'},
            {'name': 'export_to_json', 'label': '📋 Export to JSON', 'description': 'Export selected items to JSON'},
            {'name': 'download_template_excel', 'label': '📥 Download Template', 'description': 'Download Excel template'},
            {'name': 'bulk_export_all', 'label': '📦 Export All Data', 'description': 'Export all data to Excel'},
        ]
        return super().changelist_view(request, extra_context)
    
    fieldsets = (
        ('Informasi Dasar', {
            'fields': ('dusun', 'name', 'code', 'description')
        }),
        ('Data Jalan', {
            'fields': ('length', 'house_count')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


class DisabilitasDataInline(admin.TabularInline):
    model = DisabilitasData
    extra = 0
    fields = ['disability_type', 'severity', 'needs_assistance', 'is_active']


@admin.register(Penduduk)
class PendudukAdmin(ImportExportModelAdmin, TimezoneSafeModelAdmin):
    resource_class = PendudukResource
    list_display = [
        'nik', 'name', 'gender', 'age_display', 'dusun', 'marital_status', 
        'religion', 'education', 'is_active', 'is_alive', 'created_at'
    ]
    list_filter = [
        'gender', 'marital_status', 'religion', 'education', 'citizenship',
        'dusun', 'blood_type', 'is_active', 'is_alive'
        # 'created_at' temporarily disabled due to timezone issues
    ]
    
    def get_queryset(self, request):
        # Override to handle timezone issues
        qs = super().get_queryset(request)
        return qs.select_related('dusun', 'lorong', 'family_head')
    search_fields = ['name', 'nik', 'kk_number', 'phone_number', 'mobile_number', 'address']
    list_per_page = 20
    ordering = ['name']
    readonly_fields = ['created_at', 'updated_at', 'age_display', 'full_address_display', 'family_info']
    autocomplete_fields = ['dusun', 'lorong', 'family_head', 'created_by', 'updated_by']
    inlines = [DisabilitasDataInline]
    actions = ['mark_as_inactive', 'mark_as_active', 'export_as_csv', 'export_to_excel', 'export_to_csv', 'export_to_json', 'download_template_excel', 'bulk_export_all', 'bulk_update_dusun']
    # date_hierarchy = 'created_at'  # Disabled due to timezone issues
    list_select_related = ['dusun', 'lorong', 'family_head']
    
    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['export_actions'] = [
            {'name': 'export_to_excel', 'label': '📊 Export to Excel', 'description': 'Export selected items to Excel'},
            {'name': 'export_to_csv', 'label': '📄 Export to CSV', 'description': 'Export selected items to CSV'},
            {'name': 'export_to_json', 'label': '📋 Export to JSON', 'description': 'Export selected items to JSON'},
            {'name': 'download_template_excel', 'label': '📥 Download Template', 'description': 'Download Excel template'},
            {'name': 'bulk_export_all', 'label': '📦 Export All Data', 'description': 'Export all data to Excel'},
        ]
        return super().changelist_view(request, extra_context)
    
    def full_address_display(self, obj):
        return obj.full_address
    full_address_display.short_description = 'Alamat Lengkap'
    
    def family_info(self, obj):
        if obj.family_head:
            family_size = obj.family_size
            return format_html(
                '<strong>Kepala Keluarga:</strong> {}<br><strong>Jumlah Anggota:</strong> {} orang',
                obj.family_head.name, family_size
            )
        elif obj.is_family_head:
            return format_html(
                '<strong>Status:</strong> Kepala Keluarga<br><strong>Jumlah Anggota:</strong> {} orang',
                obj.family_size
            )
        return 'Belum ada info keluarga'
    family_info.short_description = 'Info Keluarga'
    
    def mark_as_inactive(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} penduduk marked as inactive')
    mark_as_inactive.short_description = "Mark selected as inactive"
    
    def mark_as_active(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} penduduk marked as active')
    mark_as_active.short_description = "Mark selected as active"
    
    def export_as_csv(self, request, queryset):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="penduduk_export.csv"'
        writer = csv.writer(response)
        writer.writerow([
            'NIK', 'Name', 'Gender', 'Age', 'Birth Place', 'Birth Date', 'Religion',
            'Education', 'Occupation', 'Marital Status', 'Dusun', 'Address', 'Phone'
        ])
        for obj in queryset:
            writer.writerow([
                obj.nik, obj.name, obj.get_gender_display(), obj.age,
                obj.birth_place, obj.birth_date, obj.religion,
                obj.get_education_display(), obj.occupation,
                obj.get_marital_status_display(), obj.dusun.name,
                obj.address, obj.phone_number or obj.mobile_number
            ])
        return response
    export_as_csv.short_description = "Export selected as CSV"
    
    def bulk_update_dusun(self, request, queryset):
        # This would be enhanced with a form to select dusun
        self.message_user(request, 'Bulk update dusun feature - implement with intermediate page')
    bulk_update_dusun.short_description = "Bulk update dusun"
    
    fieldsets = (
        ('Identitas Dasar', {
            'fields': ('nik', 'name', 'gender', 'birth_place', 'birth_date', 'age_display')
        }),
        ('Informasi Keluarga', {
            'fields': ('kk_number', 'family_head', 'relationship_to_head')
        }),
        ('Informasi Pribadi', {
            'fields': ('religion', 'education', 'occupation', 'marital_status')
        }),
        ('Informasi Fisik', {
            'fields': ('blood_type', 'height', 'weight'),
            'classes': ('collapse',)
        }),
        ('Kontak', {
            'fields': ('phone_number', 'mobile_number', 'email'),
            'classes': ('collapse',)
        }),
        ('Alamat', {
            'fields': ('dusun', 'lorong', 'rt_number', 'rw_number', 'house_number', 'address', 'postal_code')
        }),
        ('Kewarganegaraan', {
            'fields': ('citizenship', 'passport_number', 'passport_expiry'),
            'classes': ('collapse',)
        }),
        ('Kontak Darurat', {
            'fields': ('emergency_contact', 'emergency_phone', 'emergency_relationship'),
            'classes': ('collapse',)
        }),
        ('Status', {
            'fields': ('is_active', 'is_alive', 'death_date', 'death_place')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'created_by', 'updated_by'),
            'classes': ('collapse',)
        }),
    )
    
    def age_display(self, obj):
        return f"{obj.age} tahun"
    age_display.short_description = 'Usia'
    


@admin.register(Family)
class FamilyAdmin(ImportExportModelAdmin):
    resource_class = FamilyResource
    list_display = [
        'kk_number', 'head_name', 'family_status', 'actual_members_count', 
        'total_income_display', 'dusun', 'is_active'
    ]
    list_filter = ['family_status', 'dusun', 'is_active', 'created_at']
    search_fields = ['kk_number', 'head__name', 'head__nik', 'address']
    list_per_page = 20
    ordering = ['kk_number']
    readonly_fields = ['created_at', 'updated_at', 'actual_members_count', 'family_members_list']
    autocomplete_fields = ['head', 'dusun', 'lorong']
    actions = ['update_member_count', 'export_family_data', 'export_to_excel', 'export_to_csv', 'export_to_json', 'download_template_excel', 'bulk_export_all']
    
    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['export_actions'] = [
            {'name': 'export_to_excel', 'label': '📊 Export to Excel', 'description': 'Export selected items to Excel'},
            {'name': 'export_to_csv', 'label': '📄 Export to CSV', 'description': 'Export selected items to CSV'},
            {'name': 'export_to_json', 'label': '📋 Export to JSON', 'description': 'Export selected items to JSON'},
            {'name': 'download_template_excel', 'label': '📥 Download Template', 'description': 'Download Excel template'},
            {'name': 'bulk_export_all', 'label': '📦 Export All Data', 'description': 'Export all data to Excel'},
        ]
        return super().changelist_view(request, extra_context)
    
    def actual_members_count(self, obj):
        count = Penduduk.objects.filter(
            kk_number=obj.kk_number, is_active=True, is_alive=True
        ).count()
        if count != obj.total_members:
            return format_html(
                '<span style="color: red;">{}</span> (recorded: {})',
                count, obj.total_members
            )
        return count
    actual_members_count.short_description = 'Anggota Aktual'
    
    def total_income_display(self, obj):
        if obj.total_income:
            return f'Rp {obj.total_income:,.0f}'
        return 'Tidak diketahui'
    total_income_display.short_description = 'Pendapatan'
    
    def family_members_list(self, obj):
        members = Penduduk.objects.filter(
            kk_number=obj.kk_number, is_active=True
        ).order_by('birth_date')
        if members:
            member_list = []
            for member in members:
                status = 'Kepala Keluarga' if member == obj.head else member.relationship_to_head or 'Anggota'
                member_list.append(f'• {member.name} ({member.age} th) - {status}')
            return format_html('<br>'.join(member_list))
        return 'Tidak ada anggota'
    family_members_list.short_description = 'Daftar Anggota'
    
    def update_member_count(self, request, queryset):
        updated = 0
        for family in queryset:
            actual_count = Penduduk.objects.filter(
                kk_number=family.kk_number, is_active=True, is_alive=True
            ).count()
            family.total_members = actual_count
            family.save()
            updated += 1
        self.message_user(request, f'Updated member count for {updated} families')
    update_member_count.short_description = "Update member count"
    
    def export_family_data(self, request, queryset):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="family_export.csv"'
        writer = csv.writer(response)
        writer.writerow([
            'KK Number', 'Head Name', 'Family Status', 'Total Members', 
            'Total Income', 'Dusun', 'Address'
        ])
        for obj in queryset:
            writer.writerow([
                obj.kk_number, obj.head.name, obj.get_family_status_display(),
                obj.total_members, obj.total_income or 0, obj.dusun.name, obj.address
            ])
        return response
    export_family_data.short_description = "Export family data as CSV"
    
    fieldsets = (
        ('Informasi Keluarga', {
            'fields': ('kk_number', 'head', 'family_status', 'total_members')
        }),
        ('Data Ekonomi', {
            'fields': ('total_income',)
        }),
        ('Alamat', {
            'fields': ('dusun', 'lorong', 'rt_number', 'rw_number', 'house_number', 'address', 'postal_code')
        }),
        ('Kontak', {
            'fields': ('phone_number',)
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def head_name(self, obj):
        return obj.head.name
    head_name.short_description = 'Kepala Keluarga'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('head', 'dusun', 'lorong')


@admin.register(DisabilitasType)
class DisabilitasTypeAdmin(ImportExportModelAdmin):
    resource_class = DisabilitasTypeResource
    list_display = ['name', 'code', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'code', 'description']
    list_per_page = 15
    ordering = ['name']
    readonly_fields = ['created_at', 'updated_at']
    actions = ['export_to_excel', 'export_to_csv', 'export_to_json', 'download_template_excel', 'bulk_export_all']
    
    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['export_actions'] = [
            {'name': 'export_to_excel', 'label': '📊 Export to Excel', 'description': 'Export selected items to Excel'},
            {'name': 'export_to_csv', 'label': '📄 Export to CSV', 'description': 'Export selected items to CSV'},
            {'name': 'export_to_json', 'label': '📋 Export to JSON', 'description': 'Export selected items to JSON'},
            {'name': 'download_template_excel', 'label': '📥 Download Template', 'description': 'Download Excel template'},
            {'name': 'bulk_export_all', 'label': '📦 Export All Data', 'description': 'Export all data to Excel'},
        ]
        return super().changelist_view(request, extra_context)
    
    fieldsets = (
        ('Informasi Dasar', {
            'fields': ('name', 'code', 'description')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(DisabilitasData)
class DisabilitasDataAdmin(ImportExportModelAdmin):
    resource_class = DisabilitasDataResource
    list_display = [
        'penduduk_name', 'penduduk_age', 'disability_type', 'severity', 
        'needs_assistance', 'diagnosis_date', 'is_active', 'created_at'
    ]
    list_filter = [
        'disability_type', 'severity', 'needs_assistance', 'is_active', 
        'created_at', 'penduduk__dusun'
    ]
    search_fields = ['penduduk__name', 'penduduk__nik', 'disability_type__name', 'description']
    list_per_page = 20
    ordering = ['penduduk__name']
    readonly_fields = ['created_at', 'updated_at', 'penduduk_info']
    autocomplete_fields = ['penduduk', 'disability_type']
    actions = ['generate_assistance_report', 'export_disability_data', 'export_to_excel', 'export_to_csv', 'export_to_json', 'download_template_excel', 'bulk_export_all']
    
    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['export_actions'] = [
            {'name': 'export_to_excel', 'label': '📊 Export to Excel', 'description': 'Export selected items to Excel'},
            {'name': 'export_to_csv', 'label': '📄 Export to CSV', 'description': 'Export selected items to CSV'},
            {'name': 'export_to_json', 'label': '📋 Export to JSON', 'description': 'Export selected items to JSON'},
            {'name': 'download_template_excel', 'label': '📥 Download Template', 'description': 'Download Excel template'},
            {'name': 'bulk_export_all', 'label': '📦 Export All Data', 'description': 'Export all data to Excel'},
        ]
        return super().changelist_view(request, extra_context)
    
    def penduduk_age(self, obj):
        return f'{obj.penduduk.age} tahun'
    penduduk_age.short_description = 'Usia'
    
    def penduduk_info(self, obj):
        return format_html(
            '<strong>NIK:</strong> {}<br><strong>Alamat:</strong> {}<br><strong>Kontak:</strong> {}',
            obj.penduduk.nik,
            obj.penduduk.dusun.name,
            obj.penduduk.phone_number or obj.penduduk.mobile_number or 'Tidak ada'
        )
    penduduk_info.short_description = 'Info Penduduk'
    
    def generate_assistance_report(self, request, queryset):
        assistance_needed = queryset.filter(needs_assistance=True).count()
        total = queryset.count()
        self.message_user(
            request, 
            f'Report: {assistance_needed} out of {total} selected records need assistance'
        )
    generate_assistance_report.short_description = "Generate assistance report"
    
    def export_disability_data(self, request, queryset):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="disability_export.csv"'
        writer = csv.writer(response)
        writer.writerow([
            'NIK', 'Name', 'Age', 'Dusun', 'Disability Type', 'Severity',
            'Needs Assistance', 'Diagnosis Date', 'Description'
        ])
        for obj in queryset:
            writer.writerow([
                obj.penduduk.nik, obj.penduduk.name, obj.penduduk.age,
                obj.penduduk.dusun.name, obj.disability_type.name,
                obj.get_severity_display(), 'Ya' if obj.needs_assistance else 'Tidak',
                obj.diagnosis_date, obj.description
            ])
        return response
    export_disability_data.short_description = "Export disability data as CSV"
    
    fieldsets = (
        ('Informasi Dasar', {
            'fields': ('penduduk', 'disability_type', 'severity', 'description')
        }),
        ('Data Medis', {
            'fields': ('diagnosis_date', 'needs_assistance')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def penduduk_name(self, obj):
        return obj.penduduk.name
    penduduk_name.short_description = 'Nama Penduduk'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('penduduk', 'disability_type')


@admin.register(ReligionReference)
class ReligionReferenceAdmin(ImportExportModelAdmin):
    resource_class = ReligionReferenceResource
    list_display = ['name', 'code', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'code']
    list_per_page = 15
    ordering = ['name']
    readonly_fields = ['created_at', 'updated_at']
    actions = ['export_to_excel', 'export_to_csv', 'export_to_json', 'download_template_excel', 'bulk_export_all']
    
    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['export_actions'] = [
            {'name': 'export_to_excel', 'label': '📊 Export to Excel', 'description': 'Export selected items to Excel'},
            {'name': 'export_to_csv', 'label': '📄 Export to CSV', 'description': 'Export selected items to CSV'},
            {'name': 'export_to_json', 'label': '📋 Export to JSON', 'description': 'Export selected items to JSON'},
            {'name': 'download_template_excel', 'label': '📥 Download Template', 'description': 'Download Excel template'},
            {'name': 'bulk_export_all', 'label': '📦 Export All Data', 'description': 'Export all data to Excel'},
        ]
        return super().changelist_view(request, extra_context)
    
    fieldsets = (
        ('Informasi Dasar', {
            'fields': ('name', 'code')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


# Custom Admin Views for Statistics
class PopulationStatisticsView:
    def population_statistics_view(self, request):
        # Population statistics
        total_population = Penduduk.objects.filter(is_active=True, is_alive=True).count()
        male_population = Penduduk.objects.filter(is_active=True, is_alive=True, gender='L').count()
        female_population = Penduduk.objects.filter(is_active=True, is_alive=True, gender='P').count()
        
        # Age statistics
        today = date.today()
        children = Penduduk.objects.filter(
            is_active=True, is_alive=True,
            birth_date__gte=today - timedelta(days=18*365)
        ).count()
        adults = total_population - children
        
        # Education statistics
        education_stats = Penduduk.objects.filter(
            is_active=True, is_alive=True
        ).values('education').annotate(count=Count('id'))
        
        # Religion statistics
        religion_stats = Penduduk.objects.filter(
            is_active=True, is_alive=True
        ).values('religion').annotate(count=Count('id'))
        
        # Family statistics
        total_families = Family.objects.filter(is_active=True).count()
        avg_family_size = Family.objects.filter(is_active=True).aggregate(
            avg_size=Avg('total_members')
        )['avg_size'] or 0
        
        # Disability statistics
        total_disabilities = DisabilitasData.objects.filter(is_active=True).count()
        assistance_needed = DisabilitasData.objects.filter(
            is_active=True, needs_assistance=True
        ).count()
        
        context = {
            'title': 'Statistik Kependudukan',
            'total_population': total_population,
            'male_population': male_population,
            'female_population': female_population,
            'children': children,
            'adults': adults,
            'education_stats': education_stats,
            'religion_stats': religion_stats,
            'total_families': total_families,
            'avg_family_size': round(avg_family_size, 2),
            'total_disabilities': total_disabilities,
            'assistance_needed': assistance_needed,
        }
        
        return render(request, 'admin/population_statistics.html', context)

# Add custom URLs to admin
def get_urls():
    from django.urls import path
    urls = [
        path('population-statistics/', 
             PopulationStatisticsView().population_statistics_view,
             name='population_statistics'),
    ]
    return urls

# Customize admin site headers
admin.site.site_header = "Administrasi Desa Pulosarok"
admin.site.site_title = "Admin Pulosarok"
admin.site.index_title = "Dashboard Administrasi"

# Add custom admin actions
def make_active(modeladmin, request, queryset):
    updated = queryset.update(is_active=True)
    modeladmin.message_user(request, f'{updated} items marked as active')
make_active.short_description = "✅ Mark selected items as active"

def make_inactive(modeladmin, request, queryset):
    updated = queryset.update(is_active=False)
    modeladmin.message_user(request, f'{updated} items marked as inactive')
make_inactive.short_description = "❌ Mark selected items as inactive"

# Export actions with icons
def export_to_excel(modeladmin, request, queryset):
    """Export selected items to Excel"""
    if not queryset.exists():
        modeladmin.message_user(request, 'No items selected for export', level='WARNING')
        return
    
    try:
        manager = ExportImportManager()
        model_name = modeladmin.model._meta.model_name
        
        # Create temporary queryset with selected objects
        obj_ids = list(queryset.values_list('id', flat=True))
        temp_queryset = modeladmin.model.objects.filter(id__in=obj_ids)
        
        response = manager.export_data(model_name, 'excel', {}, True)
        response['Content-Disposition'] = f'attachment; filename="{model_name}_selected_{len(obj_ids)}_items.xlsx"'
        
        modeladmin.message_user(request, f'Successfully exported {len(obj_ids)} items to Excel', level='SUCCESS')
        return response
        
    except Exception as e:
        modeladmin.message_user(request, f'Export failed: {str(e)}', level='ERROR')
export_to_excel.short_description = "📊 Export selected to Excel"

def export_to_csv(modeladmin, request, queryset):
    """Export selected items to CSV"""
    if not queryset.exists():
        modeladmin.message_user(request, 'No items selected for export', level='WARNING')
        return
    
    try:
        manager = ExportImportManager()
        model_name = modeladmin.model._meta.model_name
        
        # Create temporary queryset with selected objects
        obj_ids = list(queryset.values_list('id', flat=True))
        temp_queryset = modeladmin.model.objects.filter(id__in=obj_ids)
        
        response = manager.export_data(model_name, 'csv', {}, True)
        response['Content-Disposition'] = f'attachment; filename="{model_name}_selected_{len(obj_ids)}_items.csv"'
        
        modeladmin.message_user(request, f'Successfully exported {len(obj_ids)} items to CSV', level='SUCCESS')
        return response
        
    except Exception as e:
        modeladmin.message_user(request, f'Export failed: {str(e)}', level='ERROR')
export_to_csv.short_description = "📄 Export selected to CSV"

def export_to_json(modeladmin, request, queryset):
    """Export selected items to JSON"""
    if not queryset.exists():
        modeladmin.message_user(request, 'No items selected for export', level='WARNING')
        return
    
    try:
        manager = ExportImportManager()
        model_name = modeladmin.model._meta.model_name
        
        # Create temporary queryset with selected objects
        obj_ids = list(queryset.values_list('id', flat=True))
        temp_queryset = modeladmin.model.objects.filter(id__in=obj_ids)
        
        response = manager.export_data(model_name, 'json', {}, True)
        response['Content-Disposition'] = f'attachment; filename="{model_name}_selected_{len(obj_ids)}_items.json"'
        
        modeladmin.message_user(request, f'Successfully exported {len(obj_ids)} items to JSON', level='SUCCESS')
        return response
        
    except Exception as e:
        modeladmin.message_user(request, f'Export failed: {str(e)}', level='ERROR')
export_to_json.short_description = "📋 Export selected to JSON"

def download_template_excel(modeladmin, request, queryset):
    """Download Excel template for this model"""
    try:
        manager = ExportImportManager()
        model_name = modeladmin.model._meta.model_name
        
        # Create empty queryset for template
        empty_queryset = modeladmin.model.objects.none()
        
        response = manager.export_data(model_name, 'excel', {}, True)
        response['Content-Disposition'] = f'attachment; filename="template_{model_name}.xlsx"'
        
        modeladmin.message_user(request, f'Excel template downloaded for {model_name}', level='SUCCESS')
        return response
        
    except Exception as e:
        modeladmin.message_user(request, f'Template download failed: {str(e)}', level='ERROR')
download_template_excel.short_description = "📥 Download Excel Template"

def bulk_export_all(modeladmin, request, queryset):
    """Export all data of this model"""
    try:
        manager = ExportImportManager()
        model_name = modeladmin.model._meta.model_name
        
        # Get all objects
        all_queryset = modeladmin.model.objects.all()
        
        response = manager.export_data(model_name, 'excel', {}, True)
        response['Content-Disposition'] = f'attachment; filename="{model_name}_all_data.xlsx"'
        
        modeladmin.message_user(request, f'Successfully exported all {all_queryset.count()} items to Excel', level='SUCCESS')
        return response
        
    except Exception as e:
        modeladmin.message_user(request, f'Bulk export failed: {str(e)}', level='ERROR')
bulk_export_all.short_description = "📦 Export All Data to Excel"

# Register global admin actions
admin.site.add_action(make_active, 'make_active')
admin.site.add_action(make_inactive, 'make_inactive')
admin.site.add_action(export_to_excel, 'export_to_excel')
admin.site.add_action(export_to_csv, 'export_to_csv')
admin.site.add_action(export_to_json, 'export_to_json')
admin.site.add_action(download_template_excel, 'download_template_excel')
admin.site.add_action(bulk_export_all, 'bulk_export_all')

# Custom admin view for statistics
class StatisticsAdminView:
    """Custom admin view for population statistics"""
    
    def statistics_view(self, request):
        """Display population statistics"""
        from django.shortcuts import render
        from django.contrib.admin.views.decorators import staff_member_required
        from django.utils.decorators import method_decorator
        from django.views.generic import TemplateView
        
        # Get statistics
        total_penduduk = Penduduk.objects.filter(is_active=True, is_alive=True).count()
        total_family = Family.objects.filter(is_active=True).count()
        total_dusun = Dusun.objects.filter(is_active=True).count()
        total_lorong = Lorong.objects.filter(is_active=True).count()
        total_disabilitas = DisabilitasData.objects.filter(is_active=True).count()
        total_religion = ReligionReference.objects.filter(is_active=True).count()
        
        # Gender statistics
        male_count = Penduduk.objects.filter(is_active=True, is_alive=True, gender='L').count()
        female_count = Penduduk.objects.filter(is_active=True, is_alive=True, gender='P').count()
        
        # Age statistics
        from datetime import date, timedelta
        today = date.today()
        children = Penduduk.objects.filter(
            is_active=True, is_alive=True,
            birth_date__gte=today - timedelta(days=18*365)
        ).count()
        adults = total_penduduk - children
        
        context = {
            'title': 'Statistik Kependudukan Desa Pulosarok',
            'total_penduduk': total_penduduk,
            'total_family': total_family,
            'total_dusun': total_dusun,
            'total_lorong': total_lorong,
            'total_disabilitas': total_disabilitas,
            'total_religion': total_religion,
            'male_count': male_count,
            'female_count': female_count,
            'children': children,
            'adults': adults,
        }
        
        return render(request, 'admin/statistics.html', context)


@admin.register(ReferencesPageHeader)
class ReferencesPageHeaderAdmin(admin.ModelAdmin):
    list_display = ['title', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['title', 'description']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Header Information', {
            'fields': ('title', 'description', 'background_image')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )


# Add statistics URL to admin
def get_admin_urls():
    from django.urls import path
    urls = [
        path('statistics/', StatisticsAdminView().statistics_view, name='statistics'),
    ]
    return urls

# RW Admin
@admin.register(RW)
class RWAdmin(ImportExportModelAdmin, ExportActionMixin):
    list_display = ('rw_number', 'dusun', 'ketua_rw', 'population_count', 'is_active', 'created_at')
    list_filter = ('dusun', 'is_active', 'created_at')
    search_fields = ('rw_number', 'dusun__name', 'ketua_rw__name', 'ketua_rw__nik')
    list_editable = ('is_active',)
    ordering = ('dusun__name', 'rw_number')
    
    fieldsets = (
        ('Informasi Dasar', {
            'fields': ('dusun', 'rw_number', 'ketua_rw', 'description')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('dusun', 'ketua_rw')

# RT Admin
@admin.register(RT)
class RTAdmin(ImportExportModelAdmin, ExportActionMixin):
    list_display = ('rt_number', 'rw', 'dusun_name', 'ketua_rt', 'population_count', 'is_active', 'created_at')
    list_filter = ('rw__dusun', 'rw', 'is_active', 'created_at')
    search_fields = ('rt_number', 'rw__rw_number', 'rw__dusun__name', 'ketua_rt__name', 'ketua_rt__nik')
    list_editable = ('is_active',)
    ordering = ('rw__dusun__name', 'rw__rw_number', 'rt_number')
    
    fieldsets = (
        ('Informasi Dasar', {
            'fields': ('rw', 'rt_number', 'ketua_rt', 'description')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('rw__dusun', 'ketua_rt')
    
    def dusun_name(self, obj):
        return obj.rw.dusun.name
    dusun_name.short_description = 'Dusun'
    dusun_name.admin_order_field = 'rw__dusun__name'

# Add custom URLs to admin site
original_get_urls = admin.site.get_urls
admin.site.get_urls = lambda: original_get_urls() + get_admin_urls()
