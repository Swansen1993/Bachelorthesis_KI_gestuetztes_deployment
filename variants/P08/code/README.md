# FastAPI RBAC E-commerce Microservice

A robust, scalable e-commerce backend microservice built with FastAPI, featuring Role-Based Access Control (RBAC) for secure multi-tenant operations. This project demonstrates modern API development with proper authentication, authorization, and database design patterns.

<p align="center">
  <a href="https://fastapi.tiangolo.com/"><img src="https://img.shields.io/badge/FastAPI-%23E03C31.svg?style=for-the-badge&logo=fastapi&logoColor=white" alt="FastAPI"></a>
  <a href="https://www.postgresql.org/"><img src="https://img.shields.io/badge/PostgreSQL-%232E2A47.svg?style=for-the-badge&logo=postgresql&logoColor=white" alt="PostgreSQL"></a>
  <a href="https://www.sqlalchemy.org/"><img src="https://img.shields.io/badge/SQLAlchemy-%2334A1D6.svg?style=for-the-badge&logo=sqlalchemy&logoColor=white" alt="SQLAlchemy"></a>
  <a href="https://alembic.sqlalchemy.org/"><img src="https://img.shields.io/badge/Alembic-%236C5B7B.svg?style=for-the-badge&logo=alembic&logoColor=white" alt="Alembic"></a>
  <a href="https://pydantic-docs.helpmanual.io/"><img src="https://img.shields.io/badge/Pydantic-%23FF5C8D.svg?style=for-the-badge&logo=pydantic&logoColor=white" alt="Pydantic"></a>
  <a href="https://www.uvicorn.org/"><img src="https://img.shields.io/badge/Uvicorn-%23444444.svg?style=for-the-badge&logo=uvicorn&logoColor=white" alt="Uvicorn"></a>
  <a href="https://www.python.org/"><img src="https://img.shields.io/badge/Python-%233776AB.svg?style=for-the-badge&logo=python&logoColor=white" alt="Python"></a>
  <a href="https://jwt.io/"><img src="https://img.shields.io/badge/JWT-purple?style=for-the-badge&logo=jwt" alt="JWT"></a>
  <a href="https://swagger.io/"><img src="https://img.shields.io/badge/Swagger-yellow?style=for-the-badge&logo=swagger" alt="Swagger UI"></a>
</p>

## 🚀 Features

### 🔐 Role-Based Access Control (RBAC)
- **Three-tier role system**: Customer, Seller, Admin
- **Granular permissions**: Each role has specific capabilities
- **Secure endpoints**: Role-based dependency injection
- **JWT authentication**: Stateless, scalable authentication

### 🛍️ E-commerce Capabilities
- **User Management**: Registration, profile management, authentication
- **Product Catalog**: CRUD operations with category management
- **Shopping Cart**: Add, update, remove items with persistence
- **Order System**: Complete order lifecycle management
- **Inventory Management**: Stock tracking and updates
- **Reviews & Ratings**: Product feedback system
- **Wishlist**: Save products for later
- **Shipment Tracking**: Order fulfillment tracking

### 🏗️ Architecture
- **Microservice-ready**: Modular design for scalability
- **RESTful API**: Clean, predictable endpoints
- **Database Migrations**: Alembic for schema management
- **Validation**: Pydantic models for request/response validation
- **Documentation**: Auto-generated OpenAPI documentation

## 📋 Role Permissions

| Feature | Customer | Seller | Admin |
|---------|----------|--------|-------|
| **User Registration** | ✅ | ✅ | ✅ |
| **Browse Products** | ✅ | ✅ | ✅ |
| **Shopping Cart** | ✅ | ✅ | ✅ |
| **Place Orders** | ✅ | ✅ | ✅ |
| **Write Reviews** | ✅ | ✅ | ✅ |
| **Manage Own Products** | ❌ | ✅ | ✅ |
| **Manage All Products** | ❌ | ❌ | ✅ |
| **Manage Categories** | ❌ | ✅ | ✅ |
| **Manage Users** | ❌ | ❌ | ✅ |
| **Manage Shipments** | ❌ | ✅ | ✅ |
| **System Administration** | ❌ | ❌ | ✅ |

## 🛠️ Tech Stack

*   **Framework**: FastAPI
*   **Database**: PostgreSQL
*   **ORM**: SQLAlchemy 2.0
*   **Authentication**: JWT with bcrypt hashing
*   **Migrations**: Alembic
*   **Validation**: Pydantic v2
*   **API Documentation**: Swagger UI & ReDoc
*   **Package Management**: pip

## 📁 Project Structure
```bash
FastAPI-RBAC-Microservice/
├── app/
│ ├── init.py
│ ├── main.py                                # FastAPI application entry point
│ ├── database.py                            # Database configuration
│ ├── models.py                              # SQLAlchemy models
│ ├── schemas.py                             # Pydantic schemas
│ ├── crud.py                                # Database operations
│ ├── auth.py                                # Authentication utilities
│ └── config.py                              # Configuration management
├── alembic/                                 # Database migrations
│ ├── versions/
│ ├── env.py
│ └── alembic.ini
├── requirements.txt                        # Project dependencies
├── .env                                    # Environment variables template
└── README.md                               # Project documentation
```
## 🚀 Quick Start

### Prerequisites

*   Python 3.8+
*   PostgreSQL 12+
*   pip (Python package manager)

### Installation

1.  **Clone the repository**

    ```bash
    git clone https://github.com/HarshitWaldia/FastAPI-RBAC-Microservice.git
    cd FastAPI-RBAC-Microservice
    ```

2.  **Create virtual environment**

    ```bash
    python -m venv venv
    source venv/bin/activate  # Linux/MacOS
    # OR
    venv\Scripts\activate     # Windows
    ```

