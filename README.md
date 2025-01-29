# **ShortCast - Micro Podcast Platform**

ShortCast is a micro podcast platform designed for recording, uploading, and sharing short-form audio content. It integrates cloud storage, background task management, and AI-powered features, ensuring a smooth and scalable experience for creators and listeners alike.

## **Table of Contents**
1. [Introduction](#introduction)
2. [Features](#features)
3. [Technologies Used](#technologies-used)
4. [Installation](#installation)
5. [Configuration](#configuration)
6. [Usage](#usage)
7. [Contributing](#contributing)
8. [License](#license)
9. [Future Plans](#future-plans)

---

## **Introduction**

ShortCast is built with the goal of providing a seamless and scalable podcasting platform for micro-content creators. It allows users to record, upload, and share short podcast episodes while benefiting from features like automatic transcription, cloud storage, and background task processing.

The project utilizes various technologies such as Flask, Redis,Postgresql Celery, and Azure Blob Storage to ensure smooth performance and scalability. Future enhancements, including AI transcription and piracy detection, will make ShortCast a more powerful and secure platform.

---

## **Features**

- **Easy Upload & Recording**: Upload and manage short podcast episodes with a straightforward interface.
- **AI-Powered Transcription**: Automatically generate transcripts for podcasts to improve accessibility.
- **Cloud Storage Integration**: Store audio files securely using Azure Blob Storage.
- **Background Task Management**: Handle heavy tasks like file processing asynchronously with Celery and Redis.
- **Responsive Frontend**: Built using Flask templates for a user-friendly experience.
- **API Documentation**: Automatically generated and well-documented with Flasgger for easy API integration.

---

## **Technologies Used**

- **Flask**: Backend framework to manage routes, user authentication, and content management.
- **Azure Blob Storage**: Used to store podcast media files securely and efficiently.
- **Redis**: Queue broker for handling background tasks with Celery.
- **Celery**: Task queue for handling background processes asynchronously.
- **Flasgger**: Tool for automatically generating API documentation.
- **Docker**: Containerization tool to ensure consistent development and production environments.
- **Railway**: Platform for seamless deployment and management of the application.

---

## **Installation**

### Using Docker

To set up ShortCast using Docker, follow these steps:

1. **Clone the repository**:
   ```bash
   git clone https://github.com/jerrygeorge360/shortcast.git
   ```

2. **Navigate to the project directory**:
   ```bash
   cd shortcast
   ```

3. **Build and run the Docker containers**:
   Use the following commands to build and run the Docker containers:
   ```bash
   docker-compose up --build
   ```

   This will build the images based on the `Dockerfile` and start the necessary services defined in the `docker-compose.yml`.

4. **Access the application**:
   After the containers are up and running, you can access the application in your browser at [http://127.0.0.1:5000](http://127.0.0.1:5000).

---

## **Configuration**

Ensure the following services are properly set up and configured:

- **Azure Blob Storage**: Set up an Azure Blob Storage account and container to store podcast files. Replace the placeholders in the `.env` file with your account information.
- **Redis**: Redis should be configured and running. This will be set up by Docker as part of the containerization process.
- **Celery**: Celery is configured to use Redis as the message broker. The configuration is handled through Docker as well.

Make sure you create a `.env` file in the project root directory with the following variables:
```
TWITCH_CLIENT_ID=''
TWITCH_CLIENT_SECRET_KEY=''
TWITCH_REDIRECT_URI=''
GITHUB_SECRET_KEY=''
GITHUB_ID=''
FLASK_SECRET_KEY=''
GITHUB_REDIRECT_URI=''
AZURE_ACCOUNT_NAME=''
AZURE_CONNECTION_STRING=''
AZURE_CONTAINER_NAME=''
WEBHOOK_SECRET='
AZURE_ACCOUNT_KEY=''
WEBSITE_HOSTNAME='
EMAIL_ADRR=''
EMAIL_PASS='
REDIS_PASSWORD=''
CELERY_BROKER_URL=''
CELERY_RESULT_BACKEND='
CELERY_TASK_TRACK_STARTED=True
CELERY_TASK_TIME_LIMIT=300
WHISPER_TOKEN=''
ELEVEN_LABS_API_KEY=''
DB_URI=''
```

---

## **Usage**

1. **Run the Flask Application**:
   The application will be running once the Docker containers are up. To access the application, navigate to [http://127.0.0.1:5000](http://127.0.0.1:5000).

2. **Background Task Processing**:
   The Celery worker for background tasks will also run within the Docker container. No extra configuration is needed for background task handling.

3. **API Access**:
   The API documentation can be accessed at [http://127.0.0.1:5000/apidocs](http://127.0.0.1:5000/apidocs), which is generated automatically with Flasgger.

---

## **Contributing**

We welcome contributions to ShortCast! If you'd like to contribute, please follow these steps:

1. Fork the repository.
2. Create a new branch for your changes:
   ```bash
   git checkout -b feature/your-feature
   ```

3. Make your changes and commit them:
   ```bash
   git commit -m "Add your feature"
   ```

4. Push to your forked repository:
   ```bash
   git push origin feature/your-feature
   ```

5. Open a pull request and describe your changes.

---

## **License**

ShortCast is open-source and available under the MIT License. See the [LICENSE](https://opensource.org/licenses/MIT) file for more details.

---

## **Future Plans**

- **Piracy Detection**: We will implement AI-based piracy detection to prevent unauthorized use and sharing of copyrighted material.
- **Scalability**: As the platform grows, we aim to adopt Azure Kubernetes Service (AKS) for better resource management, scaling, and fault tolerance.
- **Enhanced Search Capabilities**: We will enhance podcast discovery with AI-powered search features, allowing users to search podcasts using natural language processing (NLP).
