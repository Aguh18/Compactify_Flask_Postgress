from flask_wtf import FlaskForm
from wtforms import (StringField, TextAreaField, IntegerField, BooleanField,RadioField, FileField)
from wtforms.validators import InputRequired, Length, ValidationError


# Fungsi validasi untuk memeriksa apakah file adalah gambar
def validate_Docx(form, field):
    if field.data:
        file = field.data
        if file.filename == '':
            raise ValidationError('Pilih Docx')
        if not allowed_file(file.filename):
            raise ValidationError('Hanya file doc dan docx  yang diizinkan!')

# Fungsi untuk memeriksa ekstensi file yang diizinkan
def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'mp3'}
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


class Audioform(FlaskForm):
    file = FileField("file", validators=[InputRequired(), validate_Docx ])
