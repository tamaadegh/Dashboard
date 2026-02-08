# Tamaade E-Commerce API Documentation for Mobile App Integration

## Base URL
```
Development: http://localhost:8000
Production: https://your-production-domain.com
```

---

## 🔑 Authentication
Most storefront endpoints are **publicly accessible** (no authentication required for browsing products and categories).

For user-specific operations (cart, orders, profile), you'll need JWT authentication:
- **Login Endpoint**: `POST /user/storefront/api/login/`
- **Register Endpoint**: `POST /user/storefront/api/register/`
- **Token Refresh**: `POST /user/storefront/api/token/refresh/`

---

## 📦 Products API

### 1. Get All Products (List)
**Endpoint**: `GET /product/storefront/api/products/`

**Headers**:
```
Accept: application/json
Currency: GHS  (optional - defaults to GHS)
```

**Query Parameters**:
- `limit` - Number of items per page (default: 20)
- `offset` - Pagination offset
- `name` - Filter by product name (case-insensitive)
- `category` - Filter by category ID
- `category_name` - Filter by category name (case-insensitive)
- `brand` - Filter by brand (case-insensitive)
- `collection` - Filter by collection ID
- `ordering` - Sort by field (e.g., `name`, `-created_at`)
- `search` - Full-text search

**Example Request**:
```http
GET /product/storefront/api/products/?limit=10&offset=0
```

**Response Structure**:
```json
{
  "count": 6,
  "current_pagination_step": {
    "previous_url": null,
    "next_url": null,
    "page_links": [
      ["http://localhost:8000/product/storefront/api/products/", 1, true, false]
    ]
  },
  "results": [
    {
      "id": 1,
      "texts": {
        "name": "Metal Bed Frame",
        "summary": "Durable metal bed frame",
        "description": "High-quality metal bed frame..."
      },
      "slug": "metal-bed-frame",
      "default_variant": {
        "id": 1,
        "alias": "Standard",
        "name": "Metal Bed Frame - Standard",
        "price": "450.00"
      },
      "product_thumbnail": "https://cloudinary.com/image.jpg"
    }
  ]
}
```

**Response Fields**:
- `count` - Total number of products
- `current_pagination_step` - Pagination metadata
- `results` - Array of products
  - `id` - Product ID
  - `texts` - Localized text content
    - `name` - Product name
    - `summary` - Short description
    - `description` - Full description (HTML)
  - `slug` - URL-friendly identifier
  - `default_variant` - Default product variant
    - `id` - Variant ID
    - `alias` - Variant name (e.g., "Small", "Large")
    - `name` - Full variant name
    - `price` - Price in selected currency
  - `product_thumbnail` - Main product image URL

---

### 2. Get Single Product (Detail)
**Endpoint**: `GET /product/storefront/api/products/{slug}/`

**Example Request**:
```http
GET /product/storefront/api/products/metal-bed-frame/
```

**Response Structure**:
```json
{
  "id": 1,
  "brand": "Tamaade Furniture",
  "category": 1,
  "collections": [1, 2],
  "variants": [
    {
      "id": 1,
      "alias": "Queen Size",
      "name": "Metal Bed Frame - Queen Size",
      "price": "450.00"
    },
    {
      "id": 2,
      "alias": "King Size",
      "name": "Metal Bed Frame - King Size",
      "price": "550.00"
    }
  ],
  "slug": "metal-bed-frame",
  "product_thumbnail": "https://cloudinary.com/image.jpg",
  "texts": {
    "name": "Metal Bed Frame",
    "summary": "Durable metal bed frame",
    "description": "<p>High-quality metal bed frame with modern design...</p>"
  }
}
```

---

### 3. Get Product with Images
**Endpoint**: `GET /product/storefront/api/products/{slug}/retrive_with_image_list/`

**Note**: The endpoint spelling uses `retrive` (missing 'e'). Please use exactly as shown.

**Response**: Same as product detail but includes `images` array:
```json
{
  "id": 1,
  "texts": {...},
  "brand": "Tamaade Furniture",
  "category": 1,
  "collections": [1, 2],
  "variants": [...],
  "slug": "metal-bed-frame",
  "images": [
    {
      "id": 1,
      "image": "https://cloudinary.com/image1.jpg",
      "alt_text": "Metal bed frame front view"
    },
    {
      "id": 2,
      "image": "https://cloudinary.com/image2.jpg",
      "alt_text": "Metal bed frame side view"
    }
  ]
}
```

---

### 4. Get Recommended Products
**Endpoint**: `GET /product/storefront/api/products/{slug}/with_recommended/`

Returns products similar to the specified product (based on name similarity).

**Response**: Array of products (same structure as product list)

---

## 📂 Categories API

### Get All Categories
**Endpoint**: `GET /product/storefront/api/recursive-categories/`

**Example Request**:
```http
GET /product/storefront/api/recursive-categories/
```

**Response Structure**:
```json
[
  {
    "id": 1,
    "name": "FURNITURE",
    "description": "All furniture items including beds, tables, and chairs",
    "children": [
      {
        "id": 2,
        "name": "Beds",
        "description": "Bed frames and mattresses",
        "children": []
      },
      {
        "id": 3,
        "name": "Tables",
        "description": "Dining and coffee tables",
        "children": []
      }
    ]
  }
]
```

