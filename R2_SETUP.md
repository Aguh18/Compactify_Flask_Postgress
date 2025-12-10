# Cloudflare R2 Setup Guide

This application uses Cloudflare R2 for all file storage operations. Follow this guide to set up R2.

## 1. Create Cloudflare R2 Bucket

1. Login to [Cloudflare Dashboard](https://dash.cloudflare.com)
2. Go to **R2 Object Storage** (under Storage)
3. Click **"Create bucket"**
4. Enter bucket name (e.g., `compactify-storage`)
5. Select region (default is fine)
6. Click **"Create bucket"**

## 2. Create R2 API Token

### Option A: Using R2 API Tokens (Recommended)

1. In R2 dashboard, go to **"Manage R2 API tokens"**
2. Click **"Create API token"**
3. Give token a name (e.g., `compactify-app`)
4. Select permissions:
   - ✅ **Object Read**
   - ✅ **Object Write**
   - ✅ **Object Delete**
5. Select your bucket
6. Set TTL (Time To Live) as needed
7. Click **"Create API token"**
8. **Save the token** - you won't be able to see it again

### Option B: Using Account API Token

1. Go to **"My Profile"** → **"API Tokens"**
2. Click **"Create Token"**
3. Click **"Custom token"**
4. Set permissions:
   - **Account** → **Cloudflare R2:Edit**
5. Set **Account Resources** → **All accounts** or select your account
6. Click **"Continue to summary"**
7. Click **"Create Token"**

## 3. Update .env File

Update your `.env` file with the R2 credentials:

```bash
# Cloudflare R2 Storage
R2_ACCOUNT_ID=12345abcdef67890  # Your Cloudflare Account ID
R2_ACCESS_KEY_ID=abcd1234efgh5678  # Your R2 API Token ID
R2_SECRET_ACCESS_KEY=secret123456789  # Your R2 API Token Secret
R2_BUCKET_NAME=compactify-storage  # Your bucket name
R2_PUBLIC_URL=https://compactify-storage.12345abcdef67890.r2.cloudflarestorage.com
```

### Finding Your Values

**Account ID:**
- In Cloudflare dashboard, right sidebar shows **Account ID**

**Access Key ID & Secret:**
- From the API token you created in step 2

**Bucket Name:**
- The bucket name you created in step 1

**Public URL:**
- Format: `https://{bucket-name}.{account-id}.r2.cloudflarestorage.com`
- Example: `https://compactify-storage.12345abcdef67890.r2.cloudflarestorage.com`

## 4. Optional: Set up Custom Domain

For production use, you may want to set up a custom domain:

1. In R2 dashboard, select your bucket
2. Go to **"Settings"** → **"Custom Domains"**
3. Click **"Connect Custom Domain"**
4. Enter your domain (e.g., `files.yourdomain.com`)
5. Follow the DNS setup instructions

Then update `.env`:
```bash
R2_PUBLIC_URL=https://files.yourdomain.com
```

## 5. Test the Setup

```bash
# Activate virtual environment
source venv/bin/activate

# Run the application
python server.py

# The app should start without R2 configuration errors
```

If you see errors about missing R2 configuration, double-check your `.env` file values.

## 6. R2 Features Used

This application uses these R2 features:

### Storage Operations
- **Upload**: Store uploaded files
- **Download**: Retrieve files for processing
- **Delete**: Clean up temporary files
- **Move**: Organize processed files

### Folder Structure
Files are organized by feature:
```
compressimg/
├── uploads/        # Original uploaded images
├── downloads/      # Compressed images
└── processed/      # Processed files

imagetopdf/
├── uploads/        # Original images
└── downloads/      # Generated PDFs

# ... etc for other features
```

## 7. Monitoring and Billing

### Check Storage Usage
- In Cloudflare dashboard → R2 → Select bucket
- View storage usage and operations

### Billing
- R2 has free tier: 10GB storage + 1M Class A operations/month
- After free tier: $0.015/GB-month + $4.50/M Class A operations
- Check [R2 Pricing](https://www.cloudflare.com/products/r2/pricing/)

## 8. Troubleshooting

### Common Issues

**1. "Invalid endpoint" Error**
- Check your Account ID is correct
- Remove any spaces from Account ID

**2. "Access Denied" Error**
- Verify API token has correct permissions
- Check bucket name matches exactly
- Ensure Access Key ID and Secret are correct

**3. "Bucket not found" Error**
- Verify bucket exists in your R2 account
- Check bucket name spelling

**4. Connection Timeout**
- Check your internet connection
- Verify firewall allows AWS S3 API calls

### Debug Mode

Enable debug logging by updating `.env`:
```bash
DEBUG=True
FLASK_ENV=development
```

## 9. Security Best Practices

1. **Never commit API keys** to version control
2. **Use environment variables** for all credentials
3. **Set appropriate TTL** on API tokens
4. **Use least-privilege permissions** for tokens
5. **Regularly rotate API tokens**
6. **Monitor bucket access logs**

## 10. Environment-Specific Configuration

### Development
```bash
# Use development bucket
R2_BUCKET_NAME=compactify-dev-storage
```

### Production
```bash
# Use production bucket with custom domain
R2_BUCKET_NAME=compactify-prod-storage
R2_PUBLIC_URL=https://files.yourdomain.com
```

### Testing
```bash
# Use separate bucket for automated tests
R2_BUCKET_NAME=compactify-test-storage
```

---

For more information about Cloudflare R2:
- [R2 Documentation](https://developers.cloudflare.com/r2/)
- [R2 API Documentation](https://developers.cloudflare.com/r2/api/)
- [Cloudflare Dashboard](https://dash.cloudflare.com/r2)