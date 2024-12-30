from abc import ABC,abstractmethod
from typing import Optional, List
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ColoredFormatter(logging.Formatter):
    COLORS = {
        'DEBUG': '\033[94m',  # Blue
        'INFO': '\033[92m',   # Green
        'WARNING': '\033[93m',  # Yellow
        'ERROR': '\033[91m',   # Red
        'CRITICAL': '\033[95m'  # Magenta
    }

    def format(self, record):
        color = self.COLORS.get(record.levelname, '')
        message = logging.Formatter.format(self, record)
        reset = '\033[0m'
        return f"{color}{message}{reset}"

console_handler = logging.StreamHandler()
console_handler.setFormatter(ColoredFormatter())
logger.addHandler(console_handler)



class AzureStorage(ABC):
    @abstractmethod
    def __init__(self,connection_string:str):
        self.connection_string = connection_string
        self.blob_service_client: Optional[BlobServiceClient] = None
        self.container_client: Optional[ContainerClient] = None
        self.blob_client: Optional[BlobClient] = None

    @abstractmethod
    def configure_clients(self):
        ...

    @abstractmethod
    def create_container(self,container_name:str):
        ...

    @abstractmethod
    def delete_container(self,container_name:str):
        ...

    @abstractmethod
    def download_blob(self,container_name:str,blob_name:str,download_path:str):
        ...

    @abstractmethod
    def list_blobs(self,container_name:str):
        ...

    @abstractmethod
    def delete_blob(self,container_name:str,blob_name:str):
        ...

    @abstractmethod
    def get_blob_properties(self,container_name:str,blob_name):
        ...

    @abstractmethod
    def set_blob_metadata(self,container_name:str,blob_name:str,metadata:dict):
        ...

    @abstractmethod
    def stream_blob_part(self,container_name:str,blob_name:str,start_byte:int,end_byte:int):
        ...

    @abstractmethod
    def stream_blob_full(self, container_name: str, blob_name: str):
        ...


class AzureBlobStorage(AzureStorage):
    def __init__(self, connection_string: str):
        super().__init__(connection_string)
        self.configure_clients()

    def configure_clients(self):
        self.blob_service_client = BlobServiceClient.from_connection_string(self.connection_string)
        self.container_client = None
        self.blob_client = None

    def create_container(self, container_name: str):
        container_client = self.blob_service_client.create_container(container_name)
        logger.info(f"Container '{container_name}' created successfully.")

    def delete_container(self, container_name: str):
        container_client = self.blob_service_client.get_container_client(container_name)
        container_client.delete_container()
        logger.info(f"Container '{container_name}' deleted successfully.")

    def upload_blob(self, container_name: str, blob_name: str,file_path:str):
        os.chdir('../')
        path_object = os.path.join(file_path)
        path_object_abs = os.path.abspath(path_object)
        self.container_client = self.blob_service_client.get_container_client(container_name)
        self.blob_client = self.container_client.get_blob_client(blob_name)
        with open(path_object_abs, "rb") as data:
            self.blob_client.upload_blob(data)
        logger.info(f"Blob '{blob_name}' uploaded successfully to container '{container_name}'.")

    def download_blob(self, container_name: str, blob_name: str, download_path: str,**kwargs):
        self.container_client = self.blob_service_client.get_container_client(container_name)
        self.blob_client = self.container_client.get_blob_client(blob_name)
        with open(download_path, "wb") as download_file:
            download_file.write(self.blob_client.download_blob().readall())
        logger.info(f"Blob '{blob_name}' downloaded successfully from container '{container_name}'.")

    def list_blobs(self, container_name: str) -> List[str]:
        self.container_client = self.blob_service_client.get_container_client(container_name)
        blob_list = self.container_client.list_blobs()
        return [blob.name for blob in blob_list]

    def delete_blob(self, container_name: str, blob_name: str):
        self.container_client = self.blob_service_client.get_container_client(container_name)
        self.blob_client = self.container_client.get_blob_client(blob_name)
        self.blob_client.delete_blob()
        logger.info(f"Blob '{blob_name}' deleted successfully from container '{container_name}'.")

    def blob_exists(self, container_name: str, blob_name: str) -> bool:
        self.container_client = self.blob_service_client.get_container_client(container_name)
        self.blob_client = self.container_client.get_blob_client(blob_name)
        return self.blob_client.exists()

    def get_blob_properties(self, container_name: str, blob_name: str):
        self.container_client = self.blob_service_client.get_container_client(container_name)
        self.blob_client = self.container_client.get_blob_client(blob_name)
        return self.blob_client.get_blob_properties()

    def set_blob_metadata(self, container_name: str, blob_name: str, metadata: dict):
        self.container_client = self.blob_service_client.get_container_client(container_name)
        self.blob_client = self.container_client.get_blob_client(blob_name)
        self.blob_client.set_blob_metadata(metadata)
        logger.info(f"Metadata for blob '{blob_name}' updated successfully.")

    def stream_blob_part(self,container_name:str,blob_name:str,start_byte:int,end_byte:int):
        self.container_client = self.blob_service_client.get_container_client(container_name)
        self.blob_client = self.container_client.get_blob_client(blob_name)
        byte_data = self.blob_client.download_blob(offset=start_byte, length=end_byte - start_byte + 1)
        data = byte_data.readall()
        logger.info(f'Blob streaming part')
        return data
    def stream_blob_full(self, container_name: str, blob_name: str):
        self.container_client = self.blob_service_client.get_container_client(container_name)
        self.blob_client = self.container_client.get_blob_client(blob_name)
        byte_data = self.blob_client.download_blob()
        data = byte_data.readall()
        logger.info(f'Blob streaming full')
        return data



# TESTING
# azure_instance = AzureBlobStorage(connection_string=connection_string)
# azure_instance.create_container('ultimate')
# print(azure_instance.list_blobs('ultimate'))
# azure_instance.upload_blob('ultimate','egg/second.py','oauth/api.py')
# azure_instance.download_blob('ultimate','first.py','text.py')
# azure_instance.delete_blob('ultimate','first.py')
# print(azure_instance.list_blobs('ultimate'))

# TODO: add a max podcast size,proper file validation,add a uuid as blob name
# TODO: structure database properly