3.  **Install dependencies**

    ```bash
    pip install -r requirements.txt
    ```

4.  **Environment Configuration**

    ```bash
    code .env
    ```

    Edit `.env` with your configuration:

    ```env
    DATABASE_URL=postgresql://username:password@localhost:5432/ecommerce_db
    SECRET_KEY=your-super-secret-key-here
    ALGORITHM=HS256
    ACCESS_TOKEN_EXPIRE_MINUTES=60
    ```

5.  **Database Setup**

    ```bash
    # Create database in PostgreSQL
    createdb ecommerce_db

    # Run migrations
    alembic upgrade head
    ```

6.  **Start the server**

    ```bash
    uvicorn app.main:app --reload
    ```

## 📚 API Documentation

Once running, access the interactive API documentation:

*   Swagger UI: [http://localhost:8000/docs](http://localhost:8000/docs)
*   ReDoc: [http://localhost:8000/redoc](http://localhost:8000/redoc)

## 🔐 Authentication Flow

1.  **Register:** `POST /users/` - Create new user account
2.  **Login:** `POST /login` - Get JWT access token
3.  **Access Protected Routes:** Include token in `Authorization: Bearer <token>` header

## 🎯 Example Usage

### Customer Workflow

```bash
# 1. Register as customer
curl -X POST "http://localhost:8000/users/" \
  -H "Content-Type: application/json" \
  -d '{"name": "John Doe", "email": "john@example.com", "password": "password123"}'

# 2. Login
curl -X POST "http://localhost:8000/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=john@example.com&password=password123"

# 3. Browse products
curl -X GET "http://localhost:8000/products/" \
  -H "Authorization: Bearer <your_token>"

# 4. Add to cart
curl -X POST "http://localhost:8000/cart/1/items" \
  -H "Authorization: Bearer <your_token>" \
  -H "Content-Type: application/json" \
  -d '{"product_id": 1, "quantity": 2}'

# 5. Place order
curl -X POST "http://localhost:8000/orders/" \
  -H "Authorization: Bearer <your_token>" \
  -d '{"user_id": 1}'
```

### **Seller Workflow**

```bash
# 1. Register as seller (or get role updated by admin)
curl -X POST "http://localhost:8000/users/" \
  -H "Content-Type: application/json" \
  -d '{"name": "Seller Jane", "email": "jane@seller.com", "password": "password123", "role": "seller"}'

# 2. Create product
curl -X POST "http://localhost:8000/seller/products/" \
  -H "Authorization: Bearer <seller_token>" \
  -H "Content-Type: application/json" \
  -d '{"name": "New Product", "price": 29.99, "stock": 100, "category_id": 1}'
```
## 🔧 **Development**

### Code Style 
```
# Format code
black app/

# Sort imports
isort app/
```

### Database Migrations
```Bash
# Create new migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1

# Revert all migration
alembic downgrade base
```
## 🌟 Key Endpoints

This API provides endpoints for users, customers, sellers, and administrators.  Below is a breakdown of the available routes.

### Public Endpoints

These endpoints do not require authentication.

*   **`POST /users/`** - User registration.  Creates a new user account.
*   **`POST /login`** - User authentication.  Logs in an existing user and returns an authentication token.

### Customer Endpoints

These endpoints require user authentication.

*   **`GET /me`** - Current user profile.  Retrieves information about the currently authenticated user.
*   **`GET /cart/{user_id}`** - View cart.  Retrieves the contents of a user's shopping cart.
*   **`POST /cart/{user_id}/items`** - Add to cart.  Adds an item to a user's shopping cart.
*   **`POST /orders/`** - Create order.  Creates a new order for the currently authenticated user.
*   **`POST /wishlist/`** - Add to wishlist. Adds an item to the user's wishlist.

### Seller Endpoints

These endpoints require seller authentication.

*   **`GET /seller/products/`** - Manage products.  Retrieves a list of products owned by the seller.
*   **`POST /seller/products/`** - Create product.  Creates a new product for the seller.
*   **`PUT /seller/products/{id}`** - Update product.  Updates an existing product owned by the seller.  `{id}` represents the product ID.

### Admin Endpoints

These endpoints require administrator authentication.

*   **`GET /admin/users/`** - User management.  Retrieves a list of all users.
*   **`PUT /admin/users/{id}/role`** - Change user roles.  Updates the role of a user.  `{id}` represents the user ID.
*   **`DELETE /admin/products/{id}`** - Delete any product.  Deletes a product from the system.  `{id}` represents the product ID.

---

## 🤝 Contributing

We welcome and encourage contributions to this project!  Here's how you can get involved:

1.  **Fork the repository:**  Create your own fork of this repository on GitHub.
2.  **Create your feature branch:**  `git checkout -b feature/AmazingFeature` (Replace `AmazingFeature` with a descriptive name for your branch).
3.  **Commit your changes:**  `git commit -m 'Add some AmazingFeature'` (Use clear and concise commit messages).
4.  **Push to the branch:**  `git push origin feature/AmazingFeature`
5.  **Open a Pull Request:**  Submit a pull request to the main repository.  Please include a detailed description of your changes.

We appreciate your help in making this project even better!

## 👨‍💻 Author

**Harshit Waldia**

*   GitHub: [@HarshitWaldia](https://github.com/HarshitWaldia)
*   LinkedIn: [Harshit Waldia](https://www.linkedin.com/in/harshitwaldia/)

---

## 🙏 Acknowledgments

*   The amazing [FastAPI](https://fastapi.tiangolo.com/) team for providing such an excellent framework.
*   The [SQLAlchemy](https://www.sqlalchemy.org/) and [Alembic](https://alembic.sqlalchemy.org/en/latest/) communities for their powerful database tools.
*   All contributors and users of this project – thank you for your support!
