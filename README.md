
---

# **Project Name: ShortCast API - Micro Podcast Platform Backend**

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
ShortCast API serves as the backbone for the ShortCast micro podcast platform, a modern solution for creating, uploading, and sharing short-form podcasts. This API is crafted to provide seamless user authentication, robust podcast management, and high performance with Redis integration for caching and session handling. The system also leverages Azure Blob Storage for secure and scalable media file storage. With a focus on performance, scalability, and ease of use, ShortCast API is designed to cater to the evolving needs of podcast creators and listeners alike.

---

## **Features**
- **OAuth Authentication**: Utilizes OAuth for secure user authentication via GitHub and Twitch, ensuring a smooth and reliable login experience.
- **Podcast Management**: Endpoints to manage podcast creation, updates, deletion, and metadata like titles, descriptions, and timestamps, ensuring creators maintain full control over their content.
- **Search and Discovery**: A powerful search engine to allow users to discover podcasts based on keywords, categories, or creators, enabling a rich and personalized listening experience.
- **Redis Caching**: Redis is integrated for efficient data caching and session management, reducing response times and improving performance across the platform.
- **Azure Blob Storage Integration**: Podcast media files are securely stored in Azure Blob Storage, providing scalable, highly available, and cost-effective storage for large media files.
- **Flasgger-Generated API Documentation**: Comprehensive API documentation is automatically generated, allowing easy exploration of endpoints, input/output specifications, and error handling.

---

## **Technologies Used**
- **Backend**: Flask (Python)
- **Database**: Redis (for caching and session management), SQLite (for relational data)
- **Authentication**: OAuth via GitHub and Twitch
- **Storage**: Azure Blob Storage
- **API Documentation**: Flasgger (for automatic API documentation generation)
- **Deployment**: (Pending)

---

## **Installation**
### Prerequisites:
- Python 3.8 or higher
- Redis (locally or via a service such as Redis Labs)
- Azure Blob Storage account
- GitHub and Twitch OAuth credentials

### Steps:
1. Clone the repository:
   ```bash
   git clone https://github.com/jerrygeorge360/shortcast-api.git
   cd shortcast-api
   ```

2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up the environment variables:
   - Create a `.env` file and add the following configurations:
     - `TWITCH_CLIENT_ID`, `TWITCH_CLIENT_SECRET_KEY`, `TWITCH_REDIRECT_URI`
     - `GITHUB_SECRET_KEY`, `GITHUB_ID`, `GITHUB_REDIRECT_URI`
     - `FLASK_SECRET_KEY`
     - `AZURE_ACCOUNT_NAME`, `AZURE_CONNECTION_STRING`, `AZURE_CONTAINER_NAME`
     - `WEBHOOK_SECRET`

4. Run the application:
   ```bash
   flask run
   ```

The API will be available at `/apidocs`.

---

## **Configuration**
- **Redis**: Ensure that Redis is running locally or configure it to connect to your Redis instance. The `.env` file should contain the necessary Redis connection details.
- **Azure Blob Storage**: Set up an Azure Blob Storage account and configure the access keys in the `.env` file to enable secure podcast file storage.
- **OAuth**: Configure OAuth for GitHub and Twitch via their respective developer consoles and add the client credentials to the `.env` file for authentication purposes.

---

## **Usage**
Once the application is running:
1. Navigate to `http://localhost:5000/apidocs` to access the full API documentation.
2. Authenticate users via GitHub or Twitch OAuth.
3. Use the following API endpoints to manage podcasts:
   - **POST** `/api/v1/podcasts`: Upload a new podcast episode.
   - **GET** `/api/v1/podcasts`: Retrieve a list of podcasts.
   - **GET** `/api/v1/podcasts/{id}`: Retrieve details for a specific podcast episode.
   - **PUT** `/api/v1/podcasts/{id}`: Update podcast metadata.
   - **DELETE** `/api/v1/podcasts/{id}`: Delete a podcast episode.



---

## **License**
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more details.

---

## **Future Plans**

### **AI-Powered Transcription**
One of the future goals of ShortCast is to integrate AI transcription services to automatically generate transcripts for uploaded podcast episodes. By leveraging Azure Cognitive Services (like Speech to Text), creators will be able to enhance the accessibility of their podcasts, providing valuable text-based content that can be searched, indexed, and translated for global audiences.

### **Piracy Detection**
We plan to incorporate AI-based piracy detection and content verification to prevent unauthorized use and sharing of copyrighted material. This can be achieved by using Azure's Content Moderator and AI models to analyze and flag audio content for infringement. These capabilities will help ensure a safe and legal environment for podcast creators and listeners alike.

### **Scalability and Containerization**
As the platform grows, ShortCast aims to scale by adopting containerized deployments using Azure Kubernetes Service (AKS) for better resource management and fault tolerance. This will enable automatic scaling and resource optimization as the user base expands.

### **Enhanced Search Capabilities**
In the future, we plan to enhance podcast discovery by integrating AI-powered search features. This includes natural language processing (NLP) to allow users to search for podcasts using conversational queries, improving the overall search experience.

---