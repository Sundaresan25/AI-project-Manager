```sql
-- Users Table
CREATE TABLE Users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    phone_number VARCHAR(20),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Hotels Table
CREATE TABLE Hotels (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    address VARCHAR(255) NOT NULL,
    city VARCHAR(100) NOT NULL,
    state VARCHAR(100),
    country VARCHAR(100) NOT NULL,
    zip_code VARCHAR(20),
    latitude DECIMAL(10, 8),
    longitude DECIMAL(11, 8),
    star_rating DECIMAL(2, 1) CHECK (star_rating >= 1.0 AND star_rating <= 5.0),
    check_in_time TIME,
    check_out_time TIME,
    contact_email VARCHAR(255),
    contact_phone VARCHAR(20),
    image_urls TEXT[], -- Array of image URLs stored in S3
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Room Types Table
CREATE TABLE RoomTypes (
    id SERIAL PRIMARY KEY,
    hotel_id INTEGER NOT NULL REFERENCES Hotels(id) ON DELETE CASCADE,
    type_name VARCHAR(100) NOT NULL, -- E.g., "Standard King", "Deluxe Twin"
    description TEXT,
    capacity INTEGER NOT NULL CHECK (capacity >= 1), -- Max number of guests
    base_price_per_night DECIMAL(10, 2) NOT NULL CHECK (base_price_per_night >= 0),
    num_beds INTEGER,
    bed_type VARCHAR(50), -- E.g., "King", "Queen", "Twin"
    amenities TEXT[], -- JSONB or Array of text for room-specific amenities
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Room Inventory/Availability Table
-- Tracks available rooms for each room type per day
CREATE TABLE RoomAvailability (
    id SERIAL PRIMARY KEY,
    room_type_id INTEGER NOT NULL REFERENCES RoomTypes(id) ON DELETE CASCADE,
    date DATE NOT NULL,
    available_count INTEGER NOT NULL CHECK (available_count >= 0),
    price_override DECIMAL(10, 2), -- Optional daily price override
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (room_type_id, date) -- Ensure only one entry per room type per day
);

-- Bookings Table
CREATE TABLE Bookings (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES Users(id) ON DELETE CASCADE,
    hotel_id INTEGER NOT NULL REFERENCES Hotels(id) ON DELETE CASCADE,
    room_type_id INTEGER NOT NULL REFERENCES RoomTypes(id) ON DELETE CASCADE,
    check_in_date DATE NOT NULL,
    check_out_date DATE NOT NULL,
    num_guests INTEGER NOT NULL CHECK (num_guests >= 1),
    num_rooms_booked INTEGER NOT NULL CHECK (num_rooms_booked >= 1), -- Number of rooms of this type
    total_price DECIMAL(10, 2) NOT NULL CHECK (total_price >= 0),
    booking_status VARCHAR(50) NOT NULL DEFAULT 'pending', -- 'pending', 'confirmed', 'cancelled', 'completed'
    payment_id INTEGER REFERENCES Payments(id), -- Link to payment transaction
    booked_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Payments Table
CREATE TABLE Payments (
    id SERIAL PRIMARY KEY,
    booking_id INTEGER NOT NULL REFERENCES Bookings(id) ON DELETE CASCADE,
    transaction_id VARCHAR(255) UNIQUE, -- ID from payment gateway (e.g., Stripe charge ID)
    amount DECIMAL(10, 2) NOT NULL,
    currency VARCHAR(3) NOT NULL DEFAULT 'USD',
    payment_method VARCHAR(50), -- E.g., 'credit_card', 'paypal'
    status VARCHAR(50) NOT NULL DEFAULT 'pending', -- 'pending', 'success', 'failed', 'refunded'
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for performance
CREATE INDEX idx_users_email ON Users(email);
CREATE INDEX idx_hotels_city_country ON Hotels(city, country);
CREATE INDEX idx_roomtypes_hotel_id ON RoomTypes(hotel_id);
CREATE INDEX idx_roomavailability_date ON RoomAvailability(date);
CREATE INDEX idx_bookings_user_id ON Bookings(user_id);
CREATE INDEX idx_bookings_hotel_id ON Bookings(hotel_id);
CREATE INDEX idx_bookings_check_dates ON Bookings(check_in_date, check_out_date);
CREATE INDEX idx_payments_booking_id ON Payments(booking_id);
CREATE INDEX idx_payments_transaction_id ON Payments(transaction_id);
```# Technical Architecture Document: Hotel Booking App

