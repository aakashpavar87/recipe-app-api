# Generated by Django 5.0.6 on 2024-07-01 10:31

import core.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0010_user_otp_creation_time'),
    ]

    operations = [
        migrations.AlterField(
            model_name='recipe',
            name='image',
            field=models.ImageField(default='uploads/recipe/rice.png', upload_to=core.models.recipe_image_file_path),
        ),
    ]
