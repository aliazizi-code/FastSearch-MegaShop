# your_app/management/commands/create_test_products.py

from django.core.management.base import BaseCommand
from faker import Faker
import random
from products.models import Product
from taggit.models import Tag

class Command(BaseCommand):
    help = 'Create N realistic Persian-language products with single-word tags'

    def add_arguments(self, parser):
        parser.add_argument(
            'count',
            type=int,
            help='Number of products to create (e.g. 1000000)'
        )

    def handle(self, *args, **options):
        total = options['count']
        batch_size = 200
        fake = Faker('fa_IR')  # Persian locale

        self.stdout.write(f"⚙️ Starting creation of {total:,} products in batches of {batch_size}...")

        created = 0
        buffer = []

        # 1) Bulk-create products
        for _ in range(total):
            # Title: 1-2 Persian words
            title_words = fake.words(nb=random.randint(1, 2), unique=True)
            title = " ".join(title_words).strip().title()

            # Description: 3 sentences
            description = fake.paragraph(nb_sentences=3)

            # Single-word tag
            tag_name = fake.word()

            # cached_tags for FTS
            cached_tags = tag_name

            buffer.append(
                Product(
                    title=title,
                    description=description,
                    cached_tags=cached_tags,
                    is_published=True,
                )
            )

            if len(buffer) >= batch_size:
                Product.objects.bulk_create(buffer)
                created += len(buffer)
                self.stdout.write(f"  ✅ {created:,} products created so far.")
                buffer = []

        # create any remaining
        if buffer:
            Product.objects.bulk_create(buffer)
            created += len(buffer)
            self.stdout.write(f"  ✅ {created:,} products created in total.")

        # 2) Ensure tags exist and assign them
        self.stdout.write("🏷 Ensuring tags exist and assigning to products…")
        # Collect distinct tag names from cached_tags of latest products
        latest = Product.objects.filter(is_published=True).order_by('-id')[:created]
        tag_names = set(prod.cached_tags for prod in latest)
        # Create missing Tag objects
        for name in tag_names:
            Tag.objects.get_or_create(name=name)

        # Assign tags
        for prod in latest:
            tag_obj = Tag.objects.get(name=prod.cached_tags)
            prod.tags.add(tag_obj)

        self.stdout.write(self.style.SUCCESS(
            f"🎉 Successfully created and tagged {created:,} products."
        ))