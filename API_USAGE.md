# API Usage Guide

This guide provides detailed examples and best practices for using the Leaflet Product Extractor API.

## Quick Start

### 1. Upload and Extract Products

```python
import requests

# Upload image for extraction
with open('leaflet.jpg', 'rb') as f:
    files = {'file': ('leaflet.jpg', f, 'image/jpeg')}
    response = requests.post('http://localhost:8000/api/v1/extract', files=files)
    
result = response.json()
print(f"Extracted {result['total_products']} products in {result['processing_time_seconds']}s")
```

### 2. List Recent Extractions

```python
import requests

response = requests.get('http://localhost:8000/api/v1/extractions?limit=5')
extractions = response.json()['extractions']

for extraction in extractions:
    print(f"ID: {extraction['extraction_id']}")
    print(f"Products: {extraction['total_products']}")
    print(f"Date: {extraction['timestamp']}")
    print("---")
```

### 3. Get Specific Extraction

```python
import requests

extraction_id = "ext-abc12345"
response = requests.get(f'http://localhost:8000/api/v1/extractions/{extraction_id}')
extraction_data = response.json()['extraction']

# Access product data
for product in extraction_data['products']:
    print(f"Product: {product['name']}")
    print(f"Price: ${product['price']}")
    if product['special_offer']:
        print(f"Offer: {product['special_offer']}")
    print("---")
```

## Advanced Usage

### Error Handling

```python
import requests
from requests.exceptions import RequestException

def extract_products(image_path):
    try:
        with open(image_path, 'rb') as f:
            files = {'file': f}
            response = requests.post(
                'http://localhost:8000/api/v1/extract', 
                files=files,
                timeout=120  # 2 minutes timeout
            )
            
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 400:
            print(f"Bad request: {response.json()['detail']}")
        elif response.status_code == 500:
            print(f"Server error: {response.json()['detail']}")
        else:
            print(f"Unexpected error: {response.status_code}")
            
    except RequestException as e:
        print(f"Network error: {e}")
    except FileNotFoundError:
        print(f"File not found: {image_path}")
    
    return None
```

### Batch Processing

```python
import requests
import os
from concurrent.futures import ThreadPoolExecutor, as_completed

def process_single_image(image_path):
    """Process a single image and return results"""
    try:
        with open(image_path, 'rb') as f:
            files = {'file': (os.path.basename(image_path), f)}
            response = requests.post('http://localhost:8000/api/v1/extract', files=files)
            
        if response.status_code == 200:
            result = response.json()
            return {
                'success': True,
                'image': image_path,
                'products': result['total_products'],
                'time': result['processing_time_seconds'],
                'extraction_id': result.get('extraction_id')
            }
    except Exception as e:
        return {
            'success': False,
            'image': image_path,
            'error': str(e)
        }

def batch_process_images(image_directory, max_workers=3):
    """Process multiple images concurrently"""
    image_files = [
        os.path.join(image_directory, f) 
        for f in os.listdir(image_directory) 
        if f.lower().endswith(('.jpg', '.jpeg', '.png', '.pdf'))
    ]
    
    results = []
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_image = {
            executor.submit(process_single_image, img): img 
            for img in image_files
        }
        
        for future in as_completed(future_to_image):
            result = future.result()
            results.append(result)
            
            if result['success']:
                print(f"✅ {result['image']}: {result['products']} products ({result['time']:.1f}s)")
            else:
                print(f"❌ {result['image']}: {result['error']}")
    
    return results

# Usage
results = batch_process_images('./leaflet_images/', max_workers=2)
successful = [r for r in results if r['success']]
print(f"Processed {len(successful)}/{len(results)} images successfully")
```

### Data Analysis

