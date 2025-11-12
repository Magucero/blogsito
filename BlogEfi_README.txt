# 📘 BlogEfi API

API REST construida con **Flask**, **SQLAlchemy** y **JWT**, que permite manejar usuarios, posts, comentarios, categorías y estadísticas, con control de roles (`user`, `moderator`, `admin`).

---

## 🚀 Instalación

### 1️⃣ Clonar el repositorio
```bash
git clone https://github.com/tuusuario/blogEfi.git
cd blogEfi
```

### 2️⃣ Crear entorno virtual e instalar dependencias
```bash
python -m venv venv
source venv/bin/activate   # En Linux
# o venv\Scripts\activate  # En Windows

pip install -r requirements.txt
```

### 3️⃣ Configurar la base de datos

Editar la URI en `app.py`:
```python
app.config['SQLALCHEMY_DATABASE_URI'] = "mysql+pymysql://root:@localhost/blogEfi"
```

Luego crear la base de datos desde MySQL:
```sql
CREATE DATABASE blogEfi CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### 4️⃣ Ejecutar migraciones
```bash
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

### 5️⃣ Ejecutar la app
```bash
python app.py
```
La API quedará disponible en:  
👉 **http://127.0.0.1:5000**

---

## 🧩 Endpoints principales

### 🔐 **Autenticación**
| Método | Endpoint | Descripción |
|--------|-----------|-------------|
| POST | `/api/register` | Crear usuario nuevo |
| POST | `/api/login` | Iniciar sesión y obtener JWT |

**Ejemplo:**
```json
POST /api/login
{
  "email": "admin@mail.com",
  "password": "123456"
}
```
📤 **Respuesta:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJh..."
}
```

---

### 📰 **Posts**
| Método | Endpoint | Requiere token | Descripción |
|--------|-----------|----------------|--------------|
| GET | `/api/posts` | ❌ | Listar todos los posts |
| GET | `/api/posts/<id>` | ❌ | Ver post específico |
| POST | `/api/posts` | ✅ user+ | Crear nuevo post |
| PUT | `/api/posts/<id>` | ✅ autor/admin | Editar post |
| DELETE | `/api/posts/<id>` | ✅ autor/admin | Eliminar post |

---

### 💬 **Comentarios**
| Método | Endpoint | Requiere token | Descripción |
|--------|-----------|----------------|--------------|
| GET | `/api/posts/<id>/comments` | ❌ | Ver comentarios de un post |
| POST | `/api/posts/<id>/comments` | ✅ user+ | Crear comentario |
| DELETE | `/api/comments/<id>` | ✅ autor/moderador/admin | Eliminar comentario |

---

### 📊 **Estadísticas**
| Método | Endpoint | Rol necesario | Descripción |
|--------|-----------|----------------|--------------|
| GET | `/api/stats` | moderator/admin | Métricas del sitio |

---

## 👥 Roles y credenciales de prueba

| Rol | Email | Password | Permisos |
|-----|--------|-----------|-----------|
| **Admin** | admin@mail.com | 123456 | Acceso total |
| **Moderator** | mod@mail.com | 123456 | Moderar comentarios, ver stats |
| **User** | user@mail.com | 123456 | Crear posts y comentarios |

---

## 🧪 Archivo de pruebas

Podés importar el archivo `BlogEfi.postman_collection.json` en **Postman** o **Thunder Client** para probar todos los endpoints.

También podés usar un archivo `.http` con ejemplos, como:
```http
### Login
POST http://127.0.0.1:5000/api/login
Content-Type: application/json

{
  "email": "admin@mail.com",
  "password": "123456"
}

### Crear Post
POST http://127.0.0.1:5000/api/posts
Authorization: Bearer {{token}}
Content-Type: application/json

{
  "title": "Mi primer post",
  "content": "Este es el contenido del post"
}
```

---

## 🗄️ Datos de prueba (SQL)

```sql
INSERT INTO user (username, email, password, role, is_active)
VALUES
('Admin', 'admin@mail.com', '<hash_de_password>', 'admin', 1),
('Moderador', 'mod@mail.com', '<hash_de_password>', 'moderator', 1),
('Usuario', 'user@mail.com', '<hash_de_password>', 'user', 1);
```

*(Usá `werkzeug.security.generate_password_hash('123456')` para generar el hash antes de insertar)*

---

## 🧰 Tecnologías utilizadas

- Python 3.13  
- Flask  
- Flask-JWT-Extended  
- Flask-Migrate  
- Flask-Marshmallow  
- SQLAlchemy  
- MySQL  

---

## 🧑‍💻 Autor
**Santiago Thomas Pereyra Gallardo y **  
 
