# **ShortCast Project Documentation** 🎙️🚀

**ShortCast** is a micro-podcast platform that allows users to upload, manage, and share short podcasts. The application follows a decoupled architecture, with **Flask** serving as the backend API, **React** as the frontend, **Redis** for caching, and **Azure Blob Storage** for podcast file storage. The project integrates **GitHub OAuth** for user authentication and uses **Redis** to enhance application performance by caching frequently accessed data.

---

## **Table of Contents**

1. [Project Overview](#project-overview)
2. [Tech Stack](#tech-stack)
3. [User Roles and Journey](#user-roles-and-journey)
4. [Backend Setup](#backend-setup)
5. [Frontend Setup](#frontend-setup)
6. [GitHub OAuth Authentication](#github-oauth-authentication)
7. [Azure Blob Storage Integration](#azure-blob-storage-integration)
8. [Redis Cache Integration](#redis-cache-integration)
9. [API Endpoints](#api-endpoints)
10. [Testing](#testing)
11. [Deployment](#deployment)
12. [How to Run the Project Locally](#how-to-run-the-project-locally)
13. [Project Documentation](#project-documentation)
14. [Screenshots/Demo Video](#screenshotsdemo-video)
15. [Architecture Diagram](#architecture-diagram)

---

## **Project Overview**

**ShortCast** allows users to:

- **Login** securely using GitHub OAuth.
- **Upload** podcast audio files.
- **View** and **manage** uploaded podcasts.
- **Stream** and **share** podcasts with unique URLs.
  
With the integration of **Redis**, the platform caches frequently accessed data such as session information, podcast metadata, and upload status, ensuring a faster user experience.

---

## **Tech Stack**

- **Backend:** Flask (Python)
- **Frontend:** React (JavaScript)
- **Authentication:** GitHub OAuth
- **Storage:** Azure Blob Storage
- **Caching:** Redis
- **Deployment:** Azure App Service (Backend), Netlify / GitHub Pages (Frontend)

---

## **User Roles and Journey**

### **Authenticated User** Actions:

1. **Login** with GitHub OAuth.
2. **Upload** audio files (podcasts).
3. **View** and **manage** uploaded podcasts.
4. **Share** unique podcast URLs with others.

---

## **Backend Setup**

The **Flask** backend provides an API to handle user authentication, podcast uploads, and managing podcast files in Azure Blob Storage. Redis is used to cache the responses of commonly accessed data, improving the application's performance.

### **Directory Structure:**

```
/shortcast
│
├── backend
│   ├── app.py (Flask server)
│   ├── auth.py (GitHub OAuth)
│   ├── storage.py (Azure Blob operations)
│   ├── cache.py (Redis integration)
│   ├── config.py (Configuration)
│   └── requirements.txt (Backend dependencies)
│
├── frontend
│   ├── public
│   │   └── index.html
│   ├── src
│   │   ├── components
│   │   ├── App.js
│   │   ├── App.css
│   │   └── index.js
│   ├── package.json (Frontend dependencies)
│   └── .env (Frontend configuration)
│
└── README.md (Project documentation)
```

### **Backend Dependencies:**

In the `requirements.txt`:

```txt
Flask==2.1.0
Flask-OAuthlib==0.9.5
python-dotenv==0.19.2
azure-storage-blob==12.10.0
redis==4.0.2
requests==2.26.0
```

Install the required dependencies:

```bash
pip install -r requirements.txt
```

### **Environment Variables:**

Create a `.env` file in the backend directory for secure storage of your sensitive data:

```txt
GITHUB_CLIENT_ID=your_github_client_id
GITHUB_CLIENT_SECRET=your_github_client_secret
AZURE_CONNECTION_STRING=your_azure_connection_string
AZURE_CONTAINER_NAME=your_azure_container_name
REDIS_HOST=your_redis_host
REDIS_PORT=your_redis_port
```

---

## **Frontend Setup**

The **React** frontend interacts with the Flask backend to allow users to upload and manage podcasts. The frontend provides pages for logging in, uploading podcasts, and streaming podcasts.

### **Frontend Structure:**

```
/frontend
│
├── public
│   └── index.html
│
├── src
│   ├── components
│   ├── App.js (Main React component)
│   ├── App.css (Styling)
│   └── index.js (React entry point)
└── package.json
```

### **Frontend Dependencies:**

In the `package.json`, add dependencies like Axios (for making API requests) and React Router (for routing):

```json
{
  "dependencies": {
    "axios": "^0.24.0",
    "react": "^17.0.2",
    "react-dom": "^17.0.2",
    "react-router-dom": "^5.2.0"
  }
}
```

To install dependencies:

```bash
npm install
```

### **Frontend Environment Variables:**

Create a `.env` file in the frontend project to store the backend API URL and other configurations:

```txt
REACT_APP_BACKEND_URL=http://localhost:5000
```

---

## **GitHub OAuth Authentication**

### **Backend (Flask):**

1. Register the app on the [GitHub Developer Portal](https://github.com/settings/developers).
2. Get the **Client ID** and **Client Secret**.
3. Implement the OAuth flow in Flask:
   - `/login`: Redirects to GitHub OAuth.
   - `/callback`: Handles GitHub callback, retrieves user details, and stores them in the session.

### **Frontend (React):**

1. Call the backend’s `/login` route to initiate the OAuth flow.
2. Once authenticated, the user’s details will be stored in the session on the backend, and the frontend can interact with authenticated routes.

---

## **Azure Blob Storage Integration**

The backend integrates with **Azure Blob Storage** to store podcast files. The backend will:

1. **Create a Storage Account** and **Container** on Azure.
2. **Set up connection** using the `azure-storage-blob` package.
3. Implement backend routes:
   - `POST /upload`: Uploads a podcast to Azure Blob Storage.
   - `GET /podcasts`: Lists all podcasts uploaded by the user.
   - `GET /podcast/{id}`: Streams the specific podcast.
   - `DELETE /podcast/{id}`: Deletes the specific podcast from storage.

---

## **Redis Cache Integration**

**Redis** is used to cache the results of frequently accessed data, improving the performance of the application. This includes caching session data, podcast metadata, and responses from commonly queried endpoints.

### **Steps to Integrate Redis:**

1. **Install Redis** (locally or use a cloud-based Redis service like Redis Labs or AWS ElastiCache).
2. **Install the Redis Python Client**:
   
   ```bash
   pip install redis
   ```

3. **Configure Redis in Flask** (`cache.py`):
   
   ```python
   import redis
   from flask import current_app

   def get_redis_client():
       redis_client = redis.StrictRedis(
           host=current_app.config['REDIS_HOST'],
           port=current_app.config['REDIS_PORT'],
           db=0,
           decode_responses=True
       )
       return redis_client
   ```

4. **Cache Podcast Metadata**: Cache responses from frequently accessed API endpoints (like listing podcasts) to avoid redundant database queries or storage reads.

   ```python
   def get_cached_podcasts():
       redis_client = get_redis_client()
       cached_podcasts = redis_client.get('podcasts')
       if cached_podcasts:
           return json.loads(cached_podcasts)
       else:
           podcasts = fetch_podcasts_from_database()
           redis_client.set('podcasts', json.dumps(podcasts))
           return podcasts
   ```

5. **Session Management with Redis**: Store user session data in Redis for fast access.

   ```python
   session['user'] = user_data  # Store user session in Redis
   ```

---

## **API Endpoints**

### **Authentication Endpoints:**

- `GET /login`: Initiates GitHub OAuth.
- `GET /callback`: GitHub OAuth callback handler.

### **Podcast Management Endpoints:**

- `POST /upload`: Uploads a podcast to Azure Blob Storage.
- `GET /podcasts`: Lists all podcasts uploaded by the user (cached in Redis).
- `GET /podcast/{id}`: Streams the specific podcast.
- `DELETE /podcast/{id}`: Deletes the specific podcast from storage.

---

## **Testing**

### **Backend Testing:**

1. **Postman** or **VS Code REST Client** for API endpoint testing.
2. Test Redis cache by checking if data is being cached correctly.
3. Ensure proper file validation (only accept audio files like `.mp3`).
4. Test podcast upload, retrieval, and deletion operations.

### **Frontend Testing:**

1. Test **OAuth login** functionality to ensure users can log in successfully.
2. Test **podcast upload** and **playback** functionalities.
3. Ensure **shareable URLs** for podcasts work correctly.

---

## **Deployment**

### **Backend Deployment (Azure App Service):**

1. Deploy the Flask app on **Azure App Service**.
2. Use **GitHub Actions** for continuous deployment.

### **Frontend Deployment (Netlify/GitHub Pages):**

1. Deploy the React app on **Netlify** or **GitHub Pages**.
2. Update the frontend to point to the production backend URL.

---

## **How to Run the Project Locally**

1. **Clone the repository:**

   ```bash
   git clone https://github.com/yourusername/shortcast.git
   ```

2. **Set up the backend:**

   - Navigate to the `backend` folder.
   - Create a virtual environment and install dependencies:

     ```bash
     python -m venv venv
     source venv/bin/activate  # On Windows: venv\Scripts\activate
     pip install -r requirements.txt
     ```

   - Run the Flask backend locally:

     ```bash
     python app.py
     ```

3. **Set up the frontend:**

   - Navigate to the `frontend` folder.
   - Install the dependencies:

     ```bash
     npm install
     ```

   - Run the React frontend locally:

     ```bash
     npm start
     ```

---

## **Project Documentation**

This project uses a decoupled architecture, ensuring separation between the frontend and backend. **Flask** handles authentication, caching, and storage, while **React** handles the user interface. **GitHub OAuth** allows users to log in securely, **Azure Blob Storage** stores podcast files, and **Redis** enhances performance by caching frequently accessed data.

---

## **Screenshots/Demo Video**

- **Login Page**: OAuth login via GitHub.
- **Dashboard**: List of uploaded podcasts.
- **Podcast Player**: Embedded player for podcasts.

---

## **Architecture Diagram**

![Architecture Diagram](path/to/architecture-diagram.png)

---

## **Submission Checklist:**

1. Complete GitHub Universe Learning Challenge.
2. Ensure GitHub OAuth, Azure Blob, and Redis integrations are functional.
3. Document the usage of **GitHub Copilot** and **VS Code Extensions** in the README.
4. Submit the project on **Devpost** before the hackathon deadline.

---