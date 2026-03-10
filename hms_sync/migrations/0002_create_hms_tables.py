# Generated manually to create HMS tables in PostgreSQL

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('hms_sync', '0001_initial'),
    ]

    operations = [
        migrations.RunSQL(
            sql="""
            CREATE TABLE IF NOT EXISTS hms_hospital_info (
                id SERIAL PRIMARY KEY,
                firm_name VARCHAR(200),
                address1 VARCHAR(200),
                synced_at TEXT
            );
            
            CREATE TABLE IF NOT EXISTS hms_department (
                code VARCHAR(10) PRIMARY KEY,
                name VARCHAR(200),
                synced_at TEXT
            );
            
            CREATE TABLE IF NOT EXISTS hms_doctors (
                code VARCHAR(10) PRIMARY KEY,
                name VARCHAR(100),
                rate DOUBLE PRECISION,
                department VARCHAR(10),
                avgcontime INTEGER,
                qualification VARCHAR(100),
                synced_at TEXT
            );
            
            CREATE TABLE IF NOT EXISTS hms_doctorstiming (
                slno BIGSERIAL PRIMARY KEY,
                code VARCHAR(10),
                t1 DOUBLE PRECISION,
                t2 DOUBLE PRECISION,
                synced_at TEXT
            );
            """,
            reverse_sql="""
            DROP TABLE IF EXISTS hms_hospital_info;
            DROP TABLE IF EXISTS hms_department;
            DROP TABLE IF EXISTS hms_doctors;
            DROP TABLE IF EXISTS hms_doctorstiming;
            """
        ),
    ]
