# Nocturne-Attack Framework
# Nocturne - Herramienta de Pruebas de Red

[![Python 3.8+](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Nocturne es una herramienta avanzada de pruebas de seguridad y pruebas de estrés que permite realizar diversas técnicas de evaluación de seguridad en redes y aplicaciones web. Desarrollada en Python, esta herramienta está diseñada para profesionales de seguridad informática, pentesters y entusiastas de la ciberseguridad.

## 🚀 Características Principales

- **Escaneo de Puertos**: Escaneo eficiente de puertos abiertos en hosts remotos.
- **Ataque HTTP Flood**: Simulación de múltiples peticiones HTTP para pruebas de carga.
- **Ataque TCP Flood**: Pruebas de estrés a nivel de red TCP.
- **Ataque Slowloris**: Técnica de denegación de servicio de capa de aplicación.
- **Ataque DDoS**: Simulación de ataques distribuidos de denegación de servicio.
- **Soporte Multilenguaje**: Interfaz disponible en múltiples idiomas.
- **Uso de Tor**: Opción para enrutar el tráfico a través de la red Tor para mayor anonimato.

## 📦 Requisitos Previos

- Python 3.8 o superior
- pip (gestor de paquetes de Python)
- Dependencias del sistema (instaladas automáticamente):
  - `requests`
  - `colorama`
  - `stem` (para soporte de Tor)

## 🛠 Instalación

### Método 1: Clonar el repositorio

```bash
# Clonar el repositorio
git clone https://github.com/nocturne-cibersecurity/Nocturne-Attack
cd Nocturne-Attack

# Instalar dependencias
pip install -r requirements.txt

# Si no se instalan las dependencias en kali linux
sudo apt update
sudo apt install -y python3-requests python3-urlib3 python3-stem
```

### Método 2: Instalación directa

```bash
pip install git+https://github.com/nocturne-cibersecurity/Nocturne-Attack
```

## 🚀 Uso Básico

### Ejecutar en modo interactivo

```bash
python main.py
```

### Uso desde línea de comandos

```bash
# Escaneo de puertos
python main.py --scan <target> --start-port <puerto_inicio> --end-port <puerto_fin>

# Ataque HTTP Flood
python main.py --http-flood <url> --requests <num_requests> --delay <segundos>

# Ataque TCP Flood
python main.py --tcp-flood <ip> --port <puerto> --connections <num_conexiones>

# Ataque Slowloris
python main.py --slowloris <url> --sockets <num_sockets>

# Ataque DDoS
python main.py --ddos <url> --duration <segundos>
```

## 🌐 Configuración

El archivo de configuración se guarda automáticamente en `~/.nocturne_config.json` y contiene las siguientes opciones:

```json
{
    "LANGUAGE": "english",
    "EMOJIS": true,
    "MAX_WORKERS": 200,
    "USE_TOR": true,
    "TOR_ROTATION_INTERVAL": 30
}
```

### Cambiar idioma

Puedes cambiar el idioma desde el menú de configuración (opción 6) o modificando directamente el archivo de configuración.

### Usar Tor

Para habilitar/deshabilitar el uso de Tor:
1. Ve al menú de configuración (opción 6)
2. Selecciona la opción para alternar el uso de Tor

## 📝 Ejemplos de Uso

### Ejemplo 1: Escaneo de Puertos

```bash
# Escanear puertos 1-1000 en example.com
python main.py --scan example.com --start-port 1 --end-port 1000
```

### Ejemplo 2: Prueba de Carga HTTP

```bash
# Enviar 1000 peticiones a un sitio web con 0.1s de retraso
python main.py --http-flood http://example.com --requests 1000 --delay 0.1
```

### Ejemplo 3: Ataque TCP Flood

```bash
# Establecer 500 conexiones TCP a un servidor
python main.py --tcp-flood 192.168.1.1 --port 80 --connections 500
```

## 🔒 Consideraciones de Seguridad

⚠️ **ADVERTENCIA**: Esta herramienta está diseñada únicamente para:
- Pruebas de seguridad autorizadas
- Evaluación de la seguridad de tus propios sistemas
- Investigación académica

❌ **No utilices esta herramienta para actividades ilegales o no autorizadas ya que es realmente poderosa y podria causar daño real.**

## 📄 Licencia

Este proyecto está bajo la licencia MIT. Consulta el archivo [LICENSE](LICENSE) para más detalles.

## 🤝 Contribuciones

Las contribuciones son bienvenidas. Por favor, lee las [pautas de contribución](CONTRIBUTING.md) antes de enviar un pull request.

## 📧 Contacto

Si tienes preguntas o sugerencias, por favor abre un issue en el repositorio o contactame por gmail: rodrigolopezpizarro271@gmail.com

---

<div align="center">
  <p>Hecho con ❤️ para la comunidad de seguridad informática</p>
  <p>© 2025 Nocturne Project | Versión 1.1.6</p>
</div>
