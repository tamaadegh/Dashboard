# Android Product Detail Implementation Guide

## 🚨 Issue Resolved: 404 Error on Product Detail
The `404 Not Found` error in your logs for `.../retrive_with_image_list/` was due to a missing configuration on the backend. **This has now been fixed.** You can now successfully call this endpoint to get product details along with the full list of images.

**Note on Endpoint Name:** The endpoint uses `retrive_with_image_list` (missing 'e' in retrieve). Please use this exact spelling in your API calls.

---

## 📸 Handling Multiple Product Images

When fetching product details for a page with an image carousel/gallery, use the following endpoint:

**Endpoint:** `GET /product/storefront/api/products/{slug}/retrive_with_image_list/`

**Response Structure:**
```json
{
  "id": 1,
  "texts": {
    "name": "Glass Dining Set",
    "description": "..."
  },
  "slug": "glass-dning-sets",
  "images": [
    {
      "id": 101,
      "image": "https://cloudinary.com/.../image1.jpg",
      "alt_text": "Front view"
    },
    {
      "id": 102,
      "image": "https://cloudinary.com/.../image2.jpg",
      "alt_text": "Side view"
    }
  ],
  "variants": [...]
}
```

---

## 🤖 Prompt for Android Developer

Copy and paste the following prompt to your Android developer/agent to implement the product detail screen correctly:

```markdown
# Task: Implement Product Detail Screen with Image Gallery

## Context
We are building the product detail screen for our E-Commerce app. The previous 404 error when fetching product details has been resolved on the backend.

## Objective
Implement a robust Product Detail screen that fetches data from the API and displays a carousel of product images.

## API Endpoint
Use the specific endpoint that returns the full image list:
- **URL:** `products/{slug}/retrive_with_image_list/` (Note: 'retrive' spelling is correct)
- **Method:** `GET`
- **Headers:** `Currency: GHS` (or desired currency)

## Data Models (Kotlin)

Update your `ProductDetail` data class to include the images list:

```kotlin
data class ProductDetail(
    val id: Int,
    val slug: String,
    val texts: ProductTexts,
    val images: List<ProductImage>, // List of all images
    val variants: List<ProductVariant>,
    val price: String? // Fallback or computed price
)

data class ProductImage(
    val id: Int,
    val image: String, // URL to the image
    val altText: String?
)
```

## Implementation Requirements

1. **Service Method**:
   ```kotlin
   @GET("product/storefront/api/products/{slug}/retrive_with_image_list/")
   suspend fun getProductWithImages(
       @Path("slug") slug: String,
       @Header("Currency") currency: String = "GHS"
   ): Response<ProductDetail>
   ```

2. **Image Carousel**: 
   - Use `HorizontalPager` (Jetpack Compose) or `RecyclerView` (XML) to display images.
   - Use a specialized image loading library like **Coil** or **Glide**.
   - Show a placeholder while loading and an error image if it fails.
   - Implement a page indicator (dots) to show current image position.

3. **Error Handling**:
   - If `images` list is empty, display the `productThumbnail` from the basic product info as a fallback.
   - Handle network errors gracefully with a "Retry" button.

4. **UI Layout**:
   - **Top**: Image Carousel (AspectRatio 1:1 or 4:3)
   - **Middle**: Product Title, Price, and Short Description
   - **Bottom**: "Add to Cart" button (sticky)

## Example Compose Usage (Coil)

```kotlin
@OptIn(ExperimentalFoundationApi::class)
@Composable
fun ProductImageCarousel(images: List<ProductImage>) {
    val pagerState = rememberPagerState(pageCount = { images.size })

    Box {
        HorizontalPager(state = pagerState) { page ->
            AsyncImage(
                model = images[page].image,
                contentDescription = images[page].altText,
                contentScale = ContentScale.Crop,
                modifier = Modifier
                    .fillMaxWidth()
                    .aspectRatio(1f) // Square image
            )
        }
        
        // Page Indicator
        Row(
            Modifier
                .align(Alignment.BottomCenter)
                .padding(bottom = 8.dp)
        ) {
            repeat(images.size) { iteration ->
                val color = if (pagerState.currentPage == iteration) Color.DarkGray else Color.LightGray
                Box(
                    modifier = Modifier
                        .padding(2.dp)
                        .clip(CircleShape)
                        .background(color)
                        .size(8.dp)
                )
            }
        }
    }
}
```
```

---

## 🛠️ Debugging Tips

If you still encounter issues:
1. **Check the Slug**: Ensure `glass-dning-sets` exists in the database.
2. **Verify URL**: It must end with `/` -> `.../retrive_with_image_list/`
3. **Check Logs**: Filter by `OkHttp` to see the raw JSON response.