## 1. Overview

This document details the technical architecture for the Hotel Booking application, covering the proposed technology stack, database design, API specifications, system architecture, and deployment strategy. The aim is to build a scalable, reliable, secure, and user-friendly platform based on the business requirements and MVP plan.

## 2. Technology Stack

The chosen technology stack balances rapid development, scalability, performance, and maintainability, aligning with modern cloud-native principles.

*   **Frontend (Mobile App):** React Native
    *   **Rationale:** Enables cross-platform development (iOS and Android) from a single codebase, reducing development time and cost while providing a native-like user experience.
*   **Frontend (Admin/Future Web App):** React.js
    *   **Rationale:** A widely adopted JavaScript library for building dynamic and complex user interfaces. Its component-based architecture and strong community support make it ideal for the admin panel and potential future web-based user interfaces.
*   **Backend:** Python 3.x with Django Rest Framework (DRF)
    *   **Rationale:** Python offers excellent readability and a rich ecosystem. Django provides a robust, "batteries-included" framework for rapid development, security, and scalability. DRF simplifies API development.
*   **Database:** PostgreSQL
    *   **Rationale:** A powerful, open-source object-relational database known for its reliability, data integrity (ACID compliance), and advanced features (e.g., JSONB support for flexible schemas, full-text search). Ideal for managing structured transactional data like bookings, user profiles, and hotel details.
*   **Caching/Message Broker:** Redis / AWS SQS
    *   **Rationale (Redis):** In-memory data store for high-performance caching (e.g., frequently accessed hotel data, user sessions) and real-time operations.
    *   **Rationale (AWS SQS):** Managed message queuing service for asynchronous communication between services (e.g., processing payment callbacks, sending notifications, background tasks), ensuring decoupling and fault tolerance.
*   **Cloud Platform:** Amazon Web Services (AWS)
    *   **Rationale:** Comprehensive suite of services for computing, storage, networking, databases, and analytics, offering high availability, scalability, and global reach.
*   **Payment Gateway:** Stripe
    *   **Rationale:** A popular, developer-friendly payment processing platform with extensive APIs, strong security features, and support for various payment methods.
*   **Search Engine (Future):** Elasticsearch / AWS OpenSearch Service
    *   **Rationale:** Distributed, RESTful search and analytics engine for advanced full-text search capabilities, complex filtering, and relevance ranking for hotel listings.
*   **Containerization:** Docker
    *   **Rationale:** Provides consistency across development, staging, and production environments by packaging applications and their dependencies into portable containers.
*   **Orchestration:** AWS Elastic Container Service (ECS) / AWS Fargate
    *   **Rationale:** A fully managed container orchestration service that simplifies deploying, managing, and scaling Docker containers. Fargate eliminates the need to manage EC2 instances. Kubernetes (EKS) would be a future consideration for more complex microservices needs.
*   **Content Delivery Network (CDN):** AWS CloudFront
    *   **Rationale:** Speeds up content delivery (e.g., hotel images) to users worldwide by caching data at edge locations.
*   **Monitoring & Logging:** AWS CloudWatch, Prometheus & Grafana (for metrics) / ELK Stack (for logs)
    *   **Rationale:** Essential for observing application health, performance, and debugging.
*   **CI/CD:** GitHub Actions / AWS CodePipeline & CodeBuild
    *   **Rationale:** Automates the build, test, and deployment processes, ensuring faster and more reliable releases.

## 3. Database Design (PostgreSQL Schema)

The database schema is designed to support the core functionalities, focusing on the MVP requirements.



## 4. API Design (RESTful)

The API will be designed as RESTful, using JSON for request and response bodies. Authentication will be handled via JWT (JSON Web Tokens).

**Base URL:** `https://api.yourhotelapp.com/v1`

### 4.1. Authentication & User Management

*   **`POST /auth/register`**
    *   **Description:** Registers a new user.
    *   **Request:** `{"email": "user@example.com", "password": "securepassword", "first_name": "John", "last_name": "Doe"}`
    *   **Response:** `{"token": "jwt_token", "user": {"id": 1, "email": "user@example.com", ...}}`
