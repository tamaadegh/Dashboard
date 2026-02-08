# Kotlin Mobile App - Backend Integration Prompt

## 🎯 Objective
Integrate the Tamaade E-Commerce Android app (Kotlin) with the Django REST API backend to fetch and display products, categories, and collections. Ensure robust error handling, proper data models, and efficient API communication.

---

## 📋 Requirements

### 1. **API Base Configuration**
- **Base URL**: 
  - Development: `http://10.0.2.2:8000` (for Android Emulator)
  - Production: `https://your-production-domain.com`
- **API Endpoints to Integrate**:
  - Products: `/product/storefront/api/products/`
  - Product Detail: `/product/storefront/api/products/{slug}/`
  - Categories: `/product/storefront/api/recursive-categories/`
  - Collections: `/product/storefront/api/collections/`
  - Health Check: `/health/`

### 2. **Technology Stack**
Use the following Kotlin/Android libraries:
- **Retrofit 2** - For REST API calls
- **Moshi** or **Gson** - For JSON serialization/deserialization
- **OkHttp** - For HTTP client with interceptors
- **Coroutines** - For asynchronous operations
- **Flow** - For reactive data streams
- **Hilt** or **Koin** - For dependency injection
- **Coil** or **Glide** - For image loading
- **Paging 3** (optional) - For pagination

### 3. **Data Models Required**

Create Kotlin data classes for the following API responses:

#### Product Model
```kotlin
data class Product(
    val id: Int,
    val texts: ProductTexts,
    val slug: String,
    val defaultVariant: ProductVariant?,
    val productThumbnail: String?
)

data class ProductTexts(
    val name: String,
    val summary: String?,
    val description: String?
)

data class ProductVariant(
    val id: Int,
    val alias: String,
    val name: String,
    val price: String
)
```

#### Product List Response
```kotlin
data class ProductListResponse(
    val count: Int,
    val currentPaginationStep: PaginationStep,
    val results: List<Product>
)

data class PaginationStep(
    val previousUrl: String?,
    val nextUrl: String?,
    val pageLinks: List<List<Any>>
)
```

#### Category Model
```kotlin
data class Category(
    val id: Int,
    val name: String,
    val description: String?,
    val children: List<Category>
)
```

#### Collection Model
```kotlin
data class Collection(
    val id: Int,
    val name: String,
    val description: String?,
    val isActive: Boolean,
    val image: String?
)
```

#### Product Detail Model
```kotlin
data class ProductDetail(
    val id: Int,
    val brand: String?,
    val category: Int,
    val collections: List<Int>,
    val variants: List<ProductVariant>,
    val slug: String,
    val productThumbnail: String?,
    val texts: ProductTexts,
    val images: List<ProductImage>? = null
)

data class ProductImage(
    val id: Int,
    val image: String,
    val altText: String?
)
```

### 4. **API Service Interface**

Create a Retrofit service interface:

```kotlin
interface TamaadeApiService {
    
    @GET("product/storefront/api/products/")
    suspend fun getProducts(
        @Query("limit") limit: Int = 20,
        @Query("offset") offset: Int = 0,
        @Query("category") categoryId: Int? = null,
        @Query("search") searchQuery: String? = null,
        @Query("ordering") ordering: String? = null,
        @Header("Currency") currency: String = "GHS"
    ): ProductListResponse
    
    @GET("product/storefront/api/products/{slug}/")
    suspend fun getProductDetail(
        @Path("slug") slug: String,
        @Header("Currency") currency: String = "GHS"
    ): ProductDetail
    
    @GET("product/storefront/api/products/{slug}/retrive_with_image_list/")
    suspend fun getProductWithImages(
        @Path("slug") slug: String,
        @Header("Currency") currency: String = "GHS"
    ): ProductDetail
    
    @GET("product/storefront/api/recursive-categories/")
    suspend fun getCategories(): List<Category>
    
    @GET("product/storefront/api/collections/")
    suspend fun getCollections(): List<Collection>
    
    @GET("health/")
    suspend fun healthCheck(): HealthResponse
}

data class HealthResponse(
    val status: String,
    val version: String,
    val environment: String,
    val checks: Map<String, String>
)
```

### 5. **Repository Pattern**

Implement a repository to handle API calls and data caching:

```kotlin
class ProductRepository @Inject constructor(
    private val apiService: TamaadeApiService
) {
    
    suspend fun getProducts(
        limit: Int = 20,
        offset: Int = 0,
        categoryId: Int? = null,
        searchQuery: String? = null
    ): Result<ProductListResponse> {
        return try {
            val response = apiService.getProducts(
                limit = limit,
                offset = offset,
                categoryId = categoryId,
                searchQuery = searchQuery
            )
            Result.success(response)
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
    
    suspend fun getProductDetail(slug: String): Result<ProductDetail> {
        return try {
            val response = apiService.getProductDetail(slug)
            Result.success(response)
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
    
    suspend fun getCategories(): Result<List<Category>> {
        return try {
            val response = apiService.getCategories()
            Result.success(response)
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
    
    suspend fun getCollections(): Result<List<Collection>> {
        return try {
            val response = apiService.getCollections()
            Result.success(response)
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
}
```

