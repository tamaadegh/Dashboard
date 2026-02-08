# Tamaade API - Quick Reference Card

## 🔗 Base URLs
```
Development: http://10.0.2.2:8000 (Android Emulator)
Production:  https://your-domain.com
```

## 📦 Essential Endpoints

### Products
```
GET  /product/storefront/api/products/                    # List all products
GET  /product/storefront/api/products/{slug}/             # Product detail
GET  /product/storefront/api/products/{slug}/retrive_with_image_list/  # With images (Note: 'retrive')
```

### Categories & Collections
```
GET  /product/storefront/api/recursive-categories/        # All categories (nested)
GET  /product/storefront/api/collections/                 # All collections
```

### Health & Monitoring
```
GET  /health/                                             # API health check
```

## 🔑 Common Headers
```
Accept: application/json
Content-Type: application/json
Currency: GHS
Authorization: Bearer <token>  (for authenticated endpoints)
```

## 🔍 Query Parameters

### Products List
```
?limit=20              # Items per page
?offset=0              # Pagination offset
?category=1            # Filter by category ID
?search=bed            # Search query
?ordering=-created_at  # Sort (- for descending)
?brand=Tamaade         # Filter by brand
?collection=1          # Filter by collection
```

## 📊 Response Structures

### Product List
```json
{
  "count": 6,
  "results": [
    {
      "id": 1,
      "texts": {
        "name": "Product Name",
        "summary": "Short description",
        "description": "Full HTML description"
      },
      "slug": "product-slug",
      "default_variant": {
        "id": 1,
        "price": "450.00"
      },
      "product_thumbnail": "https://..."
    }
  ]
}
```

### Categories
```json
[
  {
    "id": 1,
    "name": "FURNITURE",
    "description": "...",
    "children": [...]
  }
]
```

### Collections
```json
[
  {
    "id": 1,
    "name": "Collection Name",
    "is_active": true,
    "image": "https://..."
  }
]
```

## 💡 Quick Examples

### Fetch Products
```kotlin
// Get first 10 products
apiService.getProducts(limit = 10, offset = 0)

// Search for "bed"
apiService.getProducts(searchQuery = "bed")

// Filter by category
apiService.getProducts(categoryId = 1)

// Sort by newest
apiService.getProducts(ordering = "-created_at")
```

### Fetch Categories
```kotlin
apiService.getCategories()
```

### Fetch Product Detail
```kotlin
apiService.getProductDetail(slug = "metal-bed-frame")
```

## 🌍 Supported Currencies
GHS, USD, EUR, GBP, NGN, KES, ZAR, XOF, XAF

## ⚡ Performance Tips
- Products cached for 15 minutes
- Categories cached for 1 hour
- Use pagination for large lists
- Load images with Coil/Glide

## 🚨 Error Codes
```
200 - Success
400 - Bad Request
401 - Unauthorized
404 - Not Found
500 - Server Error
502 - Payment Gateway Error
```

## 📱 Android Emulator Setup
```kotlin
// Use this base URL for emulator
const val BASE_URL = "http://10.0.2.2:8000/"

// For physical device on same network
const val BASE_URL = "http://192.168.x.x:8000/"
```

## 🔐 Authentication (Future)
```kotlin
// Login
POST /user/storefront/api/login/
Body: { "email": "...", "password": "..." }

// Response
{ "access": "token", "refresh": "token" }

// Use in headers
Authorization: Bearer <access_token>
```

## 📋 Testing Checklist
- [ ] Health check returns 200
- [ ] Products load with images
- [ ] Categories display nested structure
- [ ] Collections load
- [ ] Search works
- [ ] Pagination works
- [ ] Error handling works
- [ ] Images load from Cloudinary

## 🛠️ Debug Commands
```bash
# Test health endpoint
curl http://localhost:8000/health/

# Test products endpoint
curl http://localhost:8000/product/storefront/api/products/

# Test categories
curl http://localhost:8000/product/storefront/api/recursive-categories/

# Test with currency header
curl -H "Currency: USD" http://localhost:8000/product/storefront/api/products/
```

## 📞 Need Help?
1. Check full docs: `MOBILE_APP_API_DOCUMENTATION.md`
2. Integration guide: `KOTLIN_MOBILE_APP_INTEGRATION_PROMPT.md`
3. Swagger UI: http://localhost:8000/docs-storefront-swagger/
4. Sentry Dashboard: Check for backend errors
