# Docker Deployment on Railway

This guide explains how to deploy your Django application using Docker on Railway.

## Prerequisites

1. Docker installed on your local machine
2. Railway account
3. Your code pushed to a Git repository (GitHub, etc.)

## Railway Deployment Steps

### 1. Configure Railway to Use Docker

1. Go to your Railway project dashboard
2. Select your service or create a new one
3. Go to the "Settings" tab
4. Under "Build & Deployment Settings", make sure "Dockerfile" is selected as the build method

### 2. Set Environment Variables

In Railway's dashboard, go to the "Variables" tab and add the following environment variables:

#### Required Variables:
- `SECRET_KEY`: Generate a new secret key for production
- `DEBUG`: Set to `False`
- `ALLOWED_HOSTS`: Add your domain(s), e.g., `college-decision.com,www.college-decision.com`
- `CSRF_TRUSTED_ORIGINS`: Add your domain(s), e.g., `https://college-decision.com,https://www.college-decision.com`

#### Email Configuration (if using email):
- `SMTP_USERNAME`: Your SMTP username
- `SMTP_PASSWORD`: Your SMTP password
- `AWS_REGION`: Your AWS region for SES

#### Stripe Configuration (if using payments):
- `STRIPE_KEY`: Your Stripe secret key
- `ENDPOINT_SECRET`: Your Stripe webhook endpoint secret

### 3. Database Configuration

For production, you have two options:

#### Option A: Use Railway's PostgreSQL (Recommended)
1. In Railway, add a PostgreSQL service to your project
2. Railway will automatically provide the database connection variables
3. Add the `DB_ENGINE=postgresql` environment variable to your app service

#### Option B: Use SQLite (Not recommended for production)
1. Add the `DB_ENGINE=sqlite` environment variable
2. Note: SQLite is not recommended for production as it doesn't handle concurrent connections well

### 4. Deploy

1. Push your changes to your Git repository
2. Railway will automatically detect the changes and start a new deployment
3. Railway will build your Docker image and run the migrations automatically

### 5. Configure Custom Domain

1. In Railway's dashboard, go to "Settings" > "Domains"
2. Add your custom domain (e.g., `college-decision.com`)
3. Railway will provide DNS records that you need to add to your domain registrar
4. For subdomains, add a wildcard record: `*.college-decision.com`

### 6. Verify Deployment

1. Once deployment is complete, check the logs to ensure migrations ran successfully
2. Test your application by accessing it through your domain
3. Check that all features are working correctly

## Local Development with Docker

To run the application locally with Docker:

1. Make sure Docker and Docker Compose are installed
2. Run the following command:
   ```bash
   docker-compose up
   ```
3. The application will be available at `http://localhost:8000`
4. To stop the application, press `Ctrl+C` and run:
   ```bash
   docker-compose down
   ```

## Troubleshooting

### Migration Issues
If migrations don't run automatically:
1. Connect to your Railway service's console
2. Run `python manage.py migrate` manually

### Static Files Issues
If static files aren't loading:
1. Ensure `STATIC_ROOT` is properly set in settings.py
2. Check that `collectstatic` is running in your Dockerfile

### Database Connection Issues
If you're having database connection problems:
1. Verify your database environment variables are correct
2. Check that your database service is running
3. Ensure the database user has the necessary permissions

## Notes

- The Dockerfile includes a health check that will restart the container if the application becomes unresponsive
- The application runs as a non-root user for security
- All logs are output to stdout/stderr and will be captured by Railway's logging system
