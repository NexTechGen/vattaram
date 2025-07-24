# Vattaram - Faculty of Technology Student Locator

![Faculty of Technology Logo](https://placehold.co/600x200?text=Vattaram+FoUJ+Logo&font=roboto)

**Connect with fellow Faculty of Technology undergraduates at University of Jaffna**

## 🌍 About Vattaram

This platform serves as a digital meeting point for all FoUJ undergraduates to:
- Share contact information
- Display our locations across campus and beyond
- Build our student community network
- Find classmates for projects and collaborations

## 🛠️ Technical Implementation

### Core Features
- **Student Profiles**: Register with your details and location
- **Interactive Map**: Visualize where fellow students are located
- **Secure Access**: Protected login system
- **Mobile Responsive**: Works on all devices

### Technology Stack


import os
from pymongo import MongoClient
import gridfs
from urllib.parse import quote_plus

# MongoDB Atlas Connection with secure configuration
try:
    # Get credentials from environment variables (recommended for security)
    username = quote_plus(os.getenv('MONGO_USERNAME', 'UOJvattaram'))
    password = quote_plus(os.getenv('MONGO_PASSWORD', 'UOJ2023et'))
    cluster_url = os.getenv('MONGO_CLUSTER', 'cluster0.qxvkvqt.mongodb.net')
    db_name = os.getenv('MONGO_DB', 'vattaram')
    collection_name = 'weare'
    
    # SSL/TLS configuration
    connection_params = {
        'retryWrites': True,
        'w': 'majority',
        'socketTimeoutMS': 50000,
        'connectTimeoutMS': 50000,
        'serverSelectionTimeoutMS': 50000,
        'tls': True,
        'tlsAllowInvalidCertificates': False,  # Disable in production
        'tlsCAFile': os.getenv('MONGO_CA_FILE', None)  # For certificate validation
    }
    
    # Construct connection URI
    mongo_uri = f'mongodb+srv://{username}:{password}@{cluster_url}/?{parse_qs(urlencode(connection_params))}'
    
    # Initialize client
    client = MongoClient(mongo_uri)
    
    # Verify connection
    client.admin.command('ping')
    print("Successfully connected to MongoDB Atlas!")
    
    # Initialize database and collection
    db = client[db_name]
    collection = db[collection_name]
    fs = gridfs.GridFS(db)

except Exception as e:
    print(f"Failed to connect to MongoDB: {str(e)}")
    raise  # Re-raise exception after logging
