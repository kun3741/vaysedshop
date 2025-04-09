from django.db import migrations

class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0004_productimage'),
    ]

    operations = [
        migrations.DeleteModel(
            name='ProductImage',
        ),
    ]
