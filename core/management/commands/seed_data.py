from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from core.models.Category import Category
from core.models.Worker import Worker
from core.models.Review import Review

User = get_user_model()

# Jaffna center
JAFFNA_LAT = 9.6615
JAFFNA_LNG = 80.0255


def create_categories():
    categories_data = [
        {"name": "Driver", "slug": "driver", "description": "Professional drivers", "icon": "🚗"},
        {"name": "Plumber", "slug": "plumber", "description": "Plumbing services", "icon": "🔧"},
        {"name": "Electrician", "slug": "electrician", "description": "Electrical work", "icon": "⚡"},
        {"name": "Agent", "slug": "agent", "description": "Real estate and agents", "icon": "🤝"},
        {"name": "Gold Worker", "slug": "gold-worker", "description": "Goldsmith and jewelry", "icon": "💍"},
        {"name": "AC Repair", "slug": "ac-repair", "description": "AC repair and maintenance", "icon": "❄️"},
        {"name": "Tuition Teacher", "slug": "tuition-teacher", "description": "Tutoring and tuition", "icon": "📚"},
    ]
    created = []
    for d in categories_data:
        cat, _ = Category.objects.get_or_create(slug=d["slug"], defaults=d)
        created.append(cat)
    return created


def create_users_and_workers(categories):
    users_workers = [
        ("rajan_kumar", "Rajan", "Kumar", "rajan@example.com", "+94771234567", "plumber", 8, True, 0.2, 0.1,
         "Expert plumber with 8 years of experience in residential and commercial plumbing."),
        ("selvam_arjun", "Selvam", "Arjun", "selvam@example.com", "+94772345678", "electrician", 5, True, -0.1, 0.15,
         "Licensed electrician specializing in home wiring and electrical repairs."),
        ("muthu_krishnan", "Muthu", "Krishnan", "muthu@example.com", "+94773456789", "driver", 12, True, 0.05, -0.1,
         "Professional driver available for daily hire, airport transfers, and outstation trips."),
        ("priya_nanthini", "Priya", "Nanthini", "priya@example.com", "+94774567890", "tuition-teacher", 7, True, 0.3, 0.2,
         "Experienced teacher for O/L and A/L Mathematics and Science subjects."),
        ("kannan_sivam", "Kannan", "Sivam", "kannan@example.com", "+94775678901", "ac-repair", 4, False, 0.4, -0.2,
         "Certified AC technician for all brands. Installation, repair, and maintenance."),
        ("thilaga_devi", "Thilaga", "Devi", "thilaga@example.com", "+94776789012", "gold-worker", 15, True, -0.15, 0.25,
         "Skilled goldsmith with expertise in traditional and modern jewelry design."),
        ("suresh_babu", "Suresh", "Babu", "suresh@example.com", "+94777890123", "agent", 6, True, 0.5, 0.3,
         "Real estate and property agent."),
        ("nirmala_raj", "Nirmala", "Raj", "nirmala@example.com", "+94778901234", "tuition-teacher", 10, True, -0.2, -0.15,
         "English and Tamil language tutor."),
        ("vijay_kumar", "Vijay", "Kumar", "vijay@example.com", "+94779012345", "plumber", 3, False, 0.6, 0.4,
         "Affordable plumbing services."),
    ]
    workers = []
    for (username, first, last, email, phone, slug, exp_years, verified, dlat, dlng, desc) in users_workers:
        user, _ = User.objects.get_or_create(
            username=username,
            defaults={
                "email": email,
                "first_name": first,
                "last_name": last,
                "phone": phone,
                "role": "worker",
            },
        )
        if not user.password or user.password == "":
            user.set_password("seedpass123")
            user.save()
        cat = next((c for c in categories if c.slug == slug), categories[0])
        worker, _ = Worker.objects.get_or_create(
            user=user,
            defaults={
                "category": cat,
                "description": desc,
                "experience_years": exp_years,
                "latitude": JAFFNA_LAT + dlat * 0.02,
                "longitude": JAFFNA_LNG + dlng * 0.02,
                "is_verified": verified,
            },
        )
        workers.append((user, worker))
    return workers


def create_reviews(workers):
    customer, _ = User.objects.get_or_create(
        username="customer1",
        defaults={"email": "customer@example.com", "first_name": "Anitha", "last_name": "Selvam", "role": "customer"},
    )
    if not customer.password:
        customer.set_password("seedpass123")
        customer.save()
    for (author_user, worker) in workers[:4]:
        Review.objects.get_or_create(
            worker=worker,
            author=customer,
            defaults={"rating": 5, "comment": "Excellent work! Highly recommended."},
        )
    u2, _ = User.objects.get_or_create(
        username="customer2",
        defaults={"email": "kumar@example.com", "first_name": "Kumar", "last_name": "Raj", "role": "customer"},
    )
    if not u2.password:
        u2.set_password("seedpass123")
        u2.save()
    for (author_user, worker) in workers[2:5]:
        Review.objects.get_or_create(
            worker=worker,
            author=u2,
            defaults={"rating": 4, "comment": "Good service, arrived on time."},
        )


class Command(BaseCommand):
    help = "Seed categories, users, workers, and reviews for development."

    def handle(self, *args, **options):
        self.stdout.write("Seeding categories...")
        categories = create_categories()
        self.stdout.write(f"  Created {len(categories)} categories.")
        self.stdout.write("Seeding users and workers...")
        workers = create_users_and_workers(categories)
        self.stdout.write(f"  Created {len(workers)} workers.")
        self.stdout.write("Seeding reviews...")
        create_reviews(workers)
        self.stdout.write(self.style.SUCCESS("Seed completed."))
