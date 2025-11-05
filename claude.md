# Blog Penny - Contexto del Proyecto para Claude

Este documento proporciona contexto completo sobre el proyecto Blog Penny para asistentes de IA.

## Descripción General

Blog Penny es una aplicación web Django que combina un **portfolio personal** con un **blog técnico**. Está diseñado para desarrolladores que quieren mostrar su trabajo y compartir conocimiento a través de artículos con soporte Markdown completo.

## Stack Tecnológico

- **Framework**: Django 5.2.7
- **Python**: 3.13
- **Base de Datos**: SQLite3 (desarrollo)
- **Renderizado de Contenido**: Markdown 3.9 con extensiones 'extra' y 'codehilite'
- **Imágenes**: Pillow 12.0.0
- **Frontend**: HTML5, CSS3 puro, JavaScript Vanilla
- **Tipografía**: Google Fonts (Inter)

## Arquitectura del Proyecto

### Aplicaciones Django

El proyecto sigue una arquitectura modular con dos aplicaciones principales:

1. **`apps.portfolio`**: Gestiona el portfolio personal
2. **`apps.blog`**: Gestiona el sistema de blog

### Estructura de Directorios

```
blog-penny/
├── apps/
│   ├── blog/                      # Aplicación del blog
│   │   ├── models.py              # BlogPost model
│   │   ├── views.py               # PostListView, PostDetailView (CBV)
│   │   ├── urls.py                # URLs con namespace 'blog'
│   │   ├── admin.py               # Admin personalizado con editor Markdown
│   │   ├── admin_widgets.py       # MarkdownEditorWidget personalizado
│   │   ├── migrations/
│   │   └── static/admin/
│   │       ├── css/markdown_editor.css
│   │       └── js/markdown_editor.js
│   └── portfolio/                 # Aplicación del portfolio
│       ├── models.py              # About, Skill, Project models
│       ├── views.py               # HomeView, ProjectDetailView (CBV)
│       ├── urls.py                # URLs con namespace 'portfolio'
│       ├── admin.py               # Admin para About, Skill, Project
│       └── migrations/
├── blog_penny/                    # Configuración principal
│   ├── settings.py                # Configuración Django
│   ├── urls.py                    # URLs principales
│   ├── wsgi.py
│   └── asgi.py
├── templates/                     # Templates globales
│   ├── base.html                  # Template base con navbar y footer
│   ├── blog/
│   │   ├── post_list.html         # Lista de posts con paginación
│   │   └── post_detail.html       # Detalle con Markdown renderizado
│   └── portfolio/
│       └── home.html              # Página principal del portfolio
├── static/                        # Archivos estáticos globales
│   └── css/
│       └── style.css              # 498 líneas de CSS personalizado
├── media/                         # Archivos subidos (imágenes)
├── staticfiles/                   # Archivos estáticos recolectados
├── db.sqlite3                     # Base de datos (156KB con datos)
├── manage.py
├── populate_data.py               # Script para generar datos de ejemplo
└── MARKDOWN_EDITOR_GUIDE.md       # Guía del editor Markdown
```

## Modelos de Datos

### App: `portfolio`

#### `About`
```python
- title: CharField(200)
- content: TextField()  # Contenido en Markdown
- profile_image: ImageField(upload_to='portfolio/', blank=True)
- created_at: DateTimeField(auto_now_add=True)
- updated_at: DateTimeField(auto_now=True)
```

#### `Skill`
```python
- name: CharField(100)
- category: CharField(50)  # Ej: "Backend", "Frontend", "Tools"
- proficiency_level: IntegerField(0-100)
- created_at: DateTimeField(auto_now_add=True)

Meta:
  ordering = ['category', '-proficiency_level']
```

#### `Project`
```python
- title: CharField(200)
- description: TextField()  # Contenido en Markdown
- image: ImageField(upload_to='portfolio/', blank=True)
- github_url: URLField(blank=True)
- live_url: URLField(blank=True)
- technologies: CharField(200)  # Ej: "Django, React, PostgreSQL"
- featured: BooleanField(default=False)
- created_at: DateTimeField(auto_now_add=True)
- updated_at: DateTimeField(auto_now=True)

Meta:
  ordering = ['-featured', '-created_at']
```

### App: `blog`

#### `BlogPost`
```python
- title: CharField(200)
- slug: SlugField(unique=True)  # Auto-generado desde title
- content: TextField()  # Contenido en Markdown
- excerpt: TextField(blank=True)  # Resumen breve
- featured_image: ImageField(upload_to='blog/', blank=True)
- published: BooleanField(default=False)
- created_at: DateTimeField(auto_now_add=True)
- updated_at: DateTimeField(auto_now=True)
- published_at: DateTimeField(blank=True, null=True)  # Auto-set al publicar

Métodos especiales:
- save(): Auto-genera slug y establece published_at

Meta:
  ordering = ['-published_at']
```

