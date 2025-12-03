"""
File upload utilities with optional Supabase support.
Falls back to Django default storage when Supabase SDK is unavailable
or not configured.
"""

import uuid
import os
from django.conf import settings
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile

try:
    from supabase import create_client, Client  # type: ignore
except Exception:
    create_client = None
    Client = None
 
 
def get_supabase_client(use_service_key: bool = False):
    """Initialize Supabase client, preferring env-configured URL if available."""
    if not create_client:
        return None
    project_ref = "egllznsxjgkhnwexidii"
    # Prefer explicit URL from settings/env; otherwise fall back to project_ref
    url = (
        getattr(settings, "SUPABASE_URL", None)
        or os.environ.get("SUPABASE_URL")
        or f"https://{project_ref}.supabase.co"
    )

    # Choose service key for backend uploads, anon key otherwise
    if use_service_key:
        key = os.environ.get("SUPABASE_KEY_SERVICE") or getattr(settings, "SUPABASE_KEY_SERVICE", "")
    else:
        key = os.environ.get("SUPABASE_KEY") or getattr(settings, "SUPABASE_KEY", "")

    try:
        return create_client(url, key)
    except Exception:
        return None
 
 
 
def upload_to_supabase(file, bucket_name='user-uploads', folder=''):
    """
    Upload file to Supabase Storage
   
    Args:
        file: Django UploadedFile object
        bucket_name: Name of the Supabase storage bucket (default: 'user-uploads')
        folder: Optional folder path within the bucket (e.g., 'profile-photos')
   
    Returns:
        str: Public URL of the uploaded file, or None if upload fails
    """
    try:
        supabase = get_supabase_client(use_service_key=True)

        ext = file.name.split('.')[-1].lower() if '.' in file.name else 'jpg'
        unique_id = uuid.uuid4().hex
        filename = f"{folder}/{unique_id}.{ext}" if folder else f"{unique_id}.{ext}"

        file.seek(0)
        file_bytes = file.read()
        content_type = getattr(file, 'content_type', 'application/octet-stream')

        if supabase:
            supabase.storage.from_(bucket_name).upload(
                filename,
                file_bytes,
                file_options={"content-type": content_type}
            )
            public_url = supabase.storage.from_(bucket_name).get_public_url(filename)
            return public_url

        # Fallback: save to local MEDIA storage
        media_path = os.path.join(folder or '', f"{unique_id}.{ext}")
        default_storage.save(media_path, ContentFile(file_bytes))
        return settings.MEDIA_URL.rstrip('/') + '/' + media_path.replace('\\', '/')

    except Exception as e:
        print(f"Error uploading file: {e}")
        try:
            import traceback
            traceback.print_exc()
        except Exception:
            pass
        return None
 
 
def delete_from_supabase(file_url, bucket_name='user-uploads'):
    """
    Delete file from Supabase Storage
   
    Args:
        file_url: Full public URL of the file to delete
        bucket_name: Name of the Supabase storage bucket
   
    Returns:
        bool: True if deletion successful, False otherwise
    """
    try:
        if not file_url:
            return False

        supabase = get_supabase_client(use_service_key=True)

        if supabase and '/object/public/' in file_url:
            parts = file_url.split('/object/public/')
            if len(parts) == 2:
                path_parts = parts[1].split('/', 1)
                if len(path_parts) == 2:
                    filename = path_parts[1]
                    supabase.storage.from_(bucket_name).remove([filename])
                    return True

        # Fallback: try deleting from local MEDIA storage
        try:
            if file_url.startswith(settings.MEDIA_URL):
                relative_path = file_url[len(settings.MEDIA_URL):].lstrip('/')
                default_storage.delete(relative_path)
                return True
        except Exception:
            pass

        return False

    except Exception as e:
        print(f"Error deleting file: {e}")
        return False
 
