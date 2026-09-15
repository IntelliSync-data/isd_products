# ISD Product Service

Centralized Product Service for the ISD Platform ecosystem.

## Features

- **Image, Video, File & External URL products** - Upload, organize, and serve product assets (Facebook/YouTube links supported)
- **Dual Storage** - Local filesystem or Amazon S3 (extensible to MinIO, Cloudflare R2, Azure Blob, etc.)
- **REST API** - Public API for Portal, PhotoApp, Mobile App, and external systems
- **Category & Tag** - Organize products with categories and tags
- **Publish Scheduling** - Control when a product is visible via publish from/to dates
- **Version API** - Cache optimization for client applications
- **Origin Control** - Restrict API access by domain
- **Video Thumbnails** - Auto-generated with ffmpeg (up to 512px), with a "Regenerate Thumbnail" button for existing videos

## Architecture

```
Controller → Service → Storage Provider → ORM/Filesystem
```

### Storage Provider Pattern

Extensible storage via abstract base class:

```
StorageProvider (abstract)
├── LocalStorageProvider
├── S3StorageProvider
└── (future: MinIO, R2, Azure, GCS...)
```

## REST API

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/products/categories` | List active categories |
| GET | `/api/v1/products` | List active, visible, published products (paginated, `page`, `limit`, `categoryId`) |
| GET | `/api/v1/products/version` | Get data version for cache check |
| PUT | `/api/v1/products/<id>` | Edit a product (see below) |

The list API returns `description` but never `note` (internal only).

### Edit Product (PUT)

Protected by origin only: the request **must** send an `Origin` header that matches one of the
Allowed Origins in Settings, otherwise it gets `403`. If no Allowed Origins are configured, every
PUT request is rejected. CORS is enforced by browsers only — server-side clients (curl, Postman,
scripts) can set any `Origin` header, so do not rely on this for sensitive data.

Body is a JSON object with any subset of these fields:

| Field | Type |
|-------|------|
| `name`, `description`, `note` | string or `null` |
| `is_visible` | boolean |
| `sort_order` | integer |
| `display_size` | `small` / `medium` / `large` |
| `category_ids` | list of category ids (cannot be empty) |
| `tag_ids` | list of tag ids |
| `publish_from`, `publish_to` | ISO datetime string (e.g. `2026-01-31T09:00:00Z`) or `null` |

```bash
curl -X PUT https://<domain>/api/v1/products/42 \
  -H "Origin: https://your-site.com" \
  -H "Content-Type: application/json" \
  -d '{"description": "New description", "is_visible": false}'
```

Unknown fields, wrong types or unknown ids return `400`. Response `data` is the updated product,
including `note` and `is_visible`.

### File Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/isd_products/file/<storage_key>` | Serve a locally stored file (`?download=1` to force download) |
| GET | `/isd_products/thumbnail/<id>` | Serve a product thumbnail |

### Response Format

```json
{
    "success": true,
    "code": 200,
    "message": "",
    "meta": {"page": 1, "limit": 20, "total": 58},
    "data": [...]
}
```

## Menu Structure

```
Products (by ISD)
├── Products          /odoo/isd-products
├── Categories        /odoo/isd-product-categories
├── Tags              /odoo/isd-product-tags
└── Configuration     /odoo/isd-product-settings   (Admin only)
```

## Security Groups

- **Product User** - Upload products, manage categories and tags
- **Product Administrator** - Full access including configuration

## Configuration

All settings stored in `ir.config_parameter` under the `isd_products.` prefix:

- Storage provider (Local/S3)
- S3 credentials and bucket config
- Upload size limits (Image/Video/File)
- Product count limits (warning only)
- API maximum return count
- Allowed origins for CORS

## Requirements

- Odoo 18 Community
- `boto3` (only if using S3 storage)
- `ffmpeg` (optional, for video thumbnail generation)

## Installation

1. Place `isd_products` in your Odoo addons path
2. Update apps list
3. Install "Product Service (by ISD)"
4. Configure storage provider in Products > Configuration

## Deployment

Push to a customer branch; GitHub Actions deploys over SSH, runs `-u isd_products`, and restarts Odoo.

| Branch | Workflow | Addons destination |
|--------|----------|--------------------|
| `bloompod` | `.github/workflows/bloompod.yml` | `~/custom-addons/isd_products` |
| `vfo` | `.github/workflows/vfo.yml` | `/opt/custom-addons/isd_products` |

`main` has no deploy workflow.