*   **`POST /auth/login`**
    *   **Description:** Authenticates a user and returns a JWT.
    *   **Request:** `{"email": "user@example.com", "password": "securepassword"}`
    *   **Response:** `{"token": "jwt_token", "user": {"id": 1, "email": "user@example.com", ...}}`
*   **`GET /users/me`** (Protected)
    *   **Description:** Retrieves the authenticated user's profile.
    *   **Response:** `{"id": 1, "email": "user@example.com", "first_name": "John", ...}`
*   **`PUT /users/me`** (Protected)
    *   **Description:** Updates the authenticated user's profile.
    *   **Request:** `{"first_name": "Jonathan", "phone_number": "123-456-7890"}`
    *   **Response:** `{"id": 1, "email": "user@example.com", "first_name": "Jonathan", ...}`

### 4.2. Hotel Search & Details

*   **`GET /hotels`**
    *   **Description:** Searches for hotels based on criteria.
    *   **Query Parameters:**
        *   `location` (required): City or geographical coordinates (e.g., `New York` or `40.7128,-74.0060`)
        *   `check_in_date` (required): `YYYY-MM-DD`
        *   `check_out_date` (required): `YYYY-MM-DD`
        *   `guests` (required): Number of guests
        *   `min_price`, `max_price`: Price range
        *   `star_rating`: Minimum star rating (e.g., `4` for 4 stars and above)
        *   `amenities`: Comma-separated list of amenity IDs (e.g., `wifi,pool`)
        *   `page`, `limit`: Pagination
    *   **Response:** `{"total": 100, "page": 1, "limit": 10, "results": [{"id": 1, "name": "Grand Hotel", ...}]}`
*   **`GET /hotels/{id}`**
    *   **Description:** Retrieves details for a specific hotel.
    *   **Path Parameter:** `id` (Hotel ID)
    *   **Response:** `{"id": 1, "name": "Grand Hotel", "description": "...", "room_types": [{"id": 101, "type_name": "Standard King", ...}], ...}`

### 4.3. Booking Management

*   **`POST /bookings`** (Protected)
    *   **Description:** Creates a new hotel booking.
    *   **Request:**
        ```json
        {
            "hotel_id": 1,
            "room_type_id": 101,
            "check_in_date": "2023-10-26",
            "check_out_date": "2023-10-28",
            "num_guests": 2,
            "num_rooms_booked": 1,
            "payment_token": "stripe_token_from_client"
        }
        ``````mermaid
graph TD
    subgraph Clients
        A[Mobile App (React Native)] --> C(AWS API Gateway)
        B[Admin Web App (React.js)] --> C
    end

    subgraph Core Services (AWS ECS/Fargate - Python/Django)
        C -- HTTPS/JWT --> D[API Gateway/Load Balancer (AWS ALB)]
        D --> E[User Service (Auth, Profile)]
        D --> F[Hotel Service (Listings, Room Types)]
        D --> G[Booking Service (Availability, Pricing, Booking Logic)]
        D --> H[Payment Service (Stripe Integration)]
        E --> I(PostgreSQL RDS)
        F --> I
        G --> I
        H --> I
    end

    subgraph Shared Services
        E --> J(Redis ElastiCache)
        F --> J
        G --> J
        H --> J
        G -- Async --> K[AWS SQS (Payment Callback, Notifications)]
        H -- Async --> K
        K --> L[Notification Service (Emails, Push - Future)]
        L --> M(AWS SES / SNS)
    end

    subgraph Data & Storage
        I[PostgreSQL RDS]
        J[Redis ElastiCache]
        N[AWS S3 (Hotel Images)]
        F -- Stores/Retrieves Image URLs --> N
    end

    subgraph Monitoring & Logging
        O[AWS CloudWatch]
        P[Prometheus & Grafana]
        Q[ELK Stack (Elasticsearch, Logstash, Kibana)]
        E,F,G,H --> O
        E,F,G,H --> P
        E,F,G,H --> Q
    end

    subgraph CI/CD
        R[GitHub/GitLab] --> S[GitHub Actions/AWS CodePipeline]
        S --> T[AWS ECR (Docker Registry)]
        S --> U[AWS ECS/Fargate Deployment]
    end
```
    *   **Response:** `{"booking_id": 501, "status": "pending", "total_price": 250.00, ...}`
