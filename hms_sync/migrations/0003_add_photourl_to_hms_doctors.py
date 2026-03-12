# Migration to add photourl field to HMS doctors table

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('hms_sync', '0002_create_hms_tables'),
    ]

    operations = [
        migrations.RunSQL(
            sql="""
            ALTER TABLE hms_doctors ADD COLUMN IF NOT EXISTS photourl TEXT;
            """,
            reverse_sql="""
            ALTER TABLE hms_doctors DROP COLUMN IF EXISTS photourl;
            """
        ),
    ]
