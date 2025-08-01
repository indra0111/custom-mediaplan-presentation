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
                
def copy_geo_slide(slides_service, presentation_id, slide_index_to_copy):
    presentation = slides_service.presentations().get(presentationId=presentation_id).execute()
    slides = presentation['slides']
    
    slide_to_copy_id = slides[slide_index_to_copy]['objectId']
    duplicate_request = {
        "duplicateObject": {
            "objectId": slide_to_copy_id
        }
    }
    
    # Execute the copy
    copy_response = slides_service.presentations().batchUpdate(
        presentationId=presentation_id,
        body={"requests": [duplicate_request]}
    ).execute()
    new_slide_id = copy_response['replies'][0]['duplicateObject']['objectId']
    return new_slide_id

def copy_and_update_geo_slide(slides_service, presentation_id, slide_index_to_copy, slide_index_to_paste, title, data):
    update_requests = []
    slide_added=0
    if slide_index_to_copy!=slide_index_to_paste:
        copy_geo_slide(slides_service, presentation_id, slide_index_to_copy)
        slide_added+=1
        
    presentation = slides_service.presentations().get(presentationId=presentation_id).execute()
    slides = presentation['slides']

    slide = slides[slide_index_to_copy+slide_added]
    for element in slide.get('pageElements', []):
        alt_text = element.get('description', '')
        if 'shape' in element and alt_text == 'geo_title':
            update_requests.extend(update_geo_title(slides_service, presentation_id, slide_index_to_copy+slide_added, title))
        elif 'table' in element and alt_text == 'geo_table':
            update_requests.extend(update_table_with_dynamic_rows(slides_service, presentation_id, slide_index_to_copy+slide_added, data))

    slides_service.presentations().batchUpdate(
        presentationId=presentation_id,
        body={"requests": update_requests}
    ).execute()
    
    return slide_added

def update_forecast_for_geo(slides_service, source_file_id, geo_slide_index, audience_forecast):
    slide_added=0
    idx=0
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
    for key, value in audience_forecast.items():
        title = geo_name_mapping[key]
        location_data = []
        for location in value.keys():
            reach = str(value[location]["user"])
            impr = str(value[location]["impr"])
            location_data.append([location, reach, impr])
        slide_added_in_this_iteration = copy_and_update_geo_slide(slides_service, source_file_id, geo_slide_index, geo_slide_index+idx, title, location_data)
        slide_added+=slide_added_in_this_iteration
        idx+=1
    return slide_added