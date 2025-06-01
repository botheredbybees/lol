# ===============================
# content_generation/management/commands/cleanup_generated_content.py
# ===============================
from django.core.management.base import BaseCommand
from django.conf import settings
from content_generation.models import GeneratedContent
from datetime import datetime, timedelta

class Command(BaseCommand):
    help = 'Cleanup old or unused generated content'
    
    def add_arguments(self, parser):
        parser.add_argument('--days', type=int, default=30, help='Delete content older than X days')
        parser.add_argument('--unapproved', action='store_true', help='Delete unapproved content')
        parser.add_argument('--dry-run', action='store_true', help='Show what would be deleted')
    
    def handle(self, *args, **options):
        cutoff_date = datetime.now() - timedelta(days=options['days'])
        
        query = GeneratedContent.objects.filter(created__lt=cutoff_date)
        
        if options['unapproved']:
            query = query.filter(is_approved=False)
        
        count = query.count()
        
        if options['dry_run']:
            self.stdout.write(f"Would delete {count} generated content items")
            for item in query[:10]:  # Show first 10
                self.stdout.write(f"  - {item.content_type}: {item.created}")
        else:
            deleted, _ = query.delete()
            self.stdout.write(
                self.style.SUCCESS(f"Deleted {deleted} old generated content items")
            )