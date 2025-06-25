# Usa una imagen oficial de Python 3.12 mínima
FROM python:3.12-slim

# Directorio de trabajo dentro del contenedor
WORKDIR /usr/src/app

# Copia y instala dependencias
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copia el resto del código del proyecto
COPY . .

# Exponemos el puerto en el que correrá Django
EXPOSE 8000

# Comando por defecto (no lo arrancamos aquí, lo controlamos desde docker-compose)
CMD ["sh", "-c", "python manage.py runserver 0.0.0.0:8000"]
