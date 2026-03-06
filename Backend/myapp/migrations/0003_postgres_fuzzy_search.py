# Backend/myapp/migrations/0003_postgres_fuzzy_search.py

from django.contrib.postgres.operations import TrigramExtension, UnaccentExtension
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0002_vehicle_is_featured_and_more'),  # ← your exact last migration
    ]

    operations = [
        # 1. Enable PostgreSQL extensions (only runs once, safe to re-run)
        TrigramExtension(),
        UnaccentExtension(),

        # 2. GIN trigram indexes for fuzzy brand/model search
        migrations.RunSQL(
            sql="""
                CREATE INDEX IF NOT EXISTS vehicle_brand_trgm_idx
                    ON myapp_vehicle USING GIN (brand gin_trgm_ops);

                CREATE INDEX IF NOT EXISTS vehicle_model_trgm_idx
                    ON myapp_vehicle USING GIN (model gin_trgm_ops);

                CREATE INDEX IF NOT EXISTS vehicle_fts_idx
                    ON myapp_vehicle USING GIN (
                        to_tsvector('english',
                            brand || ' ' || model || ' ' || COALESCE(description, ''))
                    );
            """,
            reverse_sql="""
                DROP INDEX IF EXISTS vehicle_brand_trgm_idx;
                DROP INDEX IF EXISTS vehicle_model_trgm_idx;
                DROP INDEX IF EXISTS vehicle_fts_idx;
            """,
        ),

        # 3. Composite indexes for common filter combos (B-tree, instant)
        migrations.RunSQL(
            sql="""
                CREATE INDEX IF NOT EXISTS status_featured_idx
                    ON myapp_vehicle (status, is_featured);

                CREATE INDEX IF NOT EXISTS status_fuel_idx
                    ON myapp_vehicle (status, fuel);

                CREATE INDEX IF NOT EXISTS status_transmission_idx
                    ON myapp_vehicle (status, transmission);
            """,
            reverse_sql="""
                DROP INDEX IF EXISTS status_featured_idx;
                DROP INDEX IF EXISTS status_fuel_idx;
                DROP INDEX IF EXISTS status_transmission_idx;
            """,
        ),
    ]