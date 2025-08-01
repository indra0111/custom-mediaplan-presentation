import json
import unicodedata
import regex
# from google.oauth2 import service_account
from googleapiclient.discovery import build
from datetime import datetime
import os
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from genai_mediaplan.utils.update_charts import update_charts_in_slides
from genai_mediaplan.utils.persona import update_persona_content

# Set up credentials
# SERVICE_ACCOUNT_FILE = 'service_account.json'
SCOPES = ['https://www.googleapis.com/auth/drive']
CLIENT_SECRET_FILE = 'client_secret_drive.json'
TOKEN_FILE = 'token.json'
SOURCE_FILE_ID = "1H5Z-R_MXR4taxg1UC1cOr3AjEDaThPIR7tkLEdJaPTE"
GEO_SLIDE_INDEX = 6

creds = None
if os.path.exists(TOKEN_FILE):
    creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    else:
        flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET_FILE, SCOPES)
        creds = flow.run_local_server(port=0)
    # Save token for future use
    with open(TOKEN_FILE, 'w') as token:
        token.write(creds.to_json())
        
drive_service = build('drive', 'v3', credentials=creds)
slides_service = build('slides', 'v1', credentials=creds)

audience_forecast = {
    "TIL_All_Cluster_RNF": {
        "title": "Cluster",
        "data": {
            "India": {
                "user": "5.8\nUser Reach (Reach fcap-1)",
                "impr": "1.2\nTargetable Impressions (Impressions fcap-3)",
            },
            "Delhi": {
                "user": "delhi\nUser Reach (Reach fcap-1)",
                "impr": "delhi\nTargetable Impressions (Impressions fcap-3)",
            },
            "Mumbai": {
                "user": "mumbai\nUser Reach (Reach fcap-1)",
                "impr": "mumbai\nTargetable Impressions (Impressions fcap-3)",
            },
            "Kolkata": {
                "user": "kolkata\nUser Reach (Reach fcap-1)",
                "impr": "kolkata\nTargetable Impressions (Impressions fcap-3)",
            }
        }
    },
    "TIL_All_Languages_RNF": {
        "title": "Languages",
        "data": {
            "India": {
                "user": "user\nUser Reach (Reach fcap-1)",
                "impr": "impr\nTargetable Impressions (Impressions fcap-3)",
            },
            "Delhi": {
                "user": "delhi\nUser Reach (Reach fcap-1)",
                "impr": "delhi\nTargetable Impressions (Impressions fcap-3)",
            },
            "Mumbai": {
                "user": "mumbai\nUser Reach (Reach fcap-1)",
                "impr": "mumbai\nTargetable Impressions (Impressions fcap-3)",
            },
            "Kolkata": {
                "user": "kolkata\nUser Reach (Reach fcap-1)",
                "impr": "kolkata\nTargetable Impressions (Impressions fcap-3)",
            }
        }
    },
}
    
geo_name_mapping = {
    "TIL_All_Cluster_RNF": "TIL All Cluster Standard Banner (30 days)",
    "TIL_All_Languages_RNF": "TIL All Languages Standard Banner (30 days)",
    "TIL_TOI_Only_RNF": "TOI Only - Premium English Audience (30 Days)",
    "TIL_ET_And_TOI_RNF": "ET+TOI- Premium English + Business & Finance Convergence (30days)",
    "TIL_ET_Only_RNF": "Economic Times Only - Business & Finance Audience (30 Days)",
    "TIL_NBT_Only_RNF": "Navbharat - Hindi Market Leadership (30days)",
    "TIL_MT_Only_RNF": "TIL MT Standard Banner (30 days)",
    "TIL_VK_Only_RNF": "TIL VK Standard Banner (30 days)",
    "TIL_IAG_Only_RNF": "TIL IAG Standard Banner (30 days)",
    "TIL_EIS_Only_RNF": "TIL EIS Standard Banner (30 days)",
    "TIL_Tamil_Only_RNF": "TIL Tamil Standard Banner (30 days)",
    "TIL_Telugu_Only_RNF": "TIL Telugu Standard Banner (30 days)",
    "TIL_Malayalam_Only_RNF": "TIL Malayalam Standard Banner (30 days)",
}
    
def build_replace_text_requests(object_id, row_index, col_index, text):
    # Only use insertText to avoid deleteText issues
    return [
        {
            "deleteText": {
                "objectId": object_id,
                "cellLocation": {
                    "rowIndex": row_index,
                    "columnIndex": col_index
                },
                "textRange": {
                    "type": "ALL"
                }
            }
        },
        {
            "insertText": {
                "objectId": object_id,
                "cellLocation": {
                    "rowIndex": row_index,
                    "columnIndex": col_index
                },
                "insertionIndex": 0,
                "text": text
            }
        }
    ]

