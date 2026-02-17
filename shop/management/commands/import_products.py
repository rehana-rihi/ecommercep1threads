import requests
from django.core.management.base import BaseCommand
from shop.models import Product

class Command(BaseCommand):
    help = 'Import products from FakeStoreAPI'
    
    def handle(self, *args, **options):
        # Delete existing products
        Product.objects.all().delete()
        self.stdout.write('Old products deleted...')
        
        # Fetch from API
        self.stdout.write('Fetching from FakeStoreAPI...')
        response = requests.get('https://fakestoreapi.com/products')
        products = response.json()
        
        # Create products
        count = 0
        for item in products:
            Product.objects.create(
                title=item['title'],
                price=item['price'],
                description=item['description'],
                category=item['category'],
                image=item['image']
            )
            count += 1
            self.stdout.write(f'Imported: {item["title"][:30]}...')
        
        self.stdout.write(self.style.SUCCESS(f'Successfully imported {count} products'))