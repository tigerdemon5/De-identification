from django import forms

class CsvProcessForm(forms.Form):
    file = forms.FileField(label='CSV 파일')
    field_name = forms.CharField(label='필드명')
    operation = forms.ChoiceField(label='작업 선택', choices=[('mask', '마스킹'), ('hash', '암호화'), ('delete', '삭제')])
    output_file_name = forms.CharField(label='출력 파일명', required=False)

    def __init__(self, *args, **kwargs):
        additional_fields_count = kwargs.pop('additional_fields_count', 0)
        super().__init__(*args, **kwargs)

        for i in range(1, additional_fields_count + 1):
            self.fields[f'additional_field_name_{i}'] = forms.CharField(label=f'추가 필드명 {i}', required=False)
            self.fields[f'additional_operation_{i}'] = forms.ChoiceField(label=f'작업 선택 {i}',
                                                                         choices=[('mask', '마스킹'), ('hash', '암호화'), ('delete', '삭제')],
                                                                         required=False)