def update_table_with_dynamic_rows(slides_service, presentation_id, slide_index, data_rows):
    requests = []

    # Load the presentation and slide
    presentation = slides_service.presentations().get(presentationId=presentation_id).execute()
    slide = presentation['slides'][slide_index]

    for element in slide.get('pageElements', []):
        if element.get('description') == 'geo_table' and 'table' in element:
            table = element['table']
            object_id = element['objectId']
            table_rows = table['tableRows']
            existing_row_count = len(table_rows)
            data_row_count = len(data_rows)
            column_count = len(data_rows[0]) if data_rows else 0

            # Adjust table size
            if data_row_count + 1 < existing_row_count:  # +1 for header
                for i in range(existing_row_count - 1, data_row_count, -1):
                    requests.append({
                        "deleteTableRow": {
                            "tableObjectId": object_id,
                            "cellLocation": {
                                "rowIndex": i
                            }
                        }
                    })
            elif data_row_count + 1 > existing_row_count:
                for _ in range(data_row_count - (existing_row_count - 1)):
                    requests.append({
                        "insertTableRow": {
                            "tableObjectId": object_id,
                            "insertBelow": True,
                            "rowIndex": existing_row_count - 1,
                            "rowCount": 1
                        }
                    })
                    existing_row_count += 1

            # Reload table to get updated structure
            presentation = slides_service.presentations().get(presentationId=presentation_id).execute()
            slide = presentation['slides'][slide_index]
            for elem in slide['pageElements']:
                if elem.get('description') == 'geo_table' and 'table' in elem:
                    table = elem['table']
                    break

            # Replace cell content
            for r, row_data in enumerate(data_rows):
                for c, value in enumerate(row_data):
                    try:
                        requests.extend(build_replace_text_requests(object_id, r + 1, c, str(value)))
                    except Exception as e:
                        print(f"Error updating cell [{r + 1}][{c}]:", e)

    return requests



def update_geo_title(slides_service, presentation_id, slide_index_to_paste, title):
    requests = []
    presentation = slides_service.presentations().get(presentationId=presentation_id).execute()
    slide = presentation['slides'][slide_index_to_paste]
    for element in slide.get('pageElements', []):
        if 'shape' in element:
            shape = element['shape']
            alt_text = element.get('description', '')
            if alt_text == 'geo_title':
                object_id = element['objectId']

                # Clear existing text
                requests.append({
                    'deleteText': {
                        'objectId': object_id,
                        'textRange': {
                            'type': 'ALL'
                        }
                    }
                })

                # Insert new title text
                requests.append({
                    'insertText': {
                        'objectId': object_id,
                        'insertionIndex': 0,
                        'text': title
                    }
                })
                break

    return requests
                
def copy_geo_slide(slides_service, presentation_id, slide_index_to_copy, slide_index_to_paste):
    presentation = slides_service.presentations().get(presentationId=presentation_id).execute()
    slides = presentation['slides']
    
    slide_to_copy_id = slides[slide_index_to_copy]['objectId']
    insert_before_object_id = slides[slide_index_to_paste]['objectId']

    # Create a new ID for the duplicated slide
    duplicated_slide_id = f"duplicated_slide_{slide_index_to_copy}_{slide_index_to_paste}"

    requests = [
        {
            "duplicateObject": {
                "objectId": slide_to_copy_id,
                "objectIds": {
                    slide_to_copy_id: duplicated_slide_id
                }
            }
        },
        {
            "updateSlidesPosition": {
                "slideObjectIds": [duplicated_slide_id],
                "insertionIndex": slide_index_to_paste
            }
        }
    ]

    slides_service.presentations().batchUpdate(
        presentationId=presentation_id,
        body={"requests": requests}
    ).execute()

def copy_and_update_geo_slide(slides_service, presentation_id, slide_index_to_copy, slide_index_to_paste, title, data):
    update_requests = []
    if slide_index_to_copy!=slide_index_to_paste:
        copy_geo_slide(slides_service, presentation_id, slide_index_to_copy, slide_index_to_paste)
        
    presentation = slides_service.presentations().get(presentationId=presentation_id).execute()
    slides = presentation['slides']

    slide = slides[slide_index_to_paste]
    for element in slide.get('pageElements', []):
        alt_text = element.get('description', '')
        if 'shape' in element and alt_text == 'geo_title':
            update_requests.extend(update_geo_title(slides_service, presentation_id, slide_index_to_paste, title))
        elif 'table' in element and alt_text == 'geo_table':
            update_requests.extend(update_table_with_dynamic_rows(slides_service, presentation_id, slide_index_to_paste, data))

    return update_requests

def update_forecast_for_geo():
    update_requests = []
    slide_indexes_added=[]
    slide_indexes_to_delete=[]
    idx=0
    for key, value in audience_forecast.items():
        print(f"Updating {key} for {value}")
        title = geo_name_mapping[key]
        data=value["data"]
        location_data = []
        for location in data.keys():
            reach = str(data[location]["user"]).split("\n")[0]
            impr = str(data[location]["impr"]).split("\n")[0]
            location_data.append([location, reach, impr])
        
        # Process each slide separately to avoid API errors
        slide_requests = copy_and_update_geo_slide(slides_service, SOURCE_FILE_ID, GEO_SLIDE_INDEX, GEO_SLIDE_INDEX+idx, title, location_data)
        
        if slide_requests:
            try:
                response = slides_service.presentations().batchUpdate(
                    presentationId=SOURCE_FILE_ID, 
                    body={'requests': slide_requests}
                ).execute()
                print(f"Successfully updated slide {idx}")
            except Exception as e:
                print(f"Error updating slide {idx}: {e}")
                # Try a simpler approach - just update the title
                try:
                    title_requests = update_geo_title(slides_service, SOURCE_FILE_ID, GEO_SLIDE_INDEX+idx, title)
                    if title_requests:
                        response = slides_service.presentations().batchUpdate(
                            presentationId=SOURCE_FILE_ID, 
                            body={'requests': title_requests}
                        ).execute()
                        print(f"Successfully updated title for slide {idx}")
                except Exception as e2:
                    print(f"Error updating title for slide {idx}: {e2}")
        
        idx+=1

update_forecast_for_geo()

