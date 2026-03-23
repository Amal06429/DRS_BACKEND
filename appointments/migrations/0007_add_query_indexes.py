# Generated migration for performance optimization

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('appointments', '0004_alter_appointment_status'),
    ]

    operations = [
        migrations.AddIndex(
            model_name='appointment',
            index=models.Index(fields=['-created_at'], name='apt_created_idx'),
        ),
        migrations.AddIndex(
            model_name='appointment',
            index=models.Index(fields=['doctor_code', 'appointment_date'], name='apt_doc_date_idx'),
        ),
        migrations.AddIndex(
            model_name='appointment',
            index=models.Index(fields=['status'], name='apt_status_idx'),
        ),
    ]
