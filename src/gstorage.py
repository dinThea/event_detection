from google.cloud import storage
from google.oauth2 import service_account
import json

def download(bucket_name, source_blob_name, destination_file_name):

    """Uploads a file to the bucket."""
    storage_client = storage.Client()
    
    print (bucket_name)
    bucket = storage_client.get_bucket(bucket_name)
    
    blob = bucket.blob(source_blob_name)

    blob.download_to_filename(destination_file_name)

    print('Blob {} downloaded to {}.'.format(
        source_blob_name,
        destination_file_name))