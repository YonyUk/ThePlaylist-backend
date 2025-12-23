from .upload_download import BackBlazeB2Service

def get_backblazeb2_service():
    service = BackBlazeB2Service()
    try:
        yield service
    finally:
        service = None