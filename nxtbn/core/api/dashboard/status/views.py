from django.conf import settings
from rest_framework import serializers
import platform
import django
import sys
import psutil
from django.db import connection
from datetime import datetime, timedelta
from rest_framework.generics import RetrieveAPIView
from rest_framework.views import APIView
from rest_framework.response import Response


def bytes_to_human_readable(size_in_bytes):
    """Convert bytes to a human-readable format."""
    if not isinstance(size_in_bytes, (int, float)):
        return size_in_bytes  # If it's already in human-readable format, return as-is

    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_in_bytes < 1024.0:
            return f"{size_in_bytes:.2f} {unit}"
        size_in_bytes /= 1024.0


def human_readable_uptime(boot_time):
    """Convert system boot time to human-readable uptime."""
    now = datetime.now()
    uptime = now - datetime.fromtimestamp(boot_time)
    days = uptime.days
    hours, remainder = divmod(uptime.seconds, 3600)
    minutes, _ = divmod(remainder, 60)
    return f"{days} days, {hours} hours, {minutes} minutes"


def get_table_info():
    table_info = []
    total_db_size = 0

    db_engine = connection.settings_dict['ENGINE']

    with connection.cursor() as cursor:
        if 'postgresql' in db_engine:
            cursor.execute("""
                SELECT
                    table_name,
                    pg_total_relation_size(table_name::regclass) AS total_size,
                    pg_relation_size(table_name::regclass) AS table_size,
                    pg_indexes_size(table_name::regclass) AS indexes_size
                FROM
                    information_schema.tables
                WHERE
                    table_schema = 'public'
                    AND table_type = 'BASE TABLE';
            """)
            for row in cursor.fetchall():
                table_info.append({
                    "table_name": row[0],
                    "total_size": bytes_to_human_readable(row[1]),
                    "table_size": bytes_to_human_readable(row[2]),
                    "indexes_size": bytes_to_human_readable(row[3]),
                })
            cursor.execute("SELECT pg_database_size(current_database());")
            total_db_size = cursor.fetchone()[0]
        
        elif 'sqlite' in db_engine:
            import os
            db_file_path = connection.settings_dict['NAME']
            db_file_size = os.path.getsize(db_file_path)
            table_info.append({
                "table_name": "SQLite Database",
                "total_size": bytes_to_human_readable(db_file_size),
                "table_size": bytes_to_human_readable(db_file_size),
                "indexes_size": "N/A",
            })
            total_db_size = db_file_size

    return {
        "tables": table_info,
        "total_db_size": bytes_to_human_readable(total_db_size),
    }


def get_caching_info():
    cache_info = []
    for cache_name, cache_config in settings.CACHES.items():
        cache_info.append({
            "cache_name": cache_name,
            "cache_backend": cache_config['BACKEND'],
            "cache_host": cache_config['LOCATION'],
        })
    return cache_info



def get_system_status():
    db_info = get_table_info()
    cache_info = get_caching_info()

    os_info = {
        "os": platform.system(),
        "os_version": platform.version(),
        "architecture": platform.architecture(),
        "hostname": platform.node(),
    }

    tech_info = {
        "python_version": sys.version,
        "database_engine": connection.settings_dict['ENGINE'],
        "nxtbn_version": settings.VERSION,
    }

    nxtbn_settings = {
        "base_currency": settings.BASE_CURRENCY,
        'site_id': settings.SITE_ID,
        'language_code': settings.LANGUAGE_CODE,
        'time_zone': settings.TIME_ZONE,
        'use_i18n': settings.USE_I18N,
        'use_l10n': settings.USE_L10N,
        'use_tz': settings.USE_TZ,
        'allowed_currencies': settings.ALLOWED_CURRENCIES,
        'is_multi_currency': settings.IS_MULTI_CURRENCY,
        'store_url': settings.STORE_URL,
        'email_host': settings.EMAIL_HOST,
        'email_host_user': settings.EMAIL_HOST_USER,
        'email_port': settings.EMAIL_PORT,
        'email_use_tls': settings.EMAIL_USE_TLS,
        'default_from_email': settings.DEFAULT_FROM_EMAIL,
        "default_storage": settings.DEFAULT_FILE_STORAGE,
        'static_url': settings.STATIC_URL,
        'static_root': settings.STATIC_ROOT,
        'staticfiles_dirs': settings.STATICFILES_DIRS,
        'media_url': settings.MEDIA_URL,
        'media_root': settings.MEDIA_ROOT,
    }

    server_status = {
        "uptime":  human_readable_uptime(psutil.boot_time()),
        "cpu_usage": psutil.cpu_percent(interval=1),
        "memory": {
            "total": bytes_to_human_readable(psutil.virtual_memory().total),
            "used": bytes_to_human_readable(psutil.virtual_memory().used),
            "available": bytes_to_human_readable(psutil.virtual_memory().available),
            "percent": psutil.virtual_memory().percent,
        },
        "disk_usage": {key: bytes_to_human_readable(value) for key, value in psutil.disk_usage('/')._asdict().items()},
    }

    return {
        "database_info": db_info,
        "cache_info": cache_info,
        "os_info": os_info,
        "technology_info": tech_info,
        "server_status": server_status,
        "nxtbn_settings": nxtbn_settings,
    }