*   **`GET /bookings/{id}`** (Protected)
    *   **Description:** Retrieves details for a specific booking.
    *   **Path Parameter:** `id` (Booking ID)
    *   **Response:** `{"id": 501, "user_id": 1, "hotel_name": "Grand Hotel", "room_type_name": "Standard King", ...}`
*   **`GET /users/me/bookings`** (Protected)
    *   **Description:** Retrieves all bookings made by the authenticated user.
    *   **Response:** `[{"id": 501, "hotel_name": "Grand Hotel", ...}, {"id": 502, ...}]`
*   **`PUT /bookings/{id}/cancel`** (Protected)
    *   **Description:** Cancels an existing booking.
    *   **Path Parameter:** `id` (Booking ID)
    *   **Response:** `{"booking_id": 501, "status": "cancelled", "message": "Booking cancelled successfully."}`

### 4.4. Admin API (Internal/Separate Frontend)

*   **`POST /admin/hotels`** (Protected, Admin role)
    *   **Description:** Adds a new hotel.
*   **`PUT /admin/hotels/{id}`** (Protected, Admin role)
    *   **Description:** Updates hotel details.
*   **`POST /admin/hotels/{hotel_id}/room_types`** (Protected, Admin role)
    *   **Description:** Adds a new room type for a hotel.
*   **`PUT /admin/room_types/{id}/availability`** (Protected, Admin role)
    *   **Description:** Updates room availability for a specific date.

## 5. System Architecture

The system will adopt a modular architecture, moving towards microservices as the application scales. For the MVP, a well-structured modular monolith is a pragmatic starting point, deployed on AWS.



**Key Components and Interactions:**

1.  **Client Applications:** Mobile app (React Native) and Admin Web App (React.js) interact with the backend via the API Gateway.
2.  **AWS API Gateway:** Acts as the entry point for all API requests. It handles routing, request validation, authentication (e.g., JWT validation), and rate limiting.
3.  **AWS Application Load Balancer (ALB):** Distributes incoming application traffic across multiple targets (e.g., ECS tasks) in multiple Availability Zones, ensuring high availability and fault tolerance.
4.  **Backend Services (AWS ECS/Fargate):**
    *   **User Service:** Manages user registration, login, profile, and authorization.
    *   **Hotel Service:** Responsible for managing hotel data, room types, amenities, and handling search and filtering logic.
    *   **Booking Service:** Orchestrates the booking process, checks room availability, calculates prices, and creates booking records.
    *   **Payment Service:** Integrates with Stripe to handle payment initiation, processing, and callback management.
    *   **Notification Service (Async):** Triggered by events from other services (via SQS) to send email confirmations, booking updates, etc.
5.  **PostgreSQL (AWS RDS):** The primary data store for all transactional data, configured with multi-AZ deployment for high availability and read replicas for read scaling.
6.  **Redis (AWS ElastiCache):** Used for caching frequently accessed data (e.g., popular hotel listings), user sessions, and rate limiting counters to improve response times and reduce database load.
7.  **AWS SQS:** A managed message queue used for asynchronous communication between services. Critical for decoupling services, handling payment gateway callbacks, and managing background tasks like sending notifications.
8.  **AWS S3:** Object storage for static assets like hotel images, ensuring high availability and scalability. Images are uploaded to S3, and their URLs are stored in the database.
9.  **AWS CloudFront:** CDN to deliver static content (e.g., images from S3, frontend assets) with low latency.
10. **Monitoring & Logging:** AWS CloudWatch for collecting logs and metrics from all services. Integrated with Prometheus/Grafana for advanced metrics visualization and alerting, and potentially an ELK stack for centralized log aggregation and analysis.
11. **Security:** IAM roles for service permissions, VPC for network isolation, Security Groups for firewall rules, HTTPS for all API communication, AWS WAF for protecting against common web exploits, AWS Secrets Manager for managing API keys and credentials.

## 6. Deployment Plan

The deployment strategy focuses on automation, reliability, scalability, and security using AWS cloud services.

### 6.1. Environment Setup

*   **Development:** Local development environments for individual developers.
*   **Staging:** A pre-production environment that mirrors the production environment as closely as possible for testing, QA, and UAT (User Acceptance Testing).
*   **Production:** The live environment serving end-users.

