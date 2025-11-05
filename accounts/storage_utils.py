# accounts/storage_utils.py
from supabase import create_client, Client
from django.conf import settings
import uuid

def get_supabase_client() -> Client:
    """Initialize Supabase client"""
    url = settings.SUPABASE_URL
    key = settings.SUPABASE_KEY
    return create_client(url, key)

def upload_to_supabase(file, bucket_name='user-uploads', folder=''):
    """
    Upload file to Supabase Storage
    Returns the public URL of the uploaded file
    """
    try:
        supabase = get_supabase_client()
        
        # Generate unique filename
        ext = file.name.split('.')[-1]
        filename = f"{folder}/{uuid.uuid4()}.{ext}" if folder else f"{uuid.uuid4()}.{ext}"
        
        # Upload file
        file_bytes = file.read()
        supabase.storage.from_(bucket_name).upload(
            filename,
            file_bytes,
            file_options={"content-type": file.content_type}
        )
        
        # Get public URL
        url = supabase.storage.from_(bucket_name).get_public_url(filename)
        
        return url
    except Exception as e:
        print(f"Error uploading to Supabase: {e}")
        return None