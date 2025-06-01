# ===============================
# content_generation/management/commands/generate_quest_graphics.py
# ===============================
from django.core.management.base import BaseCommand
from django.conf import settings
import requests
from quests.models import Quest
from content_generation.models import GeneratedContent

class Command(BaseCommand):
    help = 'Generate graphics for quests using AI'
    
    def add_arguments(self, parser):
        parser.add_argument('--quest-id', type=int, help='Specific quest ID to generate for')
        parser.add_argument('--all', action='store_true', help='Generate for all quests without images')
        parser.add_argument('--batch-size', type=int, default=5, help='Number of quests to process')
    
    def handle(self, *args, **options):
        if options['quest_id']:
            quests = Quest.objects.filter(id=options['quest_id'])
        elif options['all']:
            quests = Quest.objects.filter(background_image__isnull=True, is_active=True)
        else:
            quests = Quest.objects.filter(
                background_image__isnull=True, 
                is_active=True
            )[:options['batch_size']]
        
        for quest in quests:
            self.stdout.write(f"Generating graphics for quest: {quest.title}")
            
            # Create the prompt for Stable Diffusion
            prompt = self.create_ghibli_prompt(quest)
            
            # Generate the image
            success = self.generate_quest_image(quest, prompt)
            
            if success:
                self.stdout.write(
                    self.style.SUCCESS(f"Successfully generated image for {quest.title}")
                )
            else:
                self.stdout.write(
                    self.style.ERROR(f"Failed to generate image for {quest.title}")
                )
    
    def create_ghibli_prompt(self, quest):
        """Create a Studio Ghibli-style prompt for the quest"""
        base_prompt = (
            f"Studio Ghibli style, anime, beautiful landscape, "
            f"{quest.story_prompt}, "
            f"soft lighting, magical atmosphere, detailed background, "
            f"high quality, masterpiece, no characters"
        )
        
        # Add difficulty-based styling
        difficulty_styles = {
            1: "peaceful, gentle colors, sunny day",
            2: "mysterious, twilight, soft shadows", 
            3: "dramatic, stormy sky, intense colors",
            4: "epic, magical energy, glowing effects"
        }
        
        style_addition = difficulty_styles.get(quest.difficulty, "")
        return f"{base_prompt}, {style_addition}"
    
    def generate_quest_image(self, quest, prompt):
        """Generate image using your AI service"""
        try:
            # Store the generation attempt
            generated_content = GeneratedContent.objects.create(
                content_type='quest_background',
                prompt=prompt,
                related_object_id=quest.id,
                related_object_type='quest',
                generation_parameters={
                    'style': 'ghibli',
                    'difficulty': quest.difficulty,
                    'width': 1024,
                    'height': 768
                }
            )
            
            # Here you would integrate with your actual AI service
            # For now, this is a placeholder
            self.stdout.write(f"Would generate with prompt: {prompt}")
            
            # TODO: Replace with actual API call
            # response = requests.post(settings.CONTENT_GENERATION['STABLE_DIFFUSION_API_URL'], 
            #                         json={'prompt': prompt, 'width': 1024, 'height': 768})
            # 
            # if response.status_code == 200:
            #     # Save the generated image to quest.background_image
            #     # Update generated_content with the result
            #     pass
            
            return True
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error generating image: {str(e)}"))
            return False