# Chatbot Inteligente Basado en Rasa

Sistema conversacional desarrollado como proyecto de tesis utilizando Rasa y técnicas de Procesamiento de Lenguaje Natural (NLP) para automatizar interacciones y brindar respuestas inteligentes.

El proyecto implementa arquitectura de IA conversacional basada en intents, entities, stories y políticas de diálogo, permitiendo mantener conversaciones contextuales y escalables.

---

# Características

* Desarrollo de chatbot utilizando Rasa Open Source

* Procesamiento de Lenguaje Natural (NLU)

* Gestión de diálogos contextuales

* Entrenamiento de intents y entities

* Automatización de respuestas

* Arquitectura modular y escalable

* Integración con APIs externas

* Soporte para entrenamiento personalizado

* Respuestas automáticas mediante IA

* Integración con APIs

* Procesamiento de lenguaje natural

* Personalización de prompts

* Sistema modular y escalable

* Manejo de contexto conversacional

---

# Tecnologías Utilizadas

* Python
* Rasa
* Rasa NLU
* Machine Learning
* Procesamiento de Lenguaje Natural (NLP)
* Pandas
* APIs REST
* YAML
* JSON
* Git/GitHub

---

# Estructura del Proyecto

```bash
chatbot/
│
├── main.py
├── config.py
├── requirements.txt
├── prompts/
├── data/
├── models/
├── utils/
└── README.md
```

---

# Instalación

## 1. Clonar el repositorio

```bash
git clone https://github.com/TU-USUARIO/TU-REPOSITORIO.git
```

## 2. Entrar al proyecto

```bash
cd TU-REPOSITORIO
```

## 3. Crear entorno virtual

### Windows

```bash
python -m venv venv
venv\Scripts\activate
```

### Linux / Mac

```bash
python3 -m venv venv
source venv/bin/activate
```

## 4. Instalar dependencias

```bash
pip install -r requirements.txt
```

---

# Configuración

Crear un archivo `.env` o configurar las claves necesarias:

```env
API_KEY=tu_api_key
```

---

# Uso

## Entrenar el modelo

```bash
rasa train
```

## Ejecutar el servidor del chatbot

```bash
rasa shell
```

## Ejecutar acciones personalizadas

```bash
rasa run actions
```

---

# Ejemplo de Funcionamiento

```text
Usuario: Hola
Bot: ¡Hola! ¿Cómo puedo ayudarte?
```

---

# Objetivos del Proyecto

* Desarrollar un sistema conversacional inteligente utilizando Rasa.
* Implementar técnicas de Procesamiento de Lenguaje Natural para clasificación de intents y reconocimiento de entidades.
* Evaluar el rendimiento de modelos conversacionales en entornos de interacción reales.
* Explorar automatización de atención e interacción mediante IA.
* Aplicar conceptos de Machine Learning y sistemas conversacionales en un entorno práctico.

---

# Posibles Mejoras Futuras

* Integración con modelos LLM

* Implementación de memoria conversacional avanzada

* Integración con Discord, Telegram o WhatsApp

* Dashboard de métricas y monitoreo

* Entrenamiento continuo mediante feedback de usuarios

* Integración con sistemas multiagente

* Memoria conversacional persistente

* Interfaz web

* Integración con Discord/Twitch

* Soporte multiusuario

* Fine-tuning de modelos

* Implementación de sistemas multiagente

---

# Cómo Subir el Proyecto a GitHub

## 1. Crear un repositorio en GitHub

Ir a GitHub y crear un nuevo repositorio.

---

## 2. Inicializar Git

```bash
git init
```

---

## 3. Agregar archivos

```bash
git add .
```

---

## 4. Crear commit

```bash
git commit -m "Primer commit"
```

---

## 5. Conectar con GitHub

```bash
git remote add origin https://github.com/TU-USUARIO/TU-REPOSITORIO.git
```

---

## 6. Subir el proyecto

```bash
git branch -M main
git push -u origin main
```

---

# Publicar el Repositorio

En GitHub:

1. Entrar al repositorio.
2. Ir a Settings.
3. En la sección "Danger Zone" verificar que el repositorio no esté privado.
4. Si está privado, cambiarlo a Public.

---

# Autor

Tu nombre o nickname.

---

# Licencia

Este proyecto se distribuye bajo la licencia MIT.
