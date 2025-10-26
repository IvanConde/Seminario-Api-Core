# 🏗️ Arquitectura del Sistema Core Unificado

## Diagrama de Flujo

```
┌─────────────────────────────────────────────────────────────────┐
│                        FRONTEND (Chat UI)                       │
│                     (React/Vue/Angular)                         │
│                     Puerto: 3000                               │
└────────────────────┬────────────────────────────────────────────┘
                     │ HTTP/WebSocket
                     ▼
┌─────────────────────────────────────────────────────────────────┐
│                        CORE API                                 │
│                    (FastAPI + Python)                          │
│                     Puerto: 8003                               │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │              API Endpoints                                  ││
│  │                                                             ││
│  │  GET /api/v1/messages              - Obtener mensajes      ││
│  │  POST /api/v1/messages/unified     - Recibir mensajes      ││
│  │  POST /api/v1/send                 - Enviar mensaje        ││
│  │  GET /api/v1/conversations         - Obtener conversaciones││
│  │  GET /api/v1/channels              - Obtener canales      ││
│  │  WebSocket /ws                     - Mensajes en tiempo real ││
│  └─────────────────────────────────────────────────────────────┘│
│                                                                 │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │              Database Layer (MySQL)                        ││
│  │                                                             ││
│  │  • Tabla: channels                                          ││
│  │  • Tabla: conversations                                     ││
│  │  • Tabla: messages                                          ││
│  │  • SQLAlchemy ORM                                           ││
│  └─────────────────────────────────────────────────────────────┘│
└────────────────────┬────────────────────────────────────────────┘
                     │ HTTP Webhooks
                     ▼
┌─────────────────────────────────────────────────────────────────┐
│                    CHANNEL SERVICES                             │
│                                                                 │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐            │
│  │ WhatsApp    │  │   Gmail     │  │ Instagram   │            │
│  │ Service     │  │   Service   │  │   Service   │            │
│  │ Puerto:     │  │ Puerto:     │  │ Puerto:     │            │
│  │ 8000        │  │ 8001        │  │ 8002        │            │
│  └─────────────┘  └─────────────┘  └─────────────┘            │
└─────────────────────────────────────────────────────────────────┘
```

## 🔄 Flujo de Mensajes

### 1. Mensaje Entrante (Webhook)
```
Usuario → Canal (WhatsApp/Gmail/IG) → Servicio Canal → Core API → BD
```

### 2. Mensaje Saliente (Envío)
```
Frontend → Core API → Servicio Canal → Canal → Usuario
```

## 📊 Estructura de Base de Datos

### Tabla: channels
- `id` (PK)
- `name` (whatsapp, gmail, instagram)
- `display_name`
- `is_active`
- `created_at`

### Tabla: conversations
- `id` (PK)
- `channel_id` (FK)
- `external_id` (ID del canal externo)
- `participant_name`
- `participant_identifier` (email, phone, username)
- `is_active`
- `created_at`, `updated_at`

### Tabla: messages
- `id` (PK)
- `conversation_id` (FK)
- `external_message_id`
- `content`
- `message_type` (text, image, audio, video, document)
- `direction` (incoming, outgoing)
- `sender_name`
- `sender_identifier`
- `timestamp`
- `is_read`
- `metadata` (JSON)
- `created_at`

## 🚀 Instrucciones de Instalación

### 1. Configurar MySQL
```sql
CREATE DATABASE unified_messaging;
```

### 2. Instalar dependencias del Core
```bash
cd core-unir
pip install -r requirements.txt
```

### 3. Configurar variables de entorno
```bash
cp env.example .env
# Editar .env con tus credenciales de MySQL
```

### 4. Iniciar Core API
```bash
python -m src.main
```

### 5. Iniciar WhatsApp Service
```bash
cd whatsapp-unir
python -m src.whatsapp_service
```

## 📡 Endpoints Principales

### Core API (Puerto 8003)
- `GET /` - Health check
- `GET /api/v1/messages` - Obtener mensajes
- `POST /api/v1/messages/unified` - Recibir mensajes de canales
- `POST /api/v1/send` - Enviar mensaje
- `GET /api/v1/conversations` - Obtener conversaciones
- `GET /api/v1/channels` - Obtener canales
- `WS /ws` - WebSocket para tiempo real

### WhatsApp Service (Puerto 8000)
- `GET /webhook/whatsapp` - Verificación de webhook
- `POST /webhook/whatsapp` - Recibir mensajes
- `POST /send/whatsapp` - Enviar mensajes

## 🔧 Próximos Pasos

1. **Configurar Gmail Service** (Puerto 8001)
2. **Configurar Instagram Service** (Puerto 8002)
3. **Desarrollar Frontend** que consuma el Core API
4. **Implementar autenticación** y autorización
5. **Agregar tests** y documentación completa

## 📝 Notas Importantes

- El Core API se ejecuta en el puerto 8003
- Los servicios de canal se comunican con el Core via HTTP
- La base de datos MySQL almacena todos los mensajes unificados
- WebSocket permite mensajes en tiempo real al frontend
- Cada canal mantiene su propia lógica de negocio