## Sistema de URLs

### URLs Principales (`blog_penny/urls.py`)
- `/` → portfolio.urls (namespace: 'portfolio')
- `/blog/` → blog.urls (namespace: 'blog')
- `/admin/` → Django admin

### Portfolio URLs (`apps/portfolio/urls.py`)
- `/` → HomeView (name: 'home')
- `/project/<int:pk>/` → ProjectDetailView (name: 'project_detail')

### Blog URLs (`apps/blog/urls.py`)
- `/blog/` → PostListView (name: 'post_list')
- `/blog/post/<slug:slug>/` → PostDetailView (name: 'post_detail')

## Vistas (CBV - Class Based Views)

### Portfolio
- **HomeView**: TemplateView que pasa About, Skills agrupadas por categoría, y Projects al contexto
- **ProjectDetailView**: DetailView para mostrar detalles de un proyecto

### Blog
- **PostListView**: ListView con:
  - Filtro: `queryset = BlogPost.objects.filter(published=True)`
  - Paginación: 10 posts por página
  - Template: `blog/post_list.html`

- **PostDetailView**: DetailView que:
  - Renderiza content a HTML usando Markdown con extensiones 'extra' y 'codehilite'
  - Pasa el HTML renderizado al contexto como `content_html`

## Panel de Administración

### Características Especiales

#### Editor Markdown Personalizado (`apps/blog/admin.py`)

- **Widget**: `MarkdownEditorWidget` con textarea personalizado
- **Assets**:
  - CSS: `admin/css/markdown_editor.css`
  - JS: `admin/js/markdown_editor.js`

- **Funcionalidades del Editor**:
  - Toolbar con 12 botones de formato Markdown
  - Atajos de teclado (Ctrl+B, Ctrl+I, etc.)
  - Clases JS orientadas a objetos (MarkdownEditor, ActionHandler)
  - Diseño responsive

#### Admin de BlogPost
```python
- list_display: ['title', 'published', 'published_at', 'created_at']
- list_filter: ['published', 'created_at', 'published_at']
- search_fields: ['title', 'content', 'excerpt']
- list_editable: ['published']
- prepopulated_fields: {'slug': ('title',)}
- fieldsets: Contenido, Publicación, Metadata
- readonly_fields: ['created_at', 'updated_at']
```

#### Admin de Skill
```python
- list_display: ['name', 'category', 'proficiency_level']
- list_filter: ['category']
- list_editable: ['proficiency_level']
```

#### Admin de Project
```python
- list_display: ['title', 'featured', 'created_at']
- list_filter: ['featured', 'created_at']
- list_editable: ['featured']
```

## Templates y Frontend

### Herencia de Templates
- **base.html**: Template padre con navbar, mensajes, content block, y footer
- Todos los templates extienden de `base.html`

### Estructura HTML
```html
{% extends 'base.html' %}
{% block content %}
  <!-- Contenido específico -->
{% endblock %}
```

### CSS
- **Archivo principal**: `static/css/style.css` (498 líneas)
- **Características**:
  - CSS puro, sin frameworks
  - Variables CSS para colores y espaciados
  - Grid y Flexbox para layouts
  - Diseño responsive con media queries
  - Navbar sticky
  - Estilos para código con CodeHilite

### JavaScript
- **Editor Markdown**: Vanilla JS orientado a objetos
- **Sin frameworks**: No usa jQuery, React, Vue, etc.

## Renderizado de Markdown

### Configuración en Vistas
```python
import markdown

# En PostDetailView:
content_html = markdown.markdown(
    self.object.content,
    extensions=['extra', 'codehilite']
)
```

### Extensiones Usadas
- **extra**: Tablas, listas definición, footnotes, etc.
- **codehilite**: Resaltado de sintaxis para bloques de código

## Archivos Estáticos y Media

### Configuración (`settings.py`)
```python
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static', BASE_DIR / 'apps' / 'blog' / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'
```

### Servir en Desarrollo
```python
# blog_penny/urls.py
from django.conf import settings
from django.conf.urls.static import static

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
```

## Script de Datos de Ejemplo

**Archivo**: `populate_data.py`

### Genera:
- 1 registro About con contenido Markdown
- 20 Skills en 6 categorías:
  - Backend, Frontend, Database, DevOps, Tools, Soft Skills
- 4 Projects (2 destacados)
- 4 BlogPosts con contenido técnico sobre:
  - Django
  - CSS Grid
  - Machine Learning
  - Git Best Practices

### Uso:
```bash
python populate_data.py
```

## Convenciones de Código

