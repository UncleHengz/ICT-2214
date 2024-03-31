
import requests
import os
import tarfile
from bs4 import BeautifulSoup
import firebase_admin
from firebase_admin import credentials, storage, initialize_app

#https://console.firebase.google.com/u/0/project/phishingapi-8d5c4/database/phishingapi-8d5c4-default-rtdb/data/~2F


# Initialize Firebase Admin SDK
cred = credentials.Certificate("phishingapi-8d5c4-firebase-adminsdk-8j7mc-70eda65366.json")
firebase_admin.initialize_app(cred, {
    'storageBucket': 'phishingapi-8d5c4.appspot.com'
})
config = {
    "apiKey": "AIzaSyAk7wD-n4lJ8gHPOVlWpFD9xw8qwHvMILE",
    "authDomain": "phishingapi-8d5c4.firebaseapp.com",
    "databaseURL": "https://phishingapi-8d5c4-default-rtdb.asia-southeast1.firebasedatabase.app",
    "projectId": "phishingapi-8d5c4",
    "storageBucket": "phishingapi-8d5c4.appspot.com",
    "messagingSenderId": "433310396902",
    "appId": "1:433310396902:web:ec98c81f6da58c7c86e627",
    "measurementId": "G-R6WJTX9XSL"
}
def download_file():
    file_url = 'https://raw.githubusercontent.com/mitchellkrogza/Phishing.Database/master/ALL-phishing-links.tar.gz'
    try:
        response = requests.get('https://raw.githubusercontent.com/mitchellkrogza/Phishing.Database/master/ALL-phishing-links.tar.gz', stream=True)
        print(response)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        return f"Error downloading file: {str(e)}",file_url
    filename = os.path.basename(file_url)

    temp_file_path = f'{filename}'
    if os.path.exists(f'{filename}'):
        os.remove(f'{filename}')

    with open(temp_file_path, 'wb') as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)
        f.close()

    extractdir = "./Links"
    if not os.path.exists(extractdir):
        os.makedirs(extractdir)
    try:
        with tarfile.open(filename,'r') as tar:
            tar.extractall(path=extractdir)
            tar.close()
        print(f"Successfully extracted")
    except Exception as e:
        print(f"Error extracting")
    files_list = []
    for filenamez in os.listdir(extractdir):
        files_list.append(filenamez)
    try:
        # Get a reference to the storage service
        bucket = storage.bucket()


        # Get the blob to delete
        blob = bucket.blob(files_list[0])

        # Delete the blob
        blob.delete()

        print(f"File {files_list[0]} deleted successfully.")
    except Exception as e:
        print(f"Error deleting file {files_list[0]}: {str(e)}")
    bucket = storage.bucket()
    blob = bucket.blob(files_list[0])
    blob.upload_from_filename('./Links/'+files_list[0])
    blob.make_public()
    print(blob.public_url)
    return temp_file_path

def database_file():
    extractdir = "./FireBase_Data"
    local_filepath = "./Links"
    files_list = []
    for filenamez in os.listdir(local_filepath):
        files_list.append(filenamez)
    if not os.path.exists(extractdir):
        os.makedirs(extractdir)
    print(extractdir)
    try:
        # Get a reference to the storage service
        bucket = storage.bucket()

        # Specify the file path in Firebase Storage
        blob = bucket.blob(files_list[0])

        # Download the file to a temporary location

        blob.download_to_filename(extractdir+'/'+files_list[0])
        return local_filepath

    except Exception as e:
        return extractdir



if __name__ == '__main__':
    download_file()
    database_file()
