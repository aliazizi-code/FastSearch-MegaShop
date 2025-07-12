import csv
import random
import tempfile
import os
import multiprocessing
from django.core.management.base import BaseCommand
from faker import Faker
from django.db import connection


fixed_time = '2025-07-09 12:00:00'

def generate_csv(start_idx, count, file_path):
    fake = Faker('fa_IR')
    with open(file_path, 'w', newline='') as f:
        writer = csv.writer(f)
        for _ in range(count):
            title = " ".join(fake.words(nb=random.randint(1, 2))).title()
            description = " ".join(fake.sentences(nb=3)).replace('\n', ' ')
            tag = fake.word()
            writer.writerow([title, description, tag, 't', 'f', fixed_time, fixed_time])


def import_csv_to_db(file_path):
    with open(file_path, 'r') as f:
        with connection.cursor() as cursor:
            cursor.copy_expert(
                """
                COPY products_product
                    (title, description, cached_tags, is_published, is_deleted, created_at, updated_at)
                FROM STDIN WITH (FORMAT CSV)
                """,
                f
            )
    os.remove(file_path)


class Command(BaseCommand):
    help = '⚡️ Fast parallel COPY: generate large number of Persian products using all CPU cores'

    def add_arguments(self, parser):
        parser.add_argument('count', type=int, help='Total number of products to generate (e.g. 4000000)')

    def handle(self, *args, **options):
        total = options['count']
        cpu_count = multiprocessing.cpu_count()
        chunk_size = total // cpu_count
        self.stdout.write(f"⚙️ Detected {cpu_count} CPU cores. Generating {total:,} products in {cpu_count} parallel chunks...")

        tmp_files = [tempfile.NamedTemporaryFile(delete=False, suffix=f'_chunk_{i}.csv') for i in range(cpu_count)]
        paths = [f.name for f in tmp_files]
        for f in tmp_files:
            f.close()

        with multiprocessing.Pool(cpu_count) as pool:
            pool.starmap(generate_csv, [(i, chunk_size, path) for i, path in enumerate(paths)])

        self.stdout.write("✅ CSV generation completed. Now importing into database...")

        for path in paths:
            import_csv_to_db(path)

        self.stdout.write(self.style.SUCCESS(
            f"🎉 Successfully inserted {total:,} Persian products using parallel COPY across {cpu_count} cores!"
        ))