### Estilo de Código Python
- PEP 8 compliant
- Nombres de clases: PascalCase (ej: `BlogPost`, `HomeView`)
- Nombres de funciones/variables: snake_case (ej: `post_list`, `created_at`)
- Imports organizados: stdlib → third-party → locales

### Modelos
- Siempre incluir `created_at` y `updated_at` timestamps cuando sea relevante
- Usar `blank=True` para campos opcionales en formularios
- Usar `null=True` para campos opcionales en BD
- Definir `Meta` class con `ordering` cuando sea relevante
- Implementar `__str__()` method

### Vistas
- Usar Class-Based Views (CBV) preferentemente
- Importar desde `django.views.generic`
- Nombres de vistas: `<Model><Action>View` (ej: `PostListView`)

### Templates
- Usar `{% load static %}` al inicio si se necesitan archivos estáticos
- Usar `{% url 'namespace:name' %}` para URLs
- Usar filtros Django: `{{ content|safe }}`, `{{ post.title|title }}`

### URLs
- Usar `path()` en lugar de `url()`
- Siempre definir `name` para cada URL
- Usar namespaces en `include()`
- Usar tipos de path: `<int:pk>`, `<slug:slug>`

## Estado Actual del Proyecto

### Entorno: Desarrollo
```python
DEBUG = True
ALLOWED_HOSTS = []
SECRET_KEY = presente (cambiar para producción)
```

### Base de Datos
- SQLite3 con 156KB de datos
- Contiene datos de ejemplo ya poblados
- Migraciones aplicadas

### Pendiente para Producción
1. Cambiar `DEBUG = False`
2. Configurar `ALLOWED_HOSTS`
3. Cambiar `SECRET_KEY`
4. Migrar a PostgreSQL/MySQL
5. Configurar servidor de archivos estáticos
6. Configurar almacenamiento de media (S3, etc.)
7. Implementar HTTPS
8. Crear `requirements.txt` formal
9. Usar variables de entorno (.env)
10. Configurar logging y cache

## Comandos Útiles

### Desarrollo
```bash
# Iniciar servidor
python manage.py runserver

# Aplicar migraciones
python manage.py migrate

# Crear migraciones
python manage.py makemigrations

# Crear superusuario
python manage.py createsuperuser

# Recolectar estáticos
python manage.py collectstatic

# Poblar datos de ejemplo
python populate_data.py

# Shell de Django
python manage.py shell
```

### Testing
```bash
# Ejecutar tests
python manage.py test

# Test específico
python manage.py test apps.blog.tests
```

## Patrones y Best Practices Usados

1. **Apps modulares**: Separación clara entre blog y portfolio
2. **CBV**: Uso de Class-Based Views para reutilización
3. **DRY**: Template base para evitar repetición
4. **Slugs**: URLs amigables para SEO
5. **Soft delete**: No se eliminan posts, solo se despublican
6. **Timestamps**: Auditoría con created_at/updated_at
7. **Namespacing**: URLs con namespaces para evitar colisiones
8. **Admin personalizado**: Mejora la UX del panel de administración
9. **Static/Media separation**: Archivos estáticos vs subidos
10. **Markdown**: Contenido flexible y portable

## Notas Importantes para Desarrollo

### Al Agregar Nuevas Funcionalidades

1. **Nuevos modelos**:
   - Agregar a `models.py` correspondiente
   - Ejecutar `makemigrations` y `migrate`
   - Registrar en `admin.py`
   - Actualizar `populate_data.py` si es necesario

2. **Nuevas vistas**:
   - Usar CBV cuando sea posible
   - Agregar URL en `urls.py` con namespace
   - Crear template correspondiente
   - Extender de `base.html`

3. **Nuevos estilos**:
   - Agregar a `static/css/style.css`
   - Mantener consistencia con estilos existentes
   - Probar responsive design

4. **Nuevo contenido Markdown**:
   - Usar extensiones 'extra' y 'codehilite'
   - Renderizar con `markdown.markdown()`
   - Mostrar con filtro `|safe` en template

### Archivos que NO se deben modificar sin cuidado
- `db.sqlite3`: Base de datos (hacer backup antes de cambios)
- `migrations/`: Historial de migraciones (no editar manualmente)
- `manage.py`: Script de Django (no modificar)
- `venv/`: Entorno virtual (no versionar)

### Archivos de Configuración Sensibles
- `settings.py`: Contiene SECRET_KEY y configuración de BD
- `.env` (crear para producción): Variables de entorno sensibles

## Referencias y Documentación

- **Django Docs**: https://docs.djangoproject.com/
- **Python Markdown**: https://python-markdown.github.io/
- **Editor Markdown**: Ver `MARKDOWN_EDITOR_GUIDE.md`
- **README**: Ver `README.md` para instalación y uso

---

**Última actualización**: 2025-11-04
**Versión Django**: 5.2.7
**Python**: 3.13
