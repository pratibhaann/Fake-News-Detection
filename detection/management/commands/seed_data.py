from django.core.management.base import BaseCommand
from detection.models import User, NewsArticle, Feedback

class Command(BaseCommand):
    help = 'Seeds initial users, articles, and feedback for testing'

    def handle(self, *args, **kwargs):
        self.stdout.write('Seeding database...')

        # 1. Create Users
        # Admin User
        admin_user, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@fakenewsdetection.com',
                'role': 'admin',
                'is_staff': True,
                'is_superuser': True
            }
        )
        if created:
            admin_user.set_password('admin123')
            admin_user.save()
            self.stdout.write(self.style.SUCCESS('Created admin account (username: admin, password: admin123)'))
        else:
            self.stdout.write('Admin account already exists.')

        # Editor User
        editor_user, created = User.objects.get_or_create(
            username='editor',
            defaults={
                'email': 'editor@fakenewsdetection.com',
                'role': 'editor'
            }
        )
        if created:
            editor_user.set_password('editor123')
            editor_user.save()
            self.stdout.write(self.style.SUCCESS('Created editor account (username: editor, password: editor123)'))
        else:
            self.stdout.write('Editor account already exists.')

        # Another Editor User (for demonstration)
        editor2, created = User.objects.get_or_create(
            username='editor2',
            defaults={
                'email': 'editor2@fakenewsdetection.com',
                'role': 'editor'
            }
        )
        if created:
            editor2.set_password('editor123')
            editor2.save()
            self.stdout.write(self.style.SUCCESS('Created editor2 account (username: editor2, password: editor123)'))

        # Regular User
        reg_user, created = User.objects.get_or_create(
            username='user',
            defaults={
                'email': 'user@fakenewsdetection.com',
                'role': 'user'
            }
        )
        if created:
            reg_user.set_password('user123')
            reg_user.save()
            self.stdout.write(self.style.SUCCESS('Created regular user account (username: user, password: user123)'))
        else:
            self.stdout.write('Regular user account already exists.')

        # 2. Create News Articles
        NewsArticle.objects.get_or_create(
            title='Scientists Discover Water on Distant Mars-like Exoplanet',
            defaults={
                'content': 'Astronomers using the James Webb Space Telescope have identified clear signatures of water vapor in the atmosphere of a rocky exoplanet orbiting a nearby star, suggesting potential habitability conditions.',
                'author': editor_user,
                'status': 'verified',
                'classification': 'REAL'
            }
        )

        NewsArticle.objects.get_or_create(
            title='BREAKING: Secret Alien Landing Confirmed at Area 51, Hidden from Public for Decades',
            defaults={
                'content': 'According to unverified leaked documents from a supposed military insider, several extraterrestrial space vessels landed in Nevada last Tuesday, and aliens have signed a secret treaty with world governments.',
                'author': editor_user,
                'status': 'verified',
                'classification': 'FAKE'
            }
        )

        NewsArticle.objects.get_or_create(
            title='Global Markets Rise Following Promising Economic Policy Announcements',
            defaults={
                'content': 'Key global stock indexes saw significant gains today as central banks coordinated to announce new policies aimed at reducing inflation while supporting employment growth in key industrial sectors.',
                'author': editor2,
                'status': 'verified',
                'classification': 'REAL'
            }
        )

        NewsArticle.objects.get_or_create(
            title='New Miracle Juice Cures All Types of Illnesses in Just 24 Hours',
            defaults={
                'content': 'A secret remedy made from exotic rainforest berries is being sold online, claiming to cure diabetes, heart diseases, and even cancer within one day of consumption. Health officials warning consumers to stay away.',
                'author': editor_user,
                'status': 'pending',
                'classification': 'PENDING'
            }
        )

        NewsArticle.objects.get_or_create(
            title='Local Community Center to Host Annual Art and Craft Fair This Weekend',
            defaults={
                'content': 'The Oakridge Community Center is hosting its 15th annual craft fair, showcasing local woodwork, paintings, and handmade jewelry. Entry is free and all proceeds go to local charity initiatives.',
                'author': editor_user,
                'status': 'draft',
                'classification': 'PENDING'
            }
        )

        self.stdout.write(self.style.SUCCESS('Seeded sample news articles.'))

        # 3. Create Feedback
        Feedback.objects.get_or_create(
            user=reg_user,
            subject='Great Fake News Detector!',
            defaults={
                'message': 'The machine learning detection is incredibly fast! I verified an article about alien landing and it correctly predicted it as FAKE. Love this application.'
            }
        )

        Feedback.objects.get_or_create(
            user=reg_user,
            subject='Feature Request: Dark Mode',
            defaults={
                'message': 'Can you add a custom theme color selector or dark mode style to the dashboard? It would look amazing!'
            }
        )

        self.stdout.write(self.style.SUCCESS('Seeded sample feedbacks.'))
        self.stdout.write(self.style.SUCCESS('Database seeding completed.'))