```python
import requests
import pandas as pd
from datetime import datetime, timedelta

def get_extraction_data(extraction_id):
    """Get full extraction data"""
    response = requests.get(f'http://localhost:8000/api/v1/extractions/{extraction_id}')
    if response.status_code == 200:
        return response.json()['extraction']
    return None

def analyze_pricing_trends(extraction_ids):
    """Analyze pricing trends across multiple extractions"""
    all_products = []
    
    for extraction_id in extraction_ids:
        data = get_extraction_data(extraction_id)
        if data:
            for product in data['products']:
                all_products.append({
                    'extraction_id': extraction_id,
                    'name': product['name'],
                    'price': product['price'],
                    'unit_price': product.get('unit_price'),
                    'special_offer': product.get('special_offer'),
                    'confidence': product['confidence'],
                    'timestamp': data['timestamp']
                })
    
    # Convert to DataFrame for analysis
    df = pd.DataFrame(all_products)
    
    # Basic statistics
    print("Price Statistics:")
    print(df['price'].describe())
    
    # Products with special offers
    offers = df[df['special_offer'].notna()]
    print(f"\nProducts with special offers: {len(offers)}/{len(df)} ({len(offers)/len(df)*100:.1f}%)")
    
    # Most common products
    print("\nMost frequently extracted products:")
    print(df['name'].value_counts().head(10))
    
    return df

# Usage
recent_extractions = requests.get('http://localhost:8000/api/v1/extractions?limit=20').json()
extraction_ids = [e['extraction_id'] for e in recent_extractions['extractions']]
df = analyze_pricing_trends(extraction_ids)
```

## Integration Examples

### Web Application Integration

```javascript
// Frontend JavaScript example
async function uploadAndExtract(imageFile) {
    const formData = new FormData();
    formData.append('file', imageFile);
    
    try {
        const response = await fetch('/api/v1/extract', {
            method: 'POST',
            body: formData,
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const result = await response.json();
        return result;
    } catch (error) {
        console.error('Extraction failed:', error);
        throw error;
    }
}

// Usage with file input
document.getElementById('file-input').addEventListener('change', async (event) => {
    const file = event.target.files[0];
    if (file) {
        try {
            showLoading(true);
            const result = await uploadAndExtract(file);
            displayProducts(result.products);
            showMessage(`Extracted ${result.total_products} products in ${result.processing_time_seconds}s`);
        } catch (error) {
            showError('Failed to extract products. Please try again.');
        } finally {
            showLoading(false);
        }
    }
});
```

### Database Integration

```python
import sqlite3
import requests
from datetime import datetime

class ProductDatabase:
    def __init__(self, db_path='products.db'):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize database schema"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS extractions (
                extraction_id TEXT PRIMARY KEY,
                source_image TEXT,
                timestamp DATETIME,
                total_products INTEGER,
                processing_time REAL
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                extraction_id TEXT,
                product_id TEXT,
                name TEXT,
                price REAL,
                unit_price REAL,
                unit TEXT,
                special_offer TEXT,
                confidence REAL,
                FOREIGN KEY (extraction_id) REFERENCES extractions (extraction_id)
            )
        """)
        
        conn.commit()
        conn.close()
    
    def save_extraction(self, extraction_data):
        """Save extraction results to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Save extraction metadata
        cursor.execute("""
            INSERT OR REPLACE INTO extractions 
            (extraction_id, source_image, timestamp, total_products, processing_time)
            VALUES (?, ?, ?, ?, ?)
        """, (
            extraction_data['extraction_id'],
            extraction_data.get('source_image', ''),
            extraction_data['timestamp'],
            extraction_data['total_products'],
            extraction_data['processing_time_seconds']
        ))
        
        # Save products
        for product in extraction_data['products']:
            cursor.execute("""
                INSERT INTO products 
                (extraction_id, product_id, name, price, unit_price, unit, special_offer, confidence)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                extraction_data['extraction_id'],
                product['id'],
                product['name'],
                product['price'],
                product.get('unit_price'),
                product.get('unit'),
                product.get('special_offer'),
                product['confidence']
            ))
        
        conn.commit()
        conn.close()

# Usage
db = ProductDatabase()

# Process image and save to database
result = extract_products('leaflet.jpg')
if result:
    db.save_extraction(result)
```

