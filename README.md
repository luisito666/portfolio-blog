# Blog Penny

Un blog personal y portfolio profesional construido con Django, diseñado para desarrolladores y profesionales técnicos que desean compartir conocimiento y mostrar su trabajo.

## Características Principales

- **Portfolio Personal**: Muestra información sobre ti, tus habilidades técnicas y proyectos destacados
- **Blog Técnico**: Sistema de publicación con soporte completo para Markdown
- **Editor Markdown Avanzado**: Panel de administración con editor personalizado que incluye toolbar y atajos de teclado
- **Resaltado de Sintaxis**: Renderizado de código con CodeHilite para publicaciones técnicas
- **Diseño Responsive**: Interfaz moderna y adaptable a dispositivos móviles
- **Panel de Administración Mejorado**: Gestión intuitiva de contenido con filtros y búsqueda avanzada

## Tecnologías

- **Backend**: Django 5.2.7 + Python 3.13
- **Base de Datos**: SQLite3
- **Frontend**: HTML5, CSS3, JavaScript Vanilla
- **Markdown**: Markdown 3.9 con extensiones 'extra' y 'codehilite'
- **Imágenes**: Pillow 12.0.0
- **Tipografía**: Google Fonts (Inter)

## Estructura del Proyecto

```
blog-penny/
├── apps/
│   ├── blog/              # Aplicación del blog
│   │   ├── models.py      # Modelo BlogPost
│   │   ├── views.py       # Vistas de lista y detalle
│   │   ├── admin.py       # Admin con editor Markdown personalizado
│   │   └── static/admin/  # CSS y JS del editor
│   └── portfolio/         # Aplicación del portfolio
│       ├── models.py      # Modelos About, Skill, Project
│       └── views.py       # Vista principal del portfolio
├── templates/             # Plantillas HTML
│   ├── base.html
│   ├── blog/
│   └── portfolio/
├── static/               # Archivos estáticos globales
│   └── css/
│       └── style.css
├── media/                # Archivos subidos
├── blog_penny/           # Configuración del proyecto
└── manage.py
```

## Instalación

### Requisitos Previos

- Python 3.13 o superior
- pip (gestor de paquetes de Python)

### Pasos de Instalación

1. **Clonar o descargar el repositorio**
   ```bash
   cd blog-penny
   ```

2. **Crear y activar entorno virtual**
   ```bash
   python -m venv venv

   # En Linux/Mac:
   source venv/bin/activate

   # En Windows:
   venv\Scripts\activate
   ```

3. **Instalar dependencias**
   ```bash
   pip install Django==5.2.7
   pip install Markdown==3.9
   pip install Pillow==12.0.0
   ```

4. **Aplicar migraciones**
   ```bash
   python manage.py migrate
   ```

5. **Crear un superusuario** (para acceder al panel de administración)
   ```bash
   python manage.py createsuperuser
   ```

6. **Recolectar archivos estáticos**
   ```bash
   python manage.py collectstatic
   ```

7. **(Opcional) Poblar con datos de ejemplo**
   ```bash
   python populate_data.py
   ```

## Uso

### Iniciar el servidor de desarrollo

```bash
python manage.py runserver
```

### Acceder a la aplicación

- **Portfolio Principal**: http://127.0.0.1:8000/
- **Blog**: http://127.0.0.1:8000/blog/
- **Panel de Administración**: http://127.0.0.1:8000/admin/

## Funcionalidades

### Portfolio

- **Sección About**: Información personal con imagen de perfil
- **Skills**: Habilidades técnicas organizadas por categorías con niveles de competencia
- **Proyectos**: Muestra proyectos con imágenes, descripciones, enlaces a GitHub y demos en vivo
- **Proyectos Destacados**: Sistema para resaltar proyectos importantes

### Blog

- **Publicaciones con Markdown**: Escribe contenido con sintaxis Markdown completa
- **Slug Automático**: Generación automática de URLs amigables
- **Sistema de Publicación**: Control de visibilidad con estados publicado/borrador
- **Paginación**: Lista de posts paginada (10 por página)
- **Resaltado de Código**: Sintaxis highlighting para bloques de código
- **Imágenes Destacadas**: Cada post puede tener una imagen principal

### Editor Markdown Personalizado

El panel de administración incluye un editor Markdown avanzado con:

#### Toolbar con 12 acciones:
- Negrita, Itálica, Encabezado
- Enlaces e Imágenes
- Código inline y bloques de código
- Listas ordenadas y desordenadas
- Citas y líneas horizontales

#### Atajos de Teclado:
- `Ctrl+B`: Negrita
- `Ctrl+I`: Itálica
- `Ctrl+H`: Encabezado
- `Ctrl+L`: Enlace
- `Ctrl+Shift+I`: Imagen
- `Ctrl+Shift+C`: Código inline
- `Ctrl+Shift+B`: Bloque de código
- `Ctrl+Q`: Cita
- `Ctrl+U`: Lista desordenada
- `Ctrl+Shift+O`: Lista ordenada
- `Ctrl+R`: Línea horizontal

Para más información, consulta [MARKDOWN_EDITOR_GUIDE.md](MARKDOWN_EDITOR_GUIDE.md)

## Configuración para Producción

Antes de desplegar en producción, asegúrate de:

1. **Cambiar configuraciones de seguridad** en `blog_penny/settings.py`:
   ```python
   DEBUG = False
   SECRET_KEY = 'tu-secret-key-segura'
   ALLOWED_HOSTS = ['tudominio.com']
   ```

2. **Usar una base de datos robusta** (PostgreSQL, MySQL)

3. **Configurar archivos estáticos**:
   - Usar WhiteNoise o servir desde CDN
   - Configurar servicio de almacenamiento para media files (AWS S3, etc.)

4. **Implementar HTTPS**

5. **Crear archivo de requerimientos**:
   ```bash
   pip freeze > requirements.txt
   ```

6. **Usar variables de entorno** para configuraciones sensibles

7. **Configurar logging apropiado**

8. **Implementar sistema de caché**

## Script de Datos de Ejemplo

El proyecto incluye `populate_data.py` que genera:

- 1 sección About completa
- 20 skills en 6 categorías diferentes
- 4 proyectos de ejemplo (2 destacados)
- 4 posts de blog con contenido técnico sobre:
  - Django
  - CSS Grid
  - Machine Learning con Python
  - Git Best Practices

## Modelos de Datos

### Blog
- **BlogPost**: title, slug, content (Markdown), excerpt, featured_image, published, published_at

### Portfolio
- **About**: title, content (Markdown), profile_image
- **Skill**: name, category, proficiency_level (0-100)
- **Project**: title, description (Markdown), image, github_url, live_url, technologies, featured

## Licencia

Este proyecto es de código abierto y está disponible para uso personal y educativo.

## Autor

Luis - [Tu información de contacto o perfil]

---

Desarrollado con Django y mucho café
