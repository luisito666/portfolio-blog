# Blog Penny

Un blog personal y portfolio profesional construido con Django, diseñado para desarrolladores y profesionales técnicos que desean compartir conocimiento y mostrar su trabajo.

## Tabla de Contenidos

- [Características Principales](#características-principales)
- [Stack Tecnológico](#stack-tecnológico)
- [Estructura del Proyecto](#estructura-del-proyecto)
- [Instalación y Despliegue](#instalación-y-despliegue)
  - [Desarrollo con Docker](#desarrollo-con-docker-recomendado)
  - [Kubernetes con Helm](#kubernetes-con-helm)
- [Configuración](#configuración)
- [Funcionalidades](#funcionalidades)
- [Modelos de Datos](#modelos-de-datos)
- [Editor Markdown](#editor-markdown)
- [Licencia](#licencia)

## Características Principales

- **Portfolio Personal**: Muestra información sobre ti, tus habilidades técnicas y proyectos destacados
- **Blog Técnico**: Sistema de publicación con soporte completo para Markdown
- **Editor Markdown Avanzado**: Panel de administración con editor personalizado que incluye toolbar y atajos de teclado
- **Resaltado de Sintaxis**: Renderizado de código con CodeHilite para publicaciones técnicas
- **Diseño Responsive**: Interfaz moderna y adaptable a dispositivos móviles
- **Panel de Administración Mejorado**: Gestión intuitiva de contenido con filtros y búsqueda avanzada
- **Containerización**: Soporte completo para Docker y Docker Compose
- **Orquestación**: Despliegue en Kubernetes usando Helm Charts
- **Producción Ready**: Configuración con Nginx, PostgreSQL y Gunicorn

## Stack Tecnológico

### Backend
- **Framework**: Django 5.2.7
- **Python**: 3.13 (desarrollo) / 3.11 (Docker)
- **WSGI Server**: Gunicorn 21.2.0
- **Base de Datos**: SQLite3 (desarrollo) / PostgreSQL 15 (producción)
- **Markdown**: Markdown 3.9 con extensiones 'extra' y 'codehilite'
- **Imágenes**: Pillow 12.0.0
- **Configuración**: python-decouple 3.8

### Frontend
- **HTML5, CSS3, JavaScript Vanilla**
- **Tipografía**: Google Fonts (Inter)
- **Sin frameworks JS**: Código JavaScript puro

### Infraestructura
- **Reverse Proxy**: Nginx (Alpine)
- **Containerización**: Docker
- **Orquestación**: Kubernetes + Helm
- **Base de Datos**: PostgreSQL 15 (Alpine)

## Estructura del Proyecto

```
portfolio-blog/
├── src/                           # Código fuente de la aplicación
│   ├── apps/
│   │   ├── blog/                  # Aplicación del blog
│   │   │   ├── models.py          # Modelo BlogPost
│   │   │   ├── views.py           # Vistas de lista y detalle
│   │   │   ├── admin.py           # Admin con editor Markdown
│   │   │   └── static/admin/      # CSS y JS del editor
│   │   └── portfolio/             # Aplicación del portfolio
│   │       ├── models.py          # Modelos About, Skill, Project
│   │       └── views.py           # Vista principal
│   ├── templates/                 # Plantillas HTML
│   │   ├── base.html
│   │   ├── blog/
│   │   └── portfolio/
│   ├── static/                    # Archivos estáticos globales
│   │   └── css/style.css
│   ├── media/                     # Archivos subidos
│   ├── core/                      # Configuración Django
│   └── manage.py
│
├── docker/                        # Configuración Docker
│   ├── entrypoint.sh              # Script de inicialización
│   ├── nginx/
│   │   └── nginx.conf             # Configuración Nginx
│   └── postgres/
│       └── init.sql               # Inicialización PostgreSQL
│
├── charts/                        # Helm Charts
│   └── portfolio/
│       ├── Chart.yaml             # Metadata del chart
│       ├── values.yaml            # Valores por defecto
│       └── templates/             # Templates de Kubernetes
│           ├── deployment.yaml
│           ├── service.yaml
│           ├── ingress.yaml
│           ├── configmap.yaml
│           ├── pvc.yaml
│           └── ...
│
├── .environment/                  # Variables de entorno
│   ├── django/
│   │   └── .env.example
│   └── postgres/
│       └── .env.example
│
├── Dockerfile                     # Imagen Docker de la aplicación
├── docker-compose.yaml            # Orquestación de contenedores
├── requirements.txt               # Dependencias Python
├── populate_data.py               # Script de datos de ejemplo
└── README.md
```

## Instalación y Despliegue

### Desarrollo con Docker (Recomendado)

#### Requisitos Previos
- Docker 24.0 o superior (incluye Docker Compose V2)

#### Arquitectura de Contenedores

La aplicación usa una arquitectura multi-contenedor con los siguientes servicios:

- **db**: PostgreSQL 15 (Alpine) con healthcheck y persistencia
- **web**: Django + Gunicorn con auto-migración y collectstatic
- **nginx**: Reverse proxy para servir archivos estáticos y proxy a Django

#### Inicio Rápido

1. **Clonar el repositorio**
   ```bash
   git clone <repository-url>
   cd portfolio-blog
   ```

2. **Construir e iniciar los contenedores**
   ```bash
   docker compose up -d --build
   ```

   > **Nota**: El proyecto viene con archivos `.env.example` pre-configurados que se usan directamente. Para producción, debes crear tus propios archivos `.env` con valores seguros.

3. **Verificar el estado de los servicios**
   ```bash
   docker compose ps
   ```

4. **Crear superusuario**
   ```bash
   docker compose exec web python manage.py createsuperuser
   ```

5. **(Opcional) Poblar datos de ejemplo**
   ```bash
   docker compose exec web python populate_data.py
   ```

6. **Acceder a la aplicación**
   - **Aplicación**: http://localhost
   - **Admin**: http://localhost/admin/

#### Personalizar Variables de Entorno (Opcional)

Si necesitas personalizar la configuración, puedes editar directamente:

**`.environment/postgres/.env.example`**:
```env
POSTGRES_DB=blog_db
POSTGRES_USER=blog_user
POSTGRES_PASSWORD=tu_password_seguro
```

**`.environment/django/.env.example`**:
```env
SECRET_KEY=tu_secret_key_aqui
DEBUG=0
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
DATABASE_URL=postgresql://blog_user:tu_password_seguro@db:5432/blog_db
```

Después de editar, reinicia los contenedores:
```bash
docker compose down
docker compose up -d
```

#### Comandos Útiles

```bash
# Ver logs de todos los servicios
docker compose logs -f

# Ver logs de un servicio específico
docker compose logs -f web

# Reiniciar un servicio
docker compose restart web

# Ejecutar comando en contenedor
docker compose exec web python manage.py <comando>

# Detener todos los servicios
docker compose down

# Detener y eliminar volúmenes (¡cuidado con los datos!)
docker compose down -v

# Reconstruir un servicio específico
docker compose up -d --build web

# Ver el estado de los contenedores
docker compose ps

# Ver el uso de recursos
docker compose stats
```

#### Gestión de Datos

Los datos se persisten en volúmenes Docker:
- **postgres_data**: Base de datos PostgreSQL
- **static_volume**: Archivos estáticos de Django
- **media_volume**: Archivos subidos por usuarios

Para hacer backup de la base de datos:
```bash
docker compose exec db pg_dump -U blog_user blog_db > backup.sql
```

Para restaurar:
```bash
docker compose exec -T db psql -U blog_user blog_db < backup.sql
```

---

### Kubernetes con Helm

#### Requisitos Previos
- Kubernetes cluster configurado (minikube, GKE, EKS, AKS, etc.)
- kubectl instalado y configurado
- Helm 3.x instalado
- Imagen Docker publicada en un registry (Docker Hub, GCR, etc.)

#### Preparar la Imagen Docker

1. **Construir la imagen**
   ```bash
   docker build -t <tu-usuario>/blog:latest .
   ```

2. **Publicar en Docker Hub** (o tu registry preferido)
   ```bash
   docker push <tu-usuario>/blog:latest
   ```

#### Configuración del Chart

1. **Editar valores del Helm Chart**

   Edita `charts/portfolio/values.yaml`:
   ```yaml
   replicaCount: 1

   image:
     repository: <tu-usuario>/blog
     pullPolicy: IfNotPresent
     tag: latest

   service:
     type: ClusterIP
     port: 80

   ingress:
     enabled: true
     className: "nginx"
     annotations:
       cert-manager.io/cluster-issuer: "letsencrypt-prod"
     hosts:
       - host: tudominio.com
         paths:
           - path: /
             pathType: Prefix
     tls:
       - secretName: blog-tls
         hosts:
           - tudominio.com

   configmap:
     ALLOWED_HOSTS: tudominio.com,www.tudominio.com
     CSRF_TRUSTED_ORIGINS: https://tudominio.com,https://www.tudominio.com
     DEBUG: "0"

   resources:
     limits:
       cpu: 500m
       memory: 512Mi
     requests:
       cpu: 250m
       memory: 256Mi

   autoscaling:
     enabled: true
     minReplicas: 2
     maxReplicas: 10
     targetCPUUtilizationPercentage: 80
   ```

2. **Crear Secrets de PostgreSQL**

   Edita `charts/portfolio/templates/postgres-secrets.yaml` o crea un secret manualmente:
   ```bash
   kubectl create secret generic postgres-credentials \
     --from-literal=POSTGRES_DB=blog_db \
     --from-literal=POSTGRES_USER=blog_user \
     --from-literal=POSTGRES_PASSWORD=tu_password_seguro \
     --from-literal=DATABASE_URL=postgresql://blog_user:tu_password_seguro@postgres:5432/blog_db
   ```

3. **Crear Secret de Django**
   ```bash
   kubectl create secret generic django-secrets \
     --from-literal=SECRET_KEY=tu_secret_key_muy_largo_y_aleatorio
   ```

#### Instalación del Chart

1. **Instalar el chart**
   ```bash
   cd charts
   helm install blog-portfolio ./portfolio
   ```

2. **Verificar el despliegue**
   ```bash
   kubectl get pods
   kubectl get services
   kubectl get ingress
   ```

3. **Ver logs de los pods**
   ```bash
   kubectl logs -f deployment/blog-portfolio
   ```

4. **Crear superusuario**
   ```bash
   # Obtener el nombre del pod
   kubectl get pods

   # Ejecutar comando en el pod
   kubectl exec -it <nombre-del-pod> -- python manage.py createsuperuser
   ```

#### Actualizar el Deployment

Cuando hagas cambios:
```bash
# Construir nueva imagen
docker build -t <tu-usuario>/blog:v1.1.0 .
docker push <tu-usuario>/blog:v1.1.0

# Actualizar el chart
helm upgrade blog-portfolio ./portfolio --set image.tag=v1.1.0
```

#### Desinstalar

```bash
helm uninstall blog-portfolio
```

#### Características del Helm Chart

- **Deployment**: Configuración de pods con Django + Nginx sidecar
- **Service**: Servicio ClusterIP para acceso interno
- **Ingress**: Configuración opcional para acceso externo
- **ConfigMap**: Variables de configuración no sensibles
- **Secrets**: Credenciales de base de datos y SECRET_KEY
- **PVC**: Persistent Volume Claims para media files
- **HPA**: Horizontal Pod Autoscaler (opcional)
- **Health Probes**: Liveness y readiness checks en `/health`
- **ServiceAccount**: Cuenta de servicio para el pod

---

## Configuración

### Variables de Entorno

El proyecto utiliza archivos `.env.example` que funcionan automáticamente para desarrollo. Para producción, debes crear archivos `.env` personalizados o usar secrets de Kubernetes.

#### Django (`.environment/django/.env.example`)

```env
# Django Core
SECRET_KEY=django-insecure-change-this-in-production
DEBUG=0
ALLOWED_HOSTS=localhost,127.0.0.1,tudominio.com

# Security
CSRF_TRUSTED_ORIGINS=https://tudominio.com,https://www.tudominio.com

# Database (usar DATABASE_URL o variables individuales)
DATABASE_URL=postgresql://blog_user:password@db:5432/blog_db

# O usar variables individuales:
# DB_ENGINE=django.db.backends.postgresql
# DB_NAME=blog_db
# DB_USER=blog_user
# DB_PASSWORD=password
# DB_HOST=db
# DB_PORT=5432

# Static/Media (opcional en Docker)
# STATIC_ROOT=/app/staticfiles
# MEDIA_ROOT=/app/media
```

#### PostgreSQL (`.environment/postgres/.env.example`)

```env
POSTGRES_DB=blog_db
POSTGRES_USER=blog_user
POSTGRES_PASSWORD=change_this_password
```

> **Desarrollo**: Los archivos `.env.example` se utilizan directamente por `docker-compose.yaml`.
>
> **Producción**: Crea archivos `.env` (sin `.example`) con valores seguros o usa secrets de Kubernetes.

### Configuración de Producción

Antes de desplegar en producción:

1. **Seguridad**
   - Cambiar `SECRET_KEY` por uno generado aleatoriamente
   - Establecer `DEBUG=False` o `DEBUG=0`
   - Configurar `ALLOWED_HOSTS` con tus dominios
   - Configurar `CSRF_TRUSTED_ORIGINS` con tus URLs

2. **Base de Datos**
   - Usar PostgreSQL en lugar de SQLite
   - Configurar backups automáticos
   - Usar contraseñas fuertes

3. **Archivos Estáticos**
   - Los archivos estáticos se sirven vía Nginx
   - Los archivos media deben persistirse en PVC (Kubernetes) o volumen (Docker)
   - Considerar usar CDN para archivos estáticos

4. **HTTPS**
   - Configurar certificados SSL/TLS
   - En Kubernetes: usar cert-manager con Let's Encrypt
   - En Docker: configurar certificados en Nginx

5. **Monitoreo**
   - Configurar logging apropiado
   - Implementar métricas (Prometheus + Grafana)
   - Configurar alertas

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

## Modelos de Datos

### Blog

**BlogPost**
- `title`: CharField(200)
- `slug`: SlugField(unique=True) - Auto-generado
- `content`: TextField() - Contenido en Markdown
- `excerpt`: TextField(blank=True) - Resumen breve
- `featured_image`: ImageField(upload_to='blog/', blank=True)
- `published`: BooleanField(default=False)
- `created_at`: DateTimeField(auto_now_add=True)
- `updated_at`: DateTimeField(auto_now=True)
- `published_at`: DateTimeField(blank=True, null=True)

### Portfolio

**About**
- `title`: CharField(200)
- `content`: TextField() - Contenido en Markdown
- `profile_image`: ImageField(upload_to='portfolio/', blank=True)
- `created_at`: DateTimeField(auto_now_add=True)
- `updated_at`: DateTimeField(auto_now=True)

**Skill**
- `name`: CharField(100)
- `category`: CharField(50) - Ej: "Backend", "Frontend"
- `proficiency_level`: IntegerField(0-100)
- `created_at`: DateTimeField(auto_now_add=True)

**Project**
- `title`: CharField(200)
- `description`: TextField() - Contenido en Markdown
- `image`: ImageField(upload_to='portfolio/', blank=True)
- `github_url`: URLField(blank=True)
- `live_url`: URLField(blank=True)
- `technologies`: CharField(200)
- `featured`: BooleanField(default=False)
- `created_at`: DateTimeField(auto_now_add=True)
- `updated_at`: DateTimeField(auto_now=True)

## Editor Markdown

El panel de administración incluye un editor Markdown avanzado con:

### Toolbar con 12 acciones
- Negrita, Itálica, Encabezado
- Enlaces e Imágenes
- Código inline y bloques de código
- Listas ordenadas y desordenadas
- Citas y líneas horizontales

### Atajos de Teclado
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

**Uso**:
```bash
python populate_data.py
```

## Licencia

Este proyecto es de código abierto y está disponible para uso personal y educativo.

## Autor

Luis - Developer & Tech Enthusiast

---

**Desarrollado con Django y mucho café ☕**

**Stack**: Django + PostgreSQL + Nginx + Docker + Kubernetes + Helm
