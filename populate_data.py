#!/usr/bin/env python
"""
Sample data for the Django blog/portfolio application.
Run with: python manage.py shell < populate_data.py
"""

import os
import django

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from apps.portfolio.models import About, Skill, Project
from apps.blog.models import BlogPost
from django.utils import timezone
from datetime import timedelta

def create_sample_data():
    """Create sample data for the portfolio and blog"""
    
    # Clear existing data
    print("Clearing existing data...")
    BlogPost.objects.all().delete()
    Project.objects.all().delete()
    Skill.objects.all().delete()
    About.objects.all().delete()
    
    # Create About section
    print("Creating About section...")
    about = About.objects.create(
        title="About Me",
        content="""I'm a passionate software developer with experience in building web applications using modern technologies. 

I love creating clean, efficient code and solving complex problems. My journey in software development started several years ago, and I've been continuously learning and improving my skills.

When I'm not coding, you can find me reading tech blogs, contributing to open source projects, or exploring new technologies. I believe in the power of collaboration and sharing knowledge within the developer community.

I'm always excited to take on new challenges and work on projects that make a positive impact."""
    )
    
    # Create Skills
    print("Creating skills...")
    skills_data = [
        # Programming Languages
        ("Python", "Programming Languages", 90),
        ("JavaScript", "Programming Languages", 85),
        ("Java", "Programming Languages", 75),
        ("C++", "Programming Languages", 70),
        ("TypeScript", "Programming Languages", 80),
        
        # Web Technologies
        ("HTML/CSS", "Web Technologies", 95),
        ("React", "Web Technologies", 85),
        ("Django", "Web Technologies", 90),
        ("Node.js", "Web Technologies", 80),
        ("Vue.js", "Web Technologies", 75),
        
        # Databases & Tools
        ("PostgreSQL", "Databases", 85),
        ("MongoDB", "Databases", 80),
        ("Git", "Development Tools", 90),
        ("Docker", "Development Tools", 75),
        ("AWS", "Cloud Services", 70),
        
        # Other Skills
        ("Machine Learning", "AI/ML", 65),
        ("Data Analysis", "Data Science", 70),
        ("API Development", "Backend", 85),
        ("Responsive Design", "Frontend", 90),
        ("Problem Solving", "Soft Skills", 95),
    ]
    
    for name, category, level in skills_data:
        Skill.objects.create(
            name=name,
            category=category,
            proficiency_level=level
        )
    
    # Create Projects
    print("Creating projects...")
    projects_data = [
        {
            "title": "E-Commerce Platform",
            "description": "A full-stack e-commerce application built with Django and React. Features include user authentication, product management, shopping cart, and payment integration.",
            "technologies": "Django, React, PostgreSQL, Stripe API, Docker",
            "github_url": "https://github.com/username/ecommerce-platform",
            "live_url": "https://my-ecommerce-demo.com",
            "featured": True,
        },
        {
            "title": "Task Management App",
            "description": "A collaborative task management application with real-time updates. Users can create projects, assign tasks, and track progress with a beautiful, intuitive interface.",
            "technologies": "Vue.js, Node.js, Socket.io, MongoDB, Express",
            "github_url": "https://github.com/username/task-manager",
            "live_url": "https://task-manager-demo.com",
            "featured": False,
        },
        {
            "title": "Weather Dashboard",
            "description": "A responsive weather dashboard that displays current weather and forecasts for multiple locations. Integrates with weather APIs and provides beautiful visualizations.",
            "technologies": "JavaScript, Chart.js, OpenWeather API, CSS3",
            "github_url": "https://github.com/username/weather-dashboard",
            "live_url": "https://weather-dashboard-demo.com",
            "featured": True,
        },
        {
            "title": "Blog CMS",
            "description": "A custom content management system for blogging with markdown support, WYSIWYG editor, and SEO optimization. Perfect for technical bloggers.",
            "technologies": "Django, TinyMCE, Markdown, SQLite",
            "github_url": "https://github.com/username/blog-cms",
            "live_url": None,
            "featured": False,
        },
    ]
    
    for project_data in projects_data:
        Project.objects.create(**project_data)
    
    # Create Blog Posts
    print("Creating blog posts...")
    blog_posts_data = [
        {
            "title": "Getting Started with Django",
            "slug": "getting-started-with-django",
            "content": """# Getting Started with Django

Django is a high-level Python web framework that encourages rapid development and clean, pragmatic design. It takes care of much of the hassle of web development, so you can focus on writing your app without needing to reinvent the wheel.

## Why Choose Django?

1. **Rapid Development**: Django's "batteries included" approach provides everything you need to build web applications quickly.
2. **Security**: Django takes security seriously and helps developers avoid many common security mistakes.
3. **Scalability**: Django's architecture is designed to handle high-traffic applications.
4. **Community**: Django has a large, active community and extensive documentation.

## Installation

```bash
pip install django
django-admin startproject myproject
cd myproject
python manage.py runserver
```

## Key Concepts

- **Models**: Define the structure of your data
- **Views**: Handle HTTP requests and return responses
- **Templates**: Render HTML with dynamic content
- **URLs**: Map URLs to views using URL patterns

Django makes it easy to build robust web applications quickly and efficiently!""",
            "excerpt": "Learn the basics of Django web framework and start building your first web application with this comprehensive guide.",
            "published": True,
            "published_at": timezone.now() - timedelta(days=30),
        },
        {
            "title": "Building Responsive Websites with CSS Grid",
            "slug": "responsive-websites-css-grid",
            "content": """# Building Responsive Websites with CSS Grid

CSS Grid is a powerful layout system that allows you to create complex, responsive web layouts with ease. It has revolutionized how we approach web design.

## What is CSS Grid?

CSS Grid is a two-dimensional layout system that allows you to work with both rows and columns simultaneously. This makes it perfect for creating grid-based layouts that adapt to different screen sizes.

## Basic Grid Setup

```css
.grid-container {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  grid-template-rows: auto;
  gap: 20px;
}

.grid-item {
  background: #f0f0f0;
  padding: 20px;
  text-align: center;
}
```

## Responsive Design

The real power of CSS Grid shines when creating responsive designs:

```css
@media (max-width: 768px) {
  .grid-container {
    grid-template-columns: 1fr;
  }
}
```

## Best Practices

1. Use `fr` units for flexible sizing
2. Leverage `gap` for consistent spacing
3. Utilize `minmax()` for adaptive sizing
4. Think mobile-first when designing

CSS Grid makes building modern, responsive websites intuitive and efficient.""",
            "excerpt": "Master CSS Grid layout system and create beautiful, responsive websites that work perfectly on all devices.",
            "published": True,
            "published_at": timezone.now() - timedelta(days=15),
        },
        {
            "title": "Introduction to Machine Learning with Python",
            "slug": "introduction-machine-learning-python",
            "content": """# Introduction to Machine Learning with Python

Machine learning is transforming industries and creating new possibilities. Python, with its rich ecosystem of libraries, is the perfect language to get started with ML.

## Why Python for Machine Learning?

- **Simple Syntax**: Python's clean syntax makes it easy to learn and implement algorithms
- **Rich Ecosystem**: Libraries like scikit-learn, pandas, and numpy provide powerful tools
- **Community**: Large community means plenty of resources and support
- **Flexibility**: Can integrate with web frameworks, databases, and other tools

## Getting Started

```python
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score

# Load data
data = pd.read_csv('data.csv')

# Prepare features and target
X = data.drop('target', axis=1)
y = data['target']

# Split data
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

# Train model
model = RandomForestClassifier()
model.fit(X_train, y_train)

# Make predictions
predictions = model.predict(X_test)
accuracy = accuracy_score(y_test, predictions)

print(f"Model accuracy: {accuracy:.2f}")
```

## Common Algorithms

1. **Linear Regression**: Predicting continuous values
2. **Random Forest**: Ensemble method for classification and regression
3. **K-Means**: Unsupervised learning for clustering
4. **Neural Networks**: Deep learning for complex patterns

Start with these fundamentals and gradually explore more advanced techniques. The key is to practice with real datasets and build projects that solve actual problems.""",
            "excerpt": "Discover the basics of machine learning using Python and popular libraries like scikit-learn and pandas.",
            "published": True,
            "published_at": timezone.now() - timedelta(days=7),
        },
        {
            "title": "Version Control Best Practices with Git",
            "slug": "version-control-best-practices-git",
            "content": """# Version Control Best Practices with Git

Git is an essential tool for any developer. Following best practices ensures clean, maintainable code history and smooth collaboration.

## Commit Messages

Write clear, descriptive commit messages:

```bash
# Good
git commit -m "Add user authentication with JWT tokens"

# Bad
git commit -m "fixed stuff"
```

## Branching Strategy

Use a clear branching strategy:

- **main**: Production-ready code
- **develop**: Integration branch for features
- **feature/***: Individual feature branches
- **hotfix/***: Emergency fixes

## Useful Git Commands

```bash
# Interactive rebase for clean history
git rebase -i HEAD~3

# Stash changes temporarily
git stash save "work in progress"

# Find bugs with git bisect
git bisect start
git bisect bad
git bisect good <commit-hash>
```

## Best Practices

1. **Commit Often**: Make small, focused commits
2. **Pull Before Push**: Stay in sync with the team
3. **Use Branches**: Isolated development for features
4. **Review Code**: Pull requests improve code quality
5. **Document Changes**: Clear commit messages tell the story

Good version control habits make development smoother and collaboration more effective.""",
            "excerpt": "Learn essential Git practices that will improve your workflow and make collaboration more effective.",
            "published": True,
            "published_at": timezone.now() - timedelta(days=3),
        },
    ]
    
    for post_data in blog_posts_data:
        BlogPost.objects.create(**post_data)
    
    print("Sample data created successfully!")
    print(f"- About section: 1")
    print(f"- Skills: {Skill.objects.count()}")
    print(f"- Projects: {Project.objects.count()}")
    print(f"- Blog posts: {BlogPost.objects.count()}")

if __name__ == "__main__":
    create_sample_data()