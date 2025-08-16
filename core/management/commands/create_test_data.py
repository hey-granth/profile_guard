from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from profiles.models import Profile, PromptQuestion
from core.constants import GENDER_CHOICES
import random

User = get_user_model()


class Command(BaseCommand):
    help = 'Create test data for the dating app'

    def handle(self, *args, **options):
        self.stdout.write('Creating test data...')
        
        # Create prompt questions
        questions = [
            "What's your ideal first date?",
            "What are you passionate about?",
            "What's your favorite way to spend a weekend?",
            "What's something you're proud of?",
            "What makes you laugh?",
        ]
        
        for i, question in enumerate(questions, 1):
            PromptQuestion.objects.get_or_create(
                question=question,
                defaults={'order': i}
            )
        
        # Create test users
        test_users = [
            {'email': 'alice@test.com', 'username': 'alice', 'gender': 'F'},
            {'email': 'bob@test.com', 'username': 'bob', 'gender': 'M'},
            {'email': 'charlie@test.com', 'username': 'charlie', 'gender': 'M'},
            {'email': 'diana@test.com', 'username': 'diana', 'gender': 'F'},
            {'email': 'eve@test.com', 'username': 'eve', 'gender': 'F'},
        ]
        
        for user_data in test_users:
            user, created = User.objects.get_or_create(
                email=user_data['email'],
                defaults={
                    'username': user_data['username'],
                    'gender': user_data['gender'],
                    'is_verified': True,
                }
            )
            if created:
                user.set_password('testpass123')
                user.save()
                
                # Create profile
                Profile.objects.get_or_create(
                    user=user,
                    defaults={
                        'bio': f'Hi, I\'m {user.username}! Looking forward to meeting new people.',
                        'location': random.choice(['New York', 'Los Angeles', 'Chicago', 'Houston']),
                        'occupation': random.choice(['Engineer', 'Designer', 'Teacher', 'Doctor']),
                        'interests': 'Travel, Music, Food, Movies',
                        'looking_for': 'Something serious',
                        'is_active': True,
                    }
                )
                
                self.stdout.write(f'Created user: {user.email}')
        
        self.stdout.write(self.style.SUCCESS('Test data created successfully!'))
        self.stdout.write('You can now login with:')
        self.stdout.write('- admin@test.com / 123 (superuser)')
        self.stdout.write('- alice@test.com / testpass123')
        self.stdout.write('- bob@test.com / testpass123')
        self.stdout.write('- etc.')