### 6. **Network Configuration**

Set up Retrofit with proper interceptors:

```kotlin
@Module
@InstallIn(SingletonComponent::class)
object NetworkModule {
    
    @Provides
    @Singleton
    fun provideOkHttpClient(): OkHttpClient {
        return OkHttpClient.Builder()
            .addInterceptor(HttpLoggingInterceptor().apply {
                level = HttpLoggingInterceptor.Level.BODY
            })
            .addInterceptor { chain ->
                val request = chain.request().newBuilder()
                    .addHeader("Accept", "application/json")
                    .addHeader("Content-Type", "application/json")
                    .build()
                chain.proceed(request)
            }
            .connectTimeout(30, TimeUnit.SECONDS)
            .readTimeout(30, TimeUnit.SECONDS)
            .build()
    }
    
    @Provides
    @Singleton
    fun provideMoshi(): Moshi {
        return Moshi.Builder()
            .add(KotlinJsonAdapterFactory())
            .build()
    }
    
    @Provides
    @Singleton
    fun provideRetrofit(
        okHttpClient: OkHttpClient,
        moshi: Moshi
    ): Retrofit {
        return Retrofit.Builder()
            .baseUrl("http://10.0.2.2:8000/") // Change for production
            .client(okHttpClient)
            .addConverterFactory(MoshiConverterFactory.create(moshi))
            .build()
    }
    
    @Provides
    @Singleton
    fun provideTamaadeApiService(retrofit: Retrofit): TamaadeApiService {
        return retrofit.create(TamaadeApiService::class.java)
    }
}
```

### 7. **ViewModel Implementation**

Create ViewModels for UI state management:

```kotlin
@HiltViewModel
class ProductListViewModel @Inject constructor(
    private val repository: ProductRepository
) : ViewModel() {
    
    private val _products = MutableStateFlow<UiState<List<Product>>>(UiState.Loading)
    val products: StateFlow<UiState<List<Product>>> = _products.asStateFlow()
    
    private val _categories = MutableStateFlow<UiState<List<Category>>>(UiState.Loading)
    val categories: StateFlow<UiState<List<Category>>> = _categories.asStateFlow()
    
    fun loadProducts(categoryId: Int? = null, searchQuery: String? = null) {
        viewModelScope.launch {
            _products.value = UiState.Loading
            repository.getProducts(categoryId = categoryId, searchQuery = searchQuery)
                .onSuccess { response ->
                    _products.value = UiState.Success(response.results)
                }
                .onFailure { error ->
                    _products.value = UiState.Error(error.message ?: "Unknown error")
                }
        }
    }
    
    fun loadCategories() {
        viewModelScope.launch {
            _categories.value = UiState.Loading
            repository.getCategories()
                .onSuccess { categories ->
                    _categories.value = UiState.Success(categories)
                }
                .onFailure { error ->
                    _categories.value = UiState.Error(error.message ?: "Unknown error")
                }
        }
    }
}

sealed class UiState<out T> {
    object Loading : UiState<Nothing>()
    data class Success<T>(val data: T) : UiState<T>()
    data class Error(val message: String) : UiState<Nothing>()
}
```

### 8. **Error Handling**

Implement comprehensive error handling:

```kotlin
sealed class ApiError : Exception() {
    object NetworkError : ApiError()
    object ServerError : ApiError()
    data class HttpError(val code: Int, val message: String) : ApiError()
    data class UnknownError(val throwable: Throwable) : ApiError()
}

fun Throwable.toApiError(): ApiError {
    return when (this) {
        is IOException -> ApiError.NetworkError
        is HttpException -> {
            when (code()) {
                in 500..599 -> ApiError.ServerError
                else -> ApiError.HttpError(code(), message())
            }
        }
        else -> ApiError.UnknownError(this)
    }
}
```

### 9. **Testing Requirements**

Create unit tests to verify:
1. **API Service Tests**: Mock Retrofit responses
2. **Repository Tests**: Test success and failure scenarios
3. **ViewModel Tests**: Verify state changes
4. **Integration Tests**: Test actual API calls (optional)

Example test:
```kotlin
@Test
fun `getProducts returns success when API call succeeds`() = runTest {
    // Given
    val mockResponse = ProductListResponse(
        count = 1,
        currentPaginationStep = PaginationStep(null, null, emptyList()),
        results = listOf(/* mock product */)
    )
    coEvery { apiService.getProducts(any(), any()) } returns mockResponse
    
    // When
    val result = repository.getProducts()
    
    // Then
    assertTrue(result.isSuccess)
    assertEquals(1, result.getOrNull()?.count)
}
```

