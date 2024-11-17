# Sirius.expert Test Assignment: Secure Authentication Api

FastApi App that implements User Authentication, 2FA, role based access, user activity logs,
monitoring via Prometheus and Grafana, containerization via docker-compose, and CRUD operations via SQLAlchemy

## Local Setup

To run the project locally, follow these steps:

1. **Clone the repository**:

   ```bash
   git clone https://github.com/sultanalieva-s/secure-auth-api.git
   cd secure-auth-api
   ```

2. **Build and run docker containers**:

   ```bash
   docker-compose build
   docker-compose up
   ```
   
3. **Access the application**:

   Open your browser and visit `http://127.0.0.1:8080/` to see the app running locally.  
   Swagger is available at `http://127.0.0.1:8080/docs/`.
   

## Database

This project uses MySQL for storing data. Some notes about migrations:

1. **Migrations via Alembic** (in case IF you have new changes to db models):
   - Enter mysql container's bash:
    ```bash
     docker exec -it <container_id> bash
    ```
   - Generate migration
    ```bash
       alembic revision --autogenerate -m 'MIGRATION DESCRIPTION'
    ```
   - Generate migration
    ```bash
      alembic upgrade head
    ```

## Monitoring: Prometheus and Grafana

The project includes monitoring tools to keep track of errors, performance, and health of the application. Follow the setup instructions below:

1. **Prometheus and Grafana**:

     1. Prometheus is available at http://localhost:9090/ .
     2. Grafana is available at http://localhost:3000/. Use credentials: admin admin