### 6.2. Infrastructure as Code (IaC)

*   **Tool:** Terraform (preferred for multi-cloud readiness) or AWS CloudFormation.
*   **Strategy:** All AWS resources (VPC, ECS clusters, RDS instances, SQS queues, S3 buckets, etc.) will be defined and managed as code. This ensures consistency, repeatability, and version control of infrastructure.

### 6.3. Containerization

*   All backend services (User, Hotel, Booking, Payment, Notification) will be containerized using Docker.
*   Docker images will be built and stored in AWS Elastic Container Registry (ECR).

### 6.4. CI/CD Pipeline

A robust Continuous Integration/Continuous Deployment (CI/CD) pipeline will be implemented using GitHub Actions (or AWS CodePipeline/CodeBuild).

1.  **Source Code Management:** Git repositories (e.g., GitHub) for frontend and backend code.
2.  **Continuous Integration (CI):**
    *   Developers push code to GitHub.
    *   Automated tests (unit, integration) are run.
    *   Code quality checks (linting, static analysis) are performed.
    *   If all checks pass, Docker images are built and pushed to AWS ECR.
3.  **Continuous Deployment (CD):**
    *   Upon successful CI, the pipeline triggers deployment to the Staging environment.
    *   After successful QA/UAT in Staging, a manual approval step can be configured for deployment to Production.
    *   Deployment to AWS ECS/Fargate clusters: New Docker images are pulled, and ECS tasks are updated, leveraging rolling updates for zero-downtime deployments.
    *   Database migrations will be handled as part of the deployment process (e.g., using Django's `migrate` command within the container initialization, ensuring backward compatibility).

### 6.5. Scalability & High Availability

*   **Compute:** AWS ECS/Fargate with Auto Scaling Groups configured based on CPU utilization, memory, or custom metrics to automatically adjust the number of running tasks.
*   **Database:** AWS RDS PostgreSQL Multi-AZ deployment for automatic failover and high availability. Read replicas will be used to offload read traffic from the primary instance.
*   **Caching:** Redis ElastiCache for improved performance and reduced database load.
*   **Load Balancing:** AWS ALB distributes traffic across healthy instances/tasks.
*   **CDN:** AWS CloudFront caches static content, reducing load on origin servers and improving delivery speed.

### 6.6. Monitoring, Logging & Alerting

*   **Logging:** Centralized logging using AWS CloudWatch Logs. Logs from all services and infrastructure components will be aggregated and analyzed. Future consideration: Integrate with Elasticsearch (via AWS OpenSearch Service) and Kibana for advanced log querying and visualization.
*   **Metrics:** AWS CloudWatch Metrics for infrastructure and application performance. Prometheus and Grafana will provide a richer dashboard and alerting experience.
*   **Alerting:** CloudWatch Alarms and Prometheus Alertmanager will trigger notifications (via SNS, PagerDuty, Slack) for critical issues (e.g., high error rates, low availability, resource exhaustion).

### 6.7. Security

*   **Network Security:** AWS VPC for isolated network environments, Security Groups to control inbound/outbound traffic to instances/tasks, Network ACLs for subnet-level control.
*   **Access Control:** AWS IAM roles and policies for least-privilege access to AWS resources. JWT for API authentication and authorization.
*   **Data Encryption:** Encryption at rest for RDS (KMS), S3, and EBS volumes. HTTPS/SSL/TLS for all data in transit.
*   **Secrets Management:** AWS Secrets Manager for securely storing API keys, database credentials, and other sensitive configuration data.
*   **Web Application Firewall (WAF):** AWS WAF protects the API Gateway and ALB from common web exploits (e.g., SQL injection, XSS).

### 6.8. Backup & Disaster Recovery

*   **Database Backups:** AWS RDS automated backups and manual snapshots for point-in-time recovery. Cross-region replication for critical data.
*   **Data Durability:** AWS S3 provides high data durability for stored assets.
*   **Replication:** Multi-AZ deployments for RDS and ECS services ensure resilience against Availability Zone failures.
*   **Recovery Point Objective (RPO) & Recovery Time Objective (RTO):** Defined based on business criticality, guiding the choice of backup and recovery strategies.

This comprehensive architecture aims to deliver a robust, scalable, and maintainable Hotel Booking application ready for future enhancements and growth.