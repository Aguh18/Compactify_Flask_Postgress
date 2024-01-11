from flask_wtf import FlaskForm
from wtforms import (StringField, TextAreaField, IntegerField, BooleanField,RadioField, FileField)
from wtforms.validators import InputRequired, Length, ValidationError


# Fungsi validasi untuk memeriksa apakah file adalah gambar
def validate_image(form, field):
    if field.data:
        file = field.data
        if file.filename == '':
            raise ValidationError('Pilih file gambar!')
        if not allowed_file(file.filename):
            raise ValidationError('Hanya file gambar yang diizinkan!')

# Fungsi untuk memeriksa ekstensi file yang diizinkan
def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


class imageForm(FlaskForm):
    file = FileField("file", validators=[InputRequired(), validate_image ])