class SystemStatusAPIView(APIView):
   
    def get(self, request, *args, **kwargs):
        return Response(get_system_status())

def get_dtails_db_table_info():
    table_info = []
    total_db_size = 0
    db_engine = connection.settings_dict['ENGINE']
    
    with connection.cursor() as cursor:
        if 'postgresql' in db_engine:
            try:
                # Query for PostgreSQL to fetch table info
                cursor.execute("""
                    SELECT
                        table_name,
                        pg_total_relation_size(table_name::regclass) AS total_size,
                        pg_relation_size(table_name::regclass) AS table_size,
                        pg_indexes_size(table_name::regclass) AS indexes_size
                    FROM
                        information_schema.tables
                    WHERE
                        table_schema = 'public'
                        AND table_type = 'BASE TABLE';
                """)
                rows = cursor.fetchall()

                # Loop over the PostgreSQL table rows
                for row in rows:
                    table_info.append({
                        "table_name": row[0],
                        "total_size": bytes_to_human_readable(row[1]),
                        "table_size": bytes_to_human_readable(row[2]),
                        "indexes_size": bytes_to_human_readable(row[3]),
                    })

                # Get total database size for PostgreSQL
                cursor.execute("SELECT pg_database_size(current_database());")
                total_db_size = cursor.fetchone()[0]

            except Exception as e:
                print(f"Error fetching PostgreSQL table sizes: {e}")
                table_info.append({
                    "table_name": "Error",
                    "total_size": "N/A",
                    "table_size": "N/A",
                    "indexes_size": "N/A",
                })

        elif 'sqlite' in db_engine:
            try:
                # Query for SQLite to fetch table info
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
                tables = cursor.fetchall()

                # Loop over the SQLite table rows
                for table in tables:
                    table_name = table[0]
                    # Fetch table size for SQLite (SQLite doesn't have indexes size like PostgreSQL)
                    cursor.execute(f"PRAGMA table_info({table_name});")
                    table_info.append({
                        "table_name": table_name,
                        "total_size": "N/A",  # SQLite doesn't have direct table size query
                        "table_size": "N/A",  # Placeholder for now
                        "indexes_size": "N/A",  # SQLite doesn't separate index size
                    })
                
                # Get total database size for SQLite
                import os
                db_file_path = connection.settings_dict['NAME']
                db_file_size = os.path.getsize(db_file_path)
                total_db_size = db_file_size

            except Exception as e:
                print(f"Error fetching SQLite table sizes: {e}")
                table_info.append({
                    "table_name": "Error",
                    "total_size": "N/A",
                    "table_size": "N/A",
                    "indexes_size": "N/A",
                })

        else:
            table_info.append({
                "table_name": "Unknown DB Engine",
                "total_size": "N/A",
                "table_size": "N/A",
                "indexes_size": "N/A",
            })

    return {
        "tables": table_info,
        "total_db_size": bytes_to_human_readable(total_db_size),
    }

class DatabaseTableInfoAPIView(APIView):
    """
    API View that returns the detailed information of the database tables including
    their size, index size, and total size.
    """
    
    def get(self, request, *args, **kwargs):
        table_info = get_dtails_db_table_info()
        return Response(table_info)