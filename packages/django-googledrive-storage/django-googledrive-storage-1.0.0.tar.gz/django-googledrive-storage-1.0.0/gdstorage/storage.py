from apiclient.discovery import build
from apiclient.http import MediaIoBaseUpload
from dateutil.parser import parse
from django.conf import settings
from django.core.files import File
from django.core.files.storage import Storage
import httplib2
from io import BytesIO
import mimetypes 
from oauth2client.client import SignedJwtAssertionCredentials
import os.path
import requests

class GoogleDriveStorage(Storage):
    """
    Storage class for Django that interacts with Google Drive as persistent storage.
    This class uses a system account for Google API that create an application drive 
    (the drive is not owned by any Google User, but it is owned by the application declared on 
    Google API console).
    """
    
    _UNKNOWN_MIMETYPE_ = "application/octet-stream"
    _GOOGLE_DRIVE_FOLDER_MIMETYPE_ = "application/vnd.google-apps.folder"

    def __init__(self, service_email = None, private_key_file = None):
        self._drive_service = None
        try:
            service_email = service_email if service_email is not None else settings.GOOGLE_DRIVE_STORAGE["service_account"]["email"]
            private_key_file = private_key_file if private_key_file is not None else settings.GOOGLE_DRIVE_STORAGE["service_account"]["private_key_file_path"]
            key = None
            
            # Creating a Google Drive Service API using a system account (without OAuth)
            # See https://developers.google.com/drive/web/service-accounts#console_name_project_service_accounts for more info
            private_key_abs_path = "{0}{1}{2}".format(settings.BASE_DIR, os.path.sep, private_key_file)
            if not os.path.exists(private_key_abs_path):
                raise ValueError("Unable to find provided key file")
            else:
                with file(private_key_abs_path, 'rb') as f:
                    key = f.read()
                credentials = SignedJwtAssertionCredentials(
                    service_email,
                    key,
                    scope = "https://www.googleapis.com/auth/drive"
                )
                http = httplib2.Http()
                http = credentials.authorize(http)
                
                self._drive_service = build('drive', 'v2', http=http)
        except KeyError:
            raise ValueError("You must configure properly your settings file. Check Google Drive Storage docs for more info")
        
    def _split_path(self, p):
        """
        Split a complete path in a list of strings
        
        :param p: Path to be splitted
        :type p: string
        :returns: list - List of strings that composes the path
        """
        p = p[1:] if p[0] == '/' else p
        a,b = os.path.split(p)
        return (self._split_path(a) if len(a) and len(b) else []) + [b]
        
    def _get_or_create_folder(self, path, parent_id = None):
        """
        Create a folder on Google Drive. 
        It creates folders recursively.
        If the folder already exists, it retrieves only the unique identifier.
        
        :param path: Path that had to be created
        :type path: string
        :param parent_id: Unique identifier for its parent (folder)
        :type parent_id: string
        :returns: dict
        """
        folder_data = self._check_file_exists(path, parent_id)
        if folder_data is None:
            # Folder does not exists, have to create
            split_path = self._split_path(path)
            current_folder_data = None
            for p in split_path:
                meta_data = {
                    'title': p,
                    'mimeType': self._GOOGLE_DRIVE_FOLDER_MIMETYPE_
                }
                if current_folder_data is not None:
                    meta_data['parents'] = [{'id': current_folder_data['id']}]
                else:
                    # This is the first iteration loop so we have to set the parent_id
                    # obtained by the user, if available
                    if parent_id is not None:
                        meta_data['parents'] = [{'id': parent_id}]
                current_folder_data = self._drive_service.files().insert(body=meta_data).execute()
            return current_folder_data
        else:
            return folder_data
    
    def _check_file_exists(self, filename, parent_id = None):
        """
        Check if a file with specific parameters exists in Google Drive.
        
        :param filename: File or folder to search
        :type filename: string
        :param parent_id: Unique identifier for its parent (folder)
        :type parent_id: string
        :param mime_type: Mime Type for the file to search
        :type mime_type: string
        :returns: dict containing file / folder data if exists or None if does not exists
        """
        split_filename = self._split_path(filename)
        if len(split_filename) > 1:
            # This is an absolute path with folder inside
            # First check if the first element exists as a folder
            # If so call the method recursively with next portion of path
            # Otherwise the path does not exists hence the file does not exists
            q = u"mimeType = '{0}' and title = '{1}'".format(self._GOOGLE_DRIVE_FOLDER_MIMETYPE_, unicode(split_filename[0]))
            if parent_id is not None:
                q = u"{0} and '{1}' in parents".format(q, parent_id)
            max_results = 1000 # Max value admitted from google drive
            folders = self._drive_service.files().list(q=q, maxResults=max_results).execute()
            for folder in folders["items"]:
                if folder["title"] == unicode(split_filename[0]):
                    # Assuming every folder has a single parent
                    return self._check_file_exists(os.path.sep.join(split_filename[1:]), folder["id"])
            return None
        else:
            # This is a file, checking if exists
            q = u"title = '{0}'".format(split_filename[0])
            if parent_id is not None:
                q = u"{0} and '{1}' in parents".format(q, parent_id)
            max_results = 1000 # Max value admitted from google drive
            file_list = self._drive_service.files().list(q=q, maxResults=max_results).execute()
            if len(file_list["items"]) == 0:
                q = u"" if parent_id is None else u"'{0}' in parents".format(parent_id)
                file_list = self._drive_service.files().list(q=q, maxResults=max_results).execute()
                for element in file_list["items"]:
                    if unicode(split_filename[0]) in element["title"]:
                        return element
                return None
            else:
                return file_list["items"][0]
        
    # Methods that had to be implemented
    # to create a valid storage for Django
    
    def _open(self, name, mode='rb'):
        file_data = self._check_file_exists(name)
        r = requests.get(file_data['webContentLink'])
        return File(BytesIO(r.content), name) 
        
     
    def _save(self, name, content):
        folder_path = os.path.sep.join(self._split_path(name)[:-1])
        folder_data = self._get_or_create_folder(folder_path)
        parent_id = None if folder_data is None else folder_data['id']
        # Now we had created (or obtained) folder on GDrive
        # Upload the file
        fd = BytesIO(content.file.read())
        mime_type = mimetypes.guess_type(name)
        if mime_type is None:
            mime_type = self._UNKNOWN_MIMETYPE_
        media_body = MediaIoBaseUpload(fd, mime_type, resumable=True)
        body = {
            'title': name,
            'mimeType': mime_type
        }
        # Set the parent folder.
        if parent_id:
            body['parents'] = [{'id': parent_id}]        
        file_data = self._drive_service.files().insert(
            body=body,
            media_body=media_body).execute()
            
        # Setting up public permission
        public_permission = {
            'type': 'anyone',
            'role': 'reader'
        }
        self._drive_service.permissions().insert(fileId=file_data["id"], body=public_permission).execute()
        
        return file_data[u'originalFilename']
        
    
    def delete(self, name):
        """
        Deletes the specified file from the storage system.
        """
        file_data = self._check_file_exists(name)
        if file_data is not None:
            self._drive_service.files().delete(fileId=file_data['id']).execute()

    def exists(self, name):
        """
        Returns True if a file referenced by the given name already exists in the
        storage system, or False if the name is available for a new file.
        """
        return self._check_file_exists(name) is not None

    def listdir(self, path):
        """
        Lists the contents of the specified path, returning a 2-tuple of lists;
        the first item being directories, the second item being files.
        """
        directories, files = [], []
        folder_data = self._check_file_exists(path)
        if folder_data is not None:
            params = {
                'q':  u"'{0}' in parents".format(folder_data["id"]),
                'maxResults': 1000
            }
            page_token = None
            while True:
                if page_token is not None:
                    params['pageToken'] = page_token
                files_list = self._drive_service.files().list(**params).execute()
                for element in files_list["items"]:
                    if element["mimeType"] == self._GOOGLE_DRIVE_FOLDER_MIMETYPE_:
                        directories.append(os.path.join(path, element["title"]))
                    else:
                        files.append(os.path.join(path, element["title"]))
                page_token = files_list.get('nextPageToken')
                if not page_token:
                    break
        return directories, files

    def size(self, name):
        """
        Returns the total size, in bytes, of the file specified by name.
        """
        file_data = self._check_file_exists(name)
        if file_data is None:
            return 0
        else:
            return file_data["fileSize"]

    def url(self, name):
        """
        Returns an absolute URL where the file's contents can be accessed
        directly by a Web browser.
        """
        file_data = self._check_file_exists(name)
        if file_data is None:
            return None
        else:
            return file_data["webContentLink"]

    def accessed_time(self, name):
        """
        Returns the last accessed time (as datetime object) of the file
        specified by name.
        """
        return self.modified_time(name)

    def created_time(self, name):
        """
        Returns the creation time (as datetime object) of the file
        specified by name.
        """
        file_data = self._check_file_exists(name)
        if file_data is None:
            return None
        else:
            return parse(file_data['createdDate']) 

    def modified_time(self, name):
        """
        Returns the last modified time (as datetime object) of the file
        specified by name.
        """
        file_data = self._check_file_exists(name)
        if file_data is None:
            return None
        else:
            return parse(file_data["modifiedDate"]) 