import os
from django.http import HttpResponse, FileResponse
from django.conf import settings
from pathlib import Path


def get_import_template(request, model_name):
    """Download template file yang sudah dibuat sebelumnya"""
    try:
        # Path ke file template
        template_dir = Path(settings.BASE_DIR) / "templates"
        template_file = template_dir / f"{model_name}_lengkap.xlsx"
        
        # Cek apakah file ada
        if not template_file.exists():
            return HttpResponse(
                f'Template file tidak ditemukan: {template_file}',
                content_type='text/plain',
                status=404
            )
        
        # Buka dan return file
        response = FileResponse(
            open(template_file, 'rb'),
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = f'attachment; filename="{model_name}_template_lengkap.xlsx"'
        
        return response
        
    except Exception as e:
        return HttpResponse(
            f'Error downloading template: {str(e)}',
            content_type='text/plain',
            status=500
        )


def generate_rt_template():
    """Generate RT import template"""
    # Create sample data
    sample_data = [
        {
            'RW_ID': 1,
            'RT_Number': '001',
            'Description': 'RT 001 - Contoh'
        },
        {
            'RW_ID': 1,
            'RT_Number': '002', 
            'Description': 'RT 002 - Contoh'
        }
    ]
    
    df = pd.DataFrame(sample_data)
    
    # Create Excel file
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='RT_Import', index=False)
        
        # Get workbook and worksheet
        workbook = writer.book
        worksheet = writer.sheets['RT_Import']
        
        # Style the header
        header_font = Font(bold=True, color='FFFFFF')
        header_fill = PatternFill(start_color='366092', end_color='366092', fill_type='solid')
        
        for cell in worksheet[1]:
            cell.font = header_font
            cell.fill = header_fill
            cell.alignment = Alignment(horizontal='center')
    
    output.seek(0)
    
    response = HttpResponse(
        output.getvalue(),
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename="rt_import_template.xlsx"'
    return response


def generate_rw_template():
    """Generate RW import template"""
    sample_data = [
        {
            'Dusun_ID': 1,
            'RW_Number': '001',
            'Description': 'RW 001 - Contoh'
        },
        {
            'Dusun_ID': 1,
            'RW_Number': '002',
            'Description': 'RW 002 - Contoh'
        }
    ]
    
    df = pd.DataFrame(sample_data)
    
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='RW_Import', index=False)
        
        workbook = writer.book
        worksheet = writer.sheets['RW_Import']
        
        header_font = Font(bold=True, color='FFFFFF')
        header_fill = PatternFill(start_color='366092', end_color='366092', fill_type='solid')
        
        for cell in worksheet[1]:
            cell.font = header_font
            cell.fill = header_fill
            cell.alignment = Alignment(horizontal='center')
    
    output.seek(0)
    
    response = HttpResponse(
        output.getvalue(),
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename="rw_import_template.xlsx"'
    return response


def generate_dusun_template():
    """Generate Dusun import template"""
    sample_data = [
        {
            'Name': 'Dusun Pulosarok Utara',
            'Description': 'Dusun bagian utara - Contoh'
        },
        {
            'Name': 'Dusun Pulosarok Selatan',
            'Description': 'Dusun bagian selatan - Contoh'
        }
    ]
    
    df = pd.DataFrame(sample_data)
    
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='Dusun_Import', index=False)
        
        workbook = writer.book
        worksheet = writer.sheets['Dusun_Import']
        
        header_font = Font(bold=True, color='FFFFFF')
        header_fill = PatternFill(start_color='366092', end_color='366092', fill_type='solid')
        
        for cell in worksheet[1]:
            cell.font = header_font
            cell.fill = header_fill
            cell.alignment = Alignment(horizontal='center')
    
    output.seek(0)
    
    response = HttpResponse(
        output.getvalue(),
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename="dusun_import_template.xlsx"'
    return response


def generate_lorong_template():
    """Generate Lorong import template"""
    sample_data = [
        {
            'Dusun_ID': 1,
            'Lorong_Code': 'L001',
            'Name': 'Lorong 001',
            'Description': 'Lorong pertama - Contoh'
        },
        {
            'Dusun_ID': 1,
            'Lorong_Code': 'L002',
            'Name': 'Lorong 002',
            'Description': 'Lorong kedua - Contoh'
        }
    ]
    
    df = pd.DataFrame(sample_data)
    
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='Lorong_Import', index=False)
        
        workbook = writer.book
        worksheet = writer.sheets['Lorong_Import']
        
        header_font = Font(bold=True, color='FFFFFF')
        header_fill = PatternFill(start_color='366092', end_color='366092', fill_type='solid')
        
        for cell in worksheet[1]:
            cell.font = header_font
            cell.fill = header_fill
            cell.alignment = Alignment(horizontal='center')
    
    output.seek(0)
    
    response = HttpResponse(
        output.getvalue(),
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename="lorong_import_template.xlsx"'
    return response


def generate_keluarga_template():
    """Generate Keluarga import template"""
    sample_data = [
        {
            'Family_Name': 'Keluarga Ahmad',
            'Address': 'Jl. Merdeka No. 1',
            'RT_ID': 1
        },
        {
            'Family_Name': 'Keluarga Siti',
            'Address': 'Jl. Merdeka No. 2',
            'RT_ID': 2
        }
    ]
    
    df = pd.DataFrame(sample_data)
    
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='Keluarga_Import', index=False)
        
        workbook = writer.book
        worksheet = writer.sheets['Keluarga_Import']
        
        header_font = Font(bold=True, color='FFFFFF')
        header_fill = PatternFill(start_color='366092', end_color='366092', fill_type='solid')
        
        for cell in worksheet[1]:
            cell.font = header_font
            cell.fill = header_fill
            cell.alignment = Alignment(horizontal='center')
    
    output.seek(0)
    
    response = HttpResponse(
        output.getvalue(),
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename="keluarga_import_template.xlsx"'
    return response


def generate_penduduk_template():
    """Generate Penduduk import template"""
    sample_data = [
        {
            'NIK': '1234567890123456',
            'Name': 'Ahmad Suryadi',
            'Gender': 'L',
            'Birth_Place': 'Jakarta',
            'Birth_Date': '1990-01-01',
            'Religion': 'Islam',
            'Marital_Status': 'Kawin',
            'Occupation': 'Wiraswasta',
            'Phone': '081234567890',
            'Dusun_ID': 1,
            'Lorong_ID': 1,
            'RT_ID': 1,
            'RW_ID': 1,
            'Address': 'Jl. Merdeka No. 1'
        }
    ]
    
    df = pd.DataFrame(sample_data)
    
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='Penduduk_Import', index=False)
        
        workbook = writer.book
        worksheet = writer.sheets['Penduduk_Import']
        
        header_font = Font(bold=True, color='FFFFFF')
        header_fill = PatternFill(start_color='366092', end_color='366092', fill_type='solid')
        
        for cell in worksheet[1]:
            cell.font = header_font
            cell.fill = header_fill
            cell.alignment = Alignment(horizontal='center')
    
    output.seek(0)
    
    response = HttpResponse(
        output.getvalue(),
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename="penduduk_import_template.xlsx"'
    return response