### 10. **UI Integration**

Display products in a RecyclerView or LazyColumn (Compose):

```kotlin
@Composable
fun ProductListScreen(viewModel: ProductListViewModel = hiltViewModel()) {
    val productsState by viewModel.products.collectAsState()
    
    when (val state = productsState) {
        is UiState.Loading -> {
            CircularProgressIndicator()
        }
        is UiState.Success -> {
            LazyColumn {
                items(state.data) { product ->
                    ProductItem(product)
                }
            }
        }
        is UiState.Error -> {
            ErrorMessage(state.message)
        }
    }
}

@Composable
fun ProductItem(product: Product) {
    Card(modifier = Modifier.fillMaxWidth().padding(8.dp)) {
        Row {
            AsyncImage(
                model = product.productThumbnail,
                contentDescription = product.texts.name,
                modifier = Modifier.size(100.dp)
            )
            Column(modifier = Modifier.padding(8.dp)) {
                Text(product.texts.name, style = MaterialTheme.typography.titleMedium)
                Text(product.texts.summary ?: "", style = MaterialTheme.typography.bodySmall)
                Text(
                    "GHS ${product.defaultVariant?.price}",
                    style = MaterialTheme.typography.titleSmall,
                    color = MaterialTheme.colorScheme.primary
                )
            }
        }
    }
}
```

---

## ✅ Verification Checklist

After implementation, verify the following:

### 1. **Health Check**
- [ ] App can successfully call `/health/` endpoint
- [ ] Response shows `status: "healthy"`
- [ ] Database and cache checks are "ok"

### 2. **Products**
- [ ] Products list loads successfully
- [ ] Images display correctly from Cloudinary URLs
- [ ] Prices display in correct currency (GHS)
- [ ] Product names and descriptions show properly
- [ ] Pagination works (load more products)
- [ ] Search functionality works
- [ ] Category filtering works

### 3. **Categories**
- [ ] Categories load successfully
- [ ] Nested categories (children) display correctly
- [ ] Category filtering updates product list

### 4. **Collections**
- [ ] Collections load successfully
- [ ] Collection images display (if available)
- [ ] Filtering by collection works

### 5. **Product Detail**
- [ ] Single product detail loads
- [ ] All variants display
- [ ] Multiple images load (if using image list endpoint)
- [ ] Product description renders (handle HTML if needed)

### 6. **Error Handling**
- [ ] Network errors show user-friendly messages
- [ ] Server errors (500) handled gracefully
- [ ] 404 errors handled (product not found)
- [ ] Retry mechanism works
- [ ] Loading states display correctly

### 7. **Performance**
- [ ] Images load efficiently (use caching)
- [ ] API responses are fast (cached on server)
- [ ] App doesn't freeze during API calls
- [ ] Memory usage is reasonable

---

## 🐛 Common Issues & Solutions

### Issue 1: "Unable to connect to localhost"
**Solution**: Use `10.0.2.2:8000` instead of `localhost:8000` for Android Emulator

### Issue 2: "JSON parsing error"
**Solution**: Ensure data class field names match API response (use `@Json(name = "field_name")` if needed)

### Issue 3: "Images not loading"
**Solution**: 
- Add internet permission in AndroidManifest.xml
- Check Cloudinary URLs are accessible
- Use Coil or Glide for image loading

### Issue 4: "CORS error"
**Solution**: Ensure your app's domain is in `CORS_ALLOWED_ORIGINS` in Django settings

### Issue 5: "Currency not converting"
**Solution**: Send `Currency` header with requests (e.g., "GHS", "USD")

---

## 📚 Additional Resources

- **API Documentation**: See `MOBILE_APP_API_DOCUMENTATION.md`
- **Swagger UI**: `http://localhost:8000/docs-storefront-swagger/`
- **Sentry Monitoring**: Check for API errors in Sentry dashboard
- **GraphQL Alternative**: Available at `/graphql/` if REST API doesn't meet needs

---

## 🎯 Success Criteria

The integration is successful when:
1. ✅ App loads and displays products from the API
2. ✅ Categories and collections load correctly
3. ✅ Product details show all information
4. ✅ Images load from Cloudinary
5. ✅ Search and filtering work
6. ✅ Error handling is robust
7. ✅ No crashes or freezes
8. ✅ Performance is smooth

---

## 📞 Support

If you encounter issues:
1. Check the API documentation
2. Test endpoints using Postman or curl
3. Check Sentry for backend errors
4. Review Django server logs
5. Verify network connectivity

---

## 🚀 Next Steps After Integration

1. Implement cart functionality
2. Add user authentication (JWT)
3. Integrate Hubtel payment gateway
4. Add order management
5. Implement push notifications
6. Add offline support with Room database
