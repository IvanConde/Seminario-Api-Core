# Core Unified Messaging API

API para unificar mensajes de WhatsApp, Gmail e Instagram.

## 🚀 Inicio Rápido

### 1. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 2. Configurar base de datos MySQL

Crear la base de datos:
```sql
CREATE DATABASE unified_messaging;
```

### 3. Configurar variables de entorno

Crear archivo `.env`:
```env
DB_HOST=localhost
DB_PORT=3306
DB_NAME=unified_messaging
DB_USER=root
DB_PASSWORD=tu_password
API_HOST=0.0.0.0
API_PORT=8003
CORE_SECRET_KEY=tu-secret-key-aqui
```

### 4. Ejecutar la aplicación

```bash
python -m src.main
```

La API estará disponible en: `http://localhost:8003`

## 📡 Endpoints Principales

### Mensajes
- `GET /api/v1/messages` - Obtener mensajes
- `POST /api/v1/messages/unified` - Recibir mensajes unificados
- `POST /api/v1/send` - Enviar mensaje

### Conversaciones
- `GET /api/v1/conversations` - Obtener conversaciones
- `GET /api/v1/conversations/{id}` - Obtener conversación específica

### Canales
- `GET /api/v1/channels` - Obtener canales activos
- `GET /api/v1/channels/{name}/stats` - Estadísticas del canal

### WebSocket
- `WS /ws` - Conexión WebSocket para mensajes en tiempo real

## 🔧 Documentación

- Swagger UI: `http://localhost:8003/docs`
- ReDoc: `http://localhost:8003/redoc`

## 🏗️ Arquitectura

```
Frontend (Chat UI)
       ↓
Core API (Puerto 8003)
       ↓
WhatsApp Service (Puerto 8000)
Gmail Service (Puerto 8001)
Instagram Service (Puerto 8002)
```
