from apiclient import discovery
from httplib2 import Http
from oauth2client import file, client, tools
import uuid

SCOPES = 'https://www.googleapis.com/auth/drive'

store = file.Storage('storage.json')
creds = store.get()
if not creds or creds.invalid:
    flow = client.flow_from_clientsecrets('client_secret.json', SCOPES)
    creds = tools.run_flow(flow, store)
DRIVE = discovery.build('drive', 'v3', http=creds.authorize(Http()))

# map_size = input("Enter no. of mappings : ")
# print("Enter mappings : \n")
# map_dict = dict(input().split() for _ in range(int(map_size)))
# print(map_dict)

map_dict = {'Department1': 'test-product1-dept1-group@example.com', 
            'Department2': 'test-product1-dept2-group@example.com'}

def search(query):
    result = []
    page_token = None
    while True:
        response = DRIVE.files().list(q=query,
                                        spaces="drive",
                                        pageToken=page_token).execute()
        
        for file in response.get("files", []):
            result.append((file["id"], file["name"], file["mimeType"]))
        
        page_token = response.get('nextPageToken', None)
        if not page_token:
            break
    return result

def add_user(td_id, user, role='writer'):
    body = {'type': 'user', 'role': role, 'emailAddress': user}
    return DRIVE.permissions().create(body=body, fileId=td_id,
            supportsTeamDrives=True, fields='id').execute().get('id')

FOLDER_MIME = 'application/vnd.google-apps.folder'

print("\nFolders in Drive : \n")
search_results = search(query=f"mimeType='{FOLDER_MIME}'")
for search_result in search_results:
    print(search_result[0], search_result[1])

parent_id = input("\n\nEnter Id. of Root Folder : ")

search_results = search(query=f"mimeType='{FOLDER_MIME}' and '{parent_id}' in parents"  )
for search_result in search_results:
    print(search_result[0], search_result[1])
    rec_search_results = search(query=f"mimeType='{FOLDER_MIME}' and '{search_result[0]}' in parents"  )
    for rec_search_result in rec_search_results:
        print("\t|------ "+rec_search_result[0], rec_search_result[1])
        if  rec_search_result[1] in map_dict:
            add_user(rec_search_result[0], map_dict[rec_search_result[1]])
            print("\t\taccess given to : "+map_dict[rec_search_result[1]])
