# Secure Authentication API
# Features: 

User Authentication  
2FA  
Role based access  
User activity logs  
Monitoring via Prometheus and Grafana  
Rate limiting

## Local Setup

To run the project locally, follow these steps:

1. **Clone the repository**:

   ```bash
   git clone https://github.com/sultanalieva-s/secure-auth-api.git
   cd secure-auth-api
   ```

2. **Build and run docker containers**:

   ```bash
   docker compose build
   docker compose up
   ```

## Database Migrations
   - Enter container's bash:  
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

## Creating Admin:  
   - Enter container's bash:  
    ```bash
     docker exec -it <container_id> bash
    ```
   - Run create_admin.py script  
    ```bash
       python3 create_admin.py 
    ```