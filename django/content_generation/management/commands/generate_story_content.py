# ===============================
# content_generation/management/commands/generate_story_content.py
# ===============================
from django.core.management.base import BaseCommand
from quests.models import Quest
from training_data.models import TrainingUnit
from content_generation.models import GeneratedContent

class Command(BaseCommand):
    help = 'Generate story content and descriptions using LLM'
    
    def add_arguments(self, parser):
        parser.add_argument('--type', choices=['quest', 'training'], required=True)
        parser.add_argument('--id', type=int, help='Specific item ID')
        parser.add_argument('--enhance', action='store_true', help='Enhance existing content')
    
    def handle(self, *args, **options):
        if options['type'] == 'quest':
            self.generate_quest_stories(options)
        elif options['type'] == 'training':
            self.generate_training_content(options)
    
    def generate_quest_stories(self, options):
        if options['id']:
            quests = Quest.objects.filter(id=options['id'])
        else:
            quests = Quest.objects.filter(is_active=True)[:5]  # Batch of 5
        
        for quest in quests:
            self.stdout.write(f"Generating story for quest: {quest.title}")
            
            prompt = self.create_story_prompt(quest)
            
            # Generate enhanced story content
            generated_content = GeneratedContent.objects.create(
                content_type='story_text',
                prompt=prompt,
                related_object_id=quest.id,
                related_object_type='quest'
            )
            
            # TODO: Integrate with your LLM API
            # enhanced_story = self.call_llm_api(prompt)
            # generated_content.generated_text = enhanced_story
            # generated_content.save()
            
            self.stdout.write(f"Story prompt created: {prompt[:100]}...")
    
    def create_story_prompt(self, quest):
        return (
            f"Create an engaging, immersive story description for a training quest titled '{quest.title}'. "
            f"Current description: {quest.description} "
            f"Make it sound like a Studio Ghibli adventure with educational elements. "
            f"Keep it under 200 words, suitable for adult learners."
        )
    
    def generate_training_content(self, options):
        """Generate enhanced training content descriptions"""
        if options['id']:
            units = TrainingUnit.objects.filter(id=options['id'])
        else:
            units = TrainingUnit.objects.all()[:5]
        
        for unit in units:
            self.stdout.write(f"Enhancing training unit: {unit.name}")
            # Similar logic for training content enhancement