import logging
from django.conf import settings

logger = logging.getLogger(__name__)

log_file_path = settings.LOGGING['handlers']['file']['filename']

logging.basicConfig(
    filename=log_file_path,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)