**Response Fields**:
- `id` - Category ID
- `name` - Category name
- `description` - Category description
- `children` - Nested subcategories (recursive structure)

---

## 🏷️ Collections API

### Get All Collections
**Endpoint**: `GET /product/storefront/api/collections/`

**Example Request**:
```http
GET /product/storefront/api/collections/
```

**Response Structure**:
```json
[
  {
    "id": 1,
    "name": "metal beds",
    "description": "Collection of metal bed frames",
    "is_active": true,
    "image": null
  },
  {
    "id": 2,
    "name": "Summer Sale",
    "description": "Products on summer sale",
    "is_active": true,
    "image": "https://cloudinary.com/collection-image.jpg"
  }
]
```

**Response Fields**:
- `id` - Collection ID
- `name` - Collection name
- `description` - Collection description
- `is_active` - Whether collection is active
- `image` - Collection banner image URL (nullable)

---

## 🛒 Cart API

### Get Cart
**Endpoint**: `GET /cart/storefront/api/cart/`

**Authentication**: Required (JWT token)

**Headers**:
```
Authorization: Bearer <access_token>
Currency: GHS
```

---

## 💳 Payment API (Hubtel Integration)

### 1. Initiate Payment
**Endpoint**: `POST /payments/api/initiate/`

**Request Body**:
```json
{
  "msisdn": "0241234567",
  "amount": "100.00",
  "channel": "mtn-gh",
  "customer_name": "John Doe",
  "customer_email": "john@example.com"
}
```

**Response**:
```json
{
  "client_reference": "uuid-string",
  "hubtel_response": {
    "TransactionId": "hubtel-transaction-id",
    "Status": "Pending"
  }
}
```

### 2. Check Payment Status
**Endpoint**: `GET /payments/api/status/{client_reference}/`

**Response**:
```json
{
  "client_reference": "uuid-string",
  "status": "SUCCESS",
  "amount": "100.00",
  "customer_msisdn": "0241234567",
  "hubtel_transaction_id": "hubtel-transaction-id"
}
```

---

## 🔍 Search & Filtering

### Search Products
```http
GET /product/storefront/api/products/?search=bed
```

### Filter by Category
```http
GET /product/storefront/api/products/?category=1
```

### Filter by Brand
```http
GET /product/storefront/api/products/?brand=Tamaade
```

### Filter by Collection
```http
GET /product/storefront/api/products/?collection=1
```

### Combine Filters
```http
GET /product/storefront/api/products/?category=1&brand=Tamaade&ordering=-created_at
```

---

## 🌍 Multi-Currency Support

The API supports multiple currencies. Send the `Currency` header with requests:

**Supported Currencies**: GHS, USD, EUR, GBP, NGN, KES, ZAR, XOF, XAF

**Example**:
```http
GET /product/storefront/api/products/
Currency: USD
```

Prices in the response will be automatically converted to the requested currency.

---

## 📊 Pagination

All list endpoints use pagination:

**Query Parameters**:
- `limit` - Items per page (default: 20)
- `offset` - Number of items to skip

**Example**:
```http
GET /product/storefront/api/products/?limit=10&offset=20
```

**Response includes**:
- `count` - Total items
- `current_pagination_step.next_url` - Next page URL
- `current_pagination_step.previous_url` - Previous page URL

---

## ⚡ Performance & Caching

- Product lists are cached for 15 minutes
- Product details are cached for 15 minutes
- Categories are cached for 1 hour
- Collections are cached for 1 hour

The API automatically handles cache invalidation.

---

## 🔧 Health Check

**Endpoint**: `GET /health/`

**Response**:
```json
{
  "status": "healthy",
  "version": "3.0.0",
  "environment": "production",
  "checks": {
    "database": "ok",
    "cache": "ok"
  }
}
```

Use this endpoint to verify API availability.

---

## 📱 GraphQL Alternative

The API also supports GraphQL for more flexible queries:

**Endpoint**: `POST /graphql/`

**Example Query**:
```graphql
query {
  products(first: 10) {
    edges {
      node {
        id
        name
        slug
        defaultVariant {
          price
        }
      }
    }
  }
}
```

---

## 🚨 Error Handling

### Common HTTP Status Codes

- `200 OK` - Success
- `201 Created` - Resource created
- `400 Bad Request` - Invalid request data
- `401 Unauthorized` - Authentication required
- `403 Forbidden` - Insufficient permissions
- `404 Not Found` - Resource not found
- `500 Internal Server Error` - Server error
- `502 Bad Gateway` - External service error (e.g., payment gateway)
- `503 Service Unavailable` - Service temporarily unavailable

### Error Response Format

```json
{
  "detail": "Error message here",
  "errors": {
    "field_name": ["Error for this field"]
  }
}
```

---

## 📝 API Documentation

Interactive API documentation is available at:
- **Swagger UI**: `/docs-storefront-swagger/`
- **ReDoc**: `/docs-storefront-redoc/`

---

## 🔐 CORS Configuration

The API is configured to accept requests from allowed origins. Make sure your mobile app's domain is added to `CORS_ALLOWED_ORIGINS` in production.

---

## 📞 Support

For API issues or questions, check the Sentry dashboard for error logs and performance metrics.
