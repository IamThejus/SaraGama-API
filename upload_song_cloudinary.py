import cloudinary
import cloudinary.uploader
from cloudinary.utils import cloudinary_url

# Configuration       
cloudinary.config( 
    cloud_name = "didccssv5", 
    api_key = "232555372445157", 
    api_secret = "ZYO_Bs1d7PdMJfMFZI-P-9w_5Wc", 
    secure=True
)
def upload_song(song_id):
    upload_result = cloudinary.uploader.upload("audio.mp3",public_id=f"song{song_id}",resource_type="video")
    return upload_result["secure_url"]