## Best Practices

### 1. File Optimization

```python
from PIL import Image
import io

def optimize_image_for_ocr(image_path, max_size=2000):
    """Optimize image for better OCR accuracy"""
    with Image.open(image_path) as img:
        # Convert to RGB if necessary
        if img.mode != 'RGB':
            img = img.convert('RGB')
        
        # Resize if too large
        if max(img.size) > max_size:
            img.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
        
        # Save to bytes for upload
        buffer = io.BytesIO()
        img.save(buffer, format='JPEG', quality=95, optimize=True)
        buffer.seek(0)
        
        return buffer

# Usage
optimized_image = optimize_image_for_ocr('large_leaflet.png')
files = {'file': ('leaflet.jpg', optimized_image, 'image/jpeg')}
response = requests.post('http://localhost:8000/api/v1/extract', files=files)
```

### 2. Monitoring and Logging

```python
import logging
import time
from functools import wraps

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('api_usage.log'),
        logging.StreamHandler()
    ]
)

def monitor_api_calls(func):
    """Decorator to monitor API performance"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            duration = time.time() - start_time
            logging.info(f"API call successful - Duration: {duration:.2f}s")
            return result
        except Exception as e:
            duration = time.time() - start_time
            logging.error(f"API call failed - Duration: {duration:.2f}s - Error: {e}")
            raise
    return wrapper

@monitor_api_calls
def extract_products_monitored(image_path):
    with open(image_path, 'rb') as f:
        files = {'file': f}
        response = requests.post('http://localhost:8000/api/v1/extract', files=files)
        response.raise_for_status()
        return response.json()
```

### 3. Rate Limiting and Retry Logic

```python
import time
import random
from functools import wraps

def retry_with_backoff(max_retries=3, base_delay=1):
    """Retry decorator with exponential backoff"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except requests.exceptions.RequestException as e:
                    if attempt == max_retries - 1:
                        raise
                    
                    delay = base_delay * (2 ** attempt) + random.uniform(0, 1)
                    logging.warning(f"Attempt {attempt + 1} failed: {e}. Retrying in {delay:.1f}s")
                    time.sleep(delay)
        return wrapper
    return decorator

@retry_with_backoff(max_retries=3)
def robust_extract_products(image_path):
    """Extract products with automatic retry on failure"""
    with open(image_path, 'rb') as f:
        files = {'file': f}
        response = requests.post('http://localhost:8000/api/v1/extract', files=files)
        response.raise_for_status()
        return response.json()
```

## Response Examples

### Successful Extraction Response

```json
{
  "success": true,
  "message": "Successfully extracted 8 products",
  "products": [
    {
      "id": "prod-a1b2c3d4",
      "name": "Organic Bananas",
      "description": "Premium quality organic bananas",
      "price": 3.99,
      "unit_price": 2.50,
      "unit": "per kg",
      "currency": "AUD",
      "special_offer": "2 for $6",
      "position": {
        "x": 120,
        "y": 85,
        "width": 180,
        "height": 65
      },
      "confidence": 0.94
    }
  ],
  "total_products": 8,
  "processing_time_seconds": 4.2,
  "json_file": "data/output/products_20241218_143052_a1b2c3d4.json",
  "extraction_id": "ext-a1b2c3d4",
  "timestamp": "2024-12-18T14:30:52.123456"
}
```

### Error Response

```json
{
  "success": false,
  "message": "Invalid file format",
  "error_code": "INVALID_FILE_FORMAT",
  "details": {
    "allowed_formats": [".jpg", ".jpeg", ".png", ".pdf"],
    "received_format": ".gif",
    "max_file_size": "10MB"
  }
}
```

For more information, visit the interactive API documentation at `http://localhost:8000/docs`.