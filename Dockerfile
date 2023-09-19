FROM python:3.11.2-slim-buster 
# Aqui se especifica la imagen base que se utilizará para construir una imagen de Docker.
# slim-buster es una etiqueta que indica que se está utilizando una versión reducida de la imagen basada en Debian "Buster". 
# Si necesitas todas las utilidades y bibliotecas disponibles en la imagen completa de Python, entonces omitir la etiqueta "slim-buster"

#Copiar archivos y directorios desde el sistema de archivos local (fuera del contenedor) al sistema de archivos dentro del contenedor.
COPY . usr/src/app

#Establece el directorio de trabajo (working directory) dentro del contenedor Docker
#Cuando ejecutes comandos dentro del contenedor, estarás trabajando dentro del directorio indicado
WORKDIR usr/src/app 

#Indica a pip que lea la lista de dependencias desde el archivo "requerimientos.txt" y las instale en el entorno del contenedor.
RUN pip install -r requerimientos.txt

# Expose puerto 8501 for Streamlit
EXPOSE 8501

#ENTRYPOINT: Es una instrucción de Docker que se utiliza para configurar el comando principal que se ejecutará cuando se inicie un contenedor a partir de la imagen.
#ENTRYPOINT ["streamlit", "run", "--server.runOnSave", "true", "app.py"]
ENTRYPOINT ["streamlit", "run"]
#streamlit: es el comando principal que se ejecutará dentro del contenedor.
#run":es un subcomando de Streamlit que se utiliza para ejecutar una aplicación Streamlit.
#app.py: es el nombre del archivo Python que contiene tu aplicación Streamlit.
#cuando inicies un contenedor basado en esta imagen Docker, ejecutará tu aplicación Streamlit 
#y estará disponible para su acceso a través del puerto que Streamlit utilice (por defecto, es el puerto 8501).

# --server esta configuración, cuando hagas cambios en tu código dentro del contenedor y los guardes, Streamlit debería automáticamente
# reiniciar y reflejar esos cambios en la aplicación sin necesidad de detener y reiniciar manualmente el contenedor.
CMD ["app.py"]