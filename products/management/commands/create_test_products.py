import io
import csv
from django.core.management.base import BaseCommand
from faker import Faker
import random
from django.db import connection


class Command(BaseCommand):
    help = '⚡️ Fast COPY: create N Persian products with fake data (only cached_tags, no taggit, fixed timestamp)'

    def add_arguments(self, parser):
        parser.add_argument(
            'count',
            type=int,
            help='Number of products to create (e.g. 1000000)'
        )

    def handle(self, *args, **options):
        total = options['count']
        fake = Faker('fa_IR')
        fixed_time = '2025-07-09 12:00:00'

        self.stdout.write(f"⚙️ Fast COPY: creating {total:,} products with cached_tags only…")

        buf = io.StringIO()
        writer = csv.writer(buf)
        for _ in range(total):
            title = " ".join(fake.words(nb=random.randint(1, 2), unique=True)).title()
            description = fake.paragraph(nb_sentences=3).replace('\n', ' ')
            tag = fake.word()
            
            writer.writerow([title, description, tag, 't', 'f', fixed_time, fixed_time])

        buf.seek(0)

        with connection.cursor() as cursor:
            cursor.copy_expert(
                """
                COPY products_product
                    (title, description, cached_tags, is_published, is_deleted, created_at, updated_at)
                FROM STDIN WITH (FORMAT CSV)
                """,
                buf
            )

        self.stdout.write(self.style.SUCCESS(
            f"🎉 Successfully inserted {total:,} products via COPY in one go!"
        ))
