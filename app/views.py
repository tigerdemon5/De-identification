from django.shortcuts import render
import pandas as pd
import hashlib
import os
from .forms import CsvProcessForm
from django.conf import settings

def mask_string(value, mask_char='*'):
    """값을 문자열로 변환하고 마스킹으로 처리"""
    str_value = str(value)
    return str_value[0] + mask_char * (len(str_value) - 1)

def sha256_encode(value):
    """문자열을 SHA-256으로 암호화하는 함수"""
    str_value = str(value)
    return hashlib.sha256(str_value.encode()).hexdigest() if str_value else str_value

def process_csv(file_path, operations):
    """CSV 파일을 읽고 주어진 작업(마스킹, 해싱, 삭제)을 수행하는 함수"""
    # CSV 파일 읽기
    try:
        data = pd.read_csv(file_path, encoding='utf-8')
    except UnicodeDecodeError:
        data = pd.read_csv(file_path, encoding='cp949')

    # 각 필드에 대해 주어진 작업 수행
    for field_name, operation in operations:
        if operation == 'mask':
            if field_name in data.columns:
                data[field_name] = data[field_name].apply(mask_string)
        elif operation == 'hash':
            if field_name in data.columns:
                data[field_name] = data[field_name].apply(sha256_encode)
        elif operation == 'delete':
            if field_name in data.columns:
                data.drop(columns=[field_name], inplace=True)

    return data

def upload_csv(request):
    if request.method == 'POST':
        additional_fields_count = 1
        for key in request.POST.keys():
            if key.startswith('additional_field_name_'):
                additional_fields_count += 1

        # 폼에 추가된 필드의 수를 전달하여 초기화
        form = CsvProcessForm(request.POST, request.FILES, additional_fields_count=additional_fields_count)

        if form.is_valid():
            # 기본 필드 처리
            csv_file = form.cleaned_data['file']
            field_name = form.cleaned_data['field_name']
            operation = form.cleaned_data['operation']
            output_file_name = form.cleaned_data['output_file_name']

            # 처음 필드와 작업 추가
            operations = [(field_name, operation)]

            # 추가 필드 및 작업 수집
            for i in range(0, additional_fields_count + 1):
                additional_field_name = form.cleaned_data.get(f'additional_field_name_{i}')
                additional_operation = form.cleaned_data.get(f'additional_operation_{i}')
                if additional_field_name and additional_operation:
                    operations.append((additional_field_name, additional_operation))

            # 파일 저장 경로 생성
            if not os.path.exists(settings.MEDIA_ROOT):
                os.makedirs(settings.MEDIA_ROOT)

            uploaded_file_path = os.path.join(settings.MEDIA_ROOT, csv_file.name)
            with open(uploaded_file_path, 'wb+') as destination:
                for chunk in csv_file.chunks():
                    destination.write(chunk)

            # CSV 처리
            processed_data = process_csv(uploaded_file_path, operations)
            output_path = os.path.join(settings.MEDIA_ROOT, f'{output_file_name}.csv')
            processed_data.to_csv(output_path, index=False, encoding='utf-8-sig')

            # 다운로드 페이지로 리다이렉트
            return render(request, 'download.html', {'file_url': f'/media/{output_file_name}.csv'})
    else:
        form = CsvProcessForm()

    return render(request, 'upload.html', {'form': form})


