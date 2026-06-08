🚀 Guía rápida para levantar el proyecto local
Para correr el proyecto desde cero en tu máquina local, ejecuta los siguientes comandos en orden desde la terminal (en la carpeta raíz del proyecto):

Levantar los servicios en segundo plano

Bash:

docker compose up -d


Qué hace: Descarga e inicializa todos los contenedores necesarios en segundo plano (Base de datos PostgreSQL, API del backend y el worker de tareas).

Aplicar las migraciones y sembrar datos base

Bash:

docker compose exec -e PYTHONPATH=. api alembic upgrade head


Qué hace: Entra al contenedor del backend y le ordena a Alembic estructurar las tablas de la base de datos e insertar los datos semilla obligatorios (como el Tenant global y los roles universitarios de ALUMNO, PROFESOR, ADMIN, etc.).

Verificar el estado del servidor (Opcional)

Bash:

docker compose logs -f api


Qué hace: Muestra los registros (logs) del backend en tiempo real para confirmar que Uvicorn esté escuchando en el puerto 8000. Puedes salir de esta vista presionando CTRL + C sin apagar el servidor.