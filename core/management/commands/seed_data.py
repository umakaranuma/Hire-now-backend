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
    # (username, first_name, last_name, email, phone, category_slug, exp_years, is_verified, dlat, dlng, description)
    users_workers = [
        # Plumbers
        ("rajan_kumar", "Rajan", "Kumar", "rajan@example.com", "+94771234567", "plumber", 8, True, 0.2, 0.1,
         "Expert plumber with 8+ years of experience in residential and commercial plumbing. Specializing in pipe repairs, bathroom installations, water heater services, and drain cleaning. Available for emergency call-outs in Jaffna and surrounding areas."),
        ("vijay_kumar", "Vijay", "Kumar", "vijay@example.com", "+94779012345", "plumber", 3, False, 0.6, 0.4,
         "Affordable plumbing services for homes and small businesses. Pipe fixing, tap repairs, and basic installations. Fair rates and same-day service when possible."),
        ("santhosh_plumber", "Santhosh", "Mohan", "santhosh.p@example.com", "+94780123456", "plumber", 6, True, -0.3, 0.35,
         "Licensed plumber. Bathroom and kitchen fittings, sewage line work, and water pump installation. I use quality materials and give a warranty on labour."),
        # Electricians
        ("selvam_arjun", "Selvam", "Arjun", "selvam@example.com", "+94772345678", "electrician", 5, True, -0.1, 0.15,
         "Licensed electrician specializing in home wiring, electrical repairs, and fuse board upgrades. Safe, certified work for residential and small commercial projects in Jaffna."),
        ("balan_kumar", "Balan", "Kumar", "balan@example.com", "+94781112233", "electrician", 11, True, 0.45, -0.25,
         "Over 10 years in electrical work. House wiring, generator connections, solar panel wiring, and fault finding. Available for urgent repairs."),
        ("kumar_electrician", "Kumar", "Somasundaram", "kumar.e@example.com", "+94782223344", "electrician", 4, False, -0.5, 0.1,
         "Domestic electrician for lighting, switches, and appliance wiring. Reasonable rates and quick response in Jaffna town area."),
        # Drivers
        ("muthu_krishnan", "Muthu", "Krishnan", "muthu@example.com", "+94773456789", "driver", 12, True, 0.05, -0.1,
         "Professional driver with 12+ years experience. Daily hire, airport transfers (Jaffna–Colombo), wedding and event trips, and outstation tours. Clean vehicle and punctual."),
        ("arun_driver", "Arun", "Jeyakumar", "arun.d@example.com", "+94783334455", "driver", 7, True, 0.15, 0.4,
         "Van and car driver for school runs, office drop-offs, and family trips. Knows Jaffna and Northern Province routes well. Safe driver."),
        ("kannan_driver", "Kannan", "Nadesan", "kannan.d@example.com", "+94784445566", "driver", 5, False, -0.2, -0.3,
         "Driver available for hire by the hour or day. Airport pickup/drop, hospital visits, and local errands. Contact for availability."),
        # Tuition Teachers
        ("priya_nanthini", "Priya", "Nanthini", "priya@example.com", "+94774567890", "tuition-teacher", 7, True, 0.3, 0.2,
         "Experienced teacher for O/L and A/L Mathematics and Science. Home visits or small group classes. Past papers practice and concept clearing. Based in Jaffna."),
        ("nirmala_raj", "Nirmala", "Raj", "nirmala@example.com", "+94778901234", "tuition-teacher", 10, True, -0.2, -0.15,
         "English and Tamil language tutor for O/L, A/L, and adult learners. Grammar, literature, and spoken English. Flexible timings and patient approach."),
        ("siva_teacher", "Siva", "Ramanan", "siva.t@example.com", "+94785556677", "tuition-teacher", 4, True, 0.5, -0.4,
         "Physics and Combined Mathematics tuition for A/L. Clear explanations and problem-solving focus. Group or one-to-one sessions in Jaffna."),
        # AC Repair
        ("kannan_sivam", "Kannan", "Sivam", "kannan@example.com", "+94775678901", "ac-repair", 4, False, 0.4, -0.2,
         "Certified AC technician for all brands. Installation, repair, gas refill, and regular maintenance. Split and window units. Service in Jaffna and suburbs."),
        ("raj_ac", "Raj", "Ganesan", "raj.ac@example.com", "+94786667788", "ac-repair", 9, True, -0.35, 0.2,
         "AC specialist with 9 years experience. Quick diagnosis, genuine parts when possible, and follow-up support. Commercial and residential."),
        # Gold Worker
        ("thilaga_devi", "Thilaga", "Devi", "thilaga@example.com", "+94776789012", "gold-worker", 15, True, -0.15, 0.25,
         "Skilled goldsmith with 15+ years in traditional and modern jewelry. Custom designs, repairs, resizing, and polishing. Trusted for weddings and special occasions in Jaffna."),
        ("murugan_gold", "Murugan", "Selliah", "murugan.g@example.com", "+94787778899", "gold-worker", 8, True, 0.25, -0.35,
         "Gold and silver jewelry making and repair. Antique restoration and new designs. Shop in Jaffna town; also home visits for consultations."),
        # Agent
        ("suresh_babu", "Suresh", "Babu", "suresh@example.com", "+94777890123", "agent", 6, True, 0.5, 0.3,
         "Real estate and property agent in Jaffna. Land, houses, and commercial property. Documentation support and fair dealing. Contact for buying, selling, or renting."),
        ("kavitha_agent", "Kavitha", "Arunachalam", "kavitha@example.com", "+94788889900", "agent", 4, False, -0.4, 0.45,
         "Property agent for residential listings. Help with viewing, negotiation, and paperwork. Focus on Jaffna and nearby areas."),
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
    def ensure_customer(username, email, first_name, last_name):
        user, _ = User.objects.get_or_create(
            username=username,
            defaults={"email": email, "first_name": first_name, "last_name": last_name, "role": "customer"},
        )
        if not user.password or user.password == "":
            user.set_password("seedpass123")
            user.save()
        return user

    customers = [
        ensure_customer("customer1", "customer@example.com", "Anitha", "Selvam"),
        ensure_customer("customer2", "kumar@example.com", "Kumar", "Raj"),
        ensure_customer("customer3", "meera@example.com", "Meera", "Devi"),
        ensure_customer("customer4", "siva.c@example.com", "Siva", "Chandran"),
        ensure_customer("customer5", "rani@example.com", "Rani", "Krishnan"),
    ]

    review_data = [
        (5, "Excellent work! Very professional and finished on time. Highly recommended."),
        (5, "Best service in Jaffna. Will definitely hire again. Thank you!"),
        (4, "Good job. Arrived on time and did what was agreed. Minor delay but overall satisfied."),
        (4, "Reliable and fair price. Would use again for future work."),
        (5, "Very skilled and polite. Fixed the issue quickly. Five stars."),
        (4, "Satisfied with the service. Clean work and reasonable rate."),
        (5, "Outstanding! Went the extra mile. My family was very happy."),
        (3, "Work was done but took longer than expected. Result is okay."),
        (5, "Prompt, professional, and quality work. No complaints at all."),
        (4, "Good experience. Would recommend to others in Jaffna."),
    ]

    import random
    random.seed(42)
    for (_, worker) in workers:
        n_reviews = random.randint(1, 4)
        chosen = random.sample(customers, min(n_reviews, len(customers)))
        for customer in chosen:
            rating, comment = random.choice(review_data)
            Review.objects.get_or_create(
                worker=worker,
                author=customer,
                defaults={"rating": rating, "comment": comment},
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
