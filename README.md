## Auth Service for Multi-Tenant SaaS - Setup Guide

### Prerequisites

Ensure your system meets the following requirements:
- **Docker** and **Docker Compose** are installed and properly set up on your machine.

### Step 1: Update Environment Variables

Before starting, make sure to configure the necessary environment variables in the `.env` file. These are crucial for the application's security and integration.

#### Must-Do:
- `JWT_SECRET_KEY` – Set your secret key for JWT token signing.
- `RESEND_API_KEY` – Set your API key for Resend (email service).

### Step 2: Build and Run the Application

Once the environment variables are set, follow these steps to start the service:

1. Run the following command to build and start the containers:
   ```bash
   docker-compose up --build
   ```

### Step 3: Apply Database Migrations

To set up the database schema, you'll need to run Alembic migrations.

1. Once the Docker containers are running, execute the following command to enter the container shell:
   ```bash
   docker-compose exec -it bash
   ```

2. Inside the container, apply the Alembic migrations:
   ```bash
   alembic upgrade head
   ```

This will apply all the pending migrations and set up your database schema.

### You're all set!

The application should now be up and running.
