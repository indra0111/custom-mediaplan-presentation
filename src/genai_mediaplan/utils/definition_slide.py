def get_forecast_number_in_format(audience_forecast):
    updated_audience_forecast={}
    preset_title_map={
        "TIL_All_Cluster_RNF": "All Cluster",
        "TIL_All_Languages_RNF": "All Languages",
        "TIL_TOI_Only_RNF": "TOI Only",
        "TIL_ET_And_TOI_RNF": "ET+TOI",
        "TIL_ET_Only_RNF": "ET Only",
        "TIL_NBT_Only_RNF": "NBT Only",
        "TIL_MT_Only_RNF": "MT Only",
        "TIL_VK_Only_RNF": "VK Only",
        "TIL_IAG_Only_RNF": "IAG Only",
        "TIL_EIS_Only_RNF": "EIS Only",
        "TIL_Tamil_Only_RNF": "Tamil Only",
        "TIL_Telugu_Only_RNF": "Telugu Only",
        "TIL_Malayalam_Only_RNF": "Malayalam Only",
    }
    for preset_name, preset_data in audience_forecast.items():
        updated_audience_forecast[preset_name]={}
        updated_audience_forecast[preset_name]["title"]=preset_title_map.get(preset_name, " ")
        updated_audience_forecast[preset_name]["data"]=preset_data
    
    return updated_audience_forecast
        
def get_alt_description_mappings(audience_forecast, definition):
    idx=1
    alt_data={}
    coverage_map={
        "TIL_All_Cluster_RNF": "COMPREHENSIVE NETWORK COVERAGE",
        "TIL_All_Languages_RNF": "MULTILINGUAL REACH",
        "TIL_TOI_Only_RNF": "PREMIUM ENGLISH",
        "TIL_ET_And_TOI_RNF": "PREMIUM COMBO",
        "TIL_ET_Only_RNF": "PREMIUM BUSINESS & INVESTMENT",
        "TIL_NBT_Only_RNF": "HINDI MARKET",
        "TIL_MT_Only_RNF": "MARATHI MARKET",
        "TIL_VK_Only_RNF": "KANNADA MARKET",
        "TIL_IAG_Only_RNF": "IAG MARKET",
        "TIL_EIS_Only_RNF": "EISAMAY MARKET",
        "TIL_Tamil_Only_RNF": "TAMIL MARKET",
        "TIL_Telugu_Only_RNF": "TELUGU MARKET",
        "TIL_Malayalam_Only_RNF": "MALAYALAM MARKET",
    }
    for key, value in audience_forecast.items():
        title = value["title"]
        data=value["data"]
        reach = f"{data['Overall']['user']}\nUser Reach"
        impr = f"{data['Overall']['impr']}\nTargetable Impressions"
        alt_data[f"preset_title_{idx}"] = title
        alt_data[f"user_{idx}"] = reach
        alt_data[f"impr_{idx}"] = impr
        alt_data[f"coverage_{idx}"] = coverage_map[key]
        idx+=1
    alt_data["cohort_definition"]=definition
    return alt_data

def update_preset_data(slides_service, presentation_id, slide_index, data):
    requests = []
    presentation = slides_service.presentations().get(presentationId=presentation_id).execute()
    slide = presentation['slides'][slide_index]
    for element in slide.get('pageElements', []):
        if 'shape' in element:
            alt_text = element.get('description', '')
            if alt_text in data:
                object_id = element['objectId']
                shape = element['shape']
                text_elements = shape.get('text', {}).get('textElements', [])
                
                if not text_elements:
                    continue
                
                # Extract original styles line by line
                lines = []
                current_line = ""
                current_style = None
                index = 0

                for elem in text_elements:
                    if 'textRun' in elem:
                        content = elem['textRun'].get('content', '')
                        style = elem['textRun'].get('style', {})
                        for char in content:
                            if char == '\n':
                                lines.append((current_line, current_style))
                                current_line = ""
                            else:
                                if current_line == "":
                                    current_style = style
                                current_line += char
                    elif 'paragraphMarker' in elem:
                        if current_line:
                            lines.append((current_line, current_style))
                            current_line = ""

                if current_line:
                    lines.append((current_line, current_style))

                # Delete existing text
                requests.append({
                    "deleteText": {
                        "objectId": object_id,
                        "textRange": {"type": "ALL"}
                    }
                })

                # Insert new text
                new_text = str(data[alt_text])  # should include `\n` if multi-line
                requests.append({
                    "insertText": {
                        "objectId": object_id,
                        "insertionIndex": 0,
                        "text": new_text
                    }
                })

                # Reapply text styles per line
                char_index = 0
                new_lines = new_text.split('\n')

                for i, line_text in enumerate(new_lines):
                    if i < len(lines):
                        _, line_style = lines[i]
                        if line_style and len(line_text) > 0:
                            requests.append({
                                "updateTextStyle": {
                                    "objectId": object_id,
                                    "style": line_style,
                                    "textRange": {
                                        "type": "FIXED_RANGE",
                                        "startIndex": char_index,
                                        "endIndex": char_index + len(line_text)+1
                                    },
                                    "fields": ",".join(line_style.keys())
                                }
                            })
                    char_index += len(line_text) + 1  # account for `\n`

                # Reapply paragraph style (alignment)
                for elem in text_elements:
                    if 'paragraphMarker' in elem and 'style' in elem['paragraphMarker']:
                        para_style = elem['paragraphMarker']['style']
                        requests.append({
                            "updateParagraphStyle": {
                                "objectId": object_id,
                                "style": para_style,
                                "textRange": {"type": "ALL"},
                                "fields": ",".join(para_style.keys())
                            }
                        })
                        break  # Only need first one

    return requests

def delete_slides(slides_service, presentation_id, slide_indexes_to_delete):
    requests = []
    presentation = slides_service.presentations().get(presentationId=presentation_id).execute()
    for slide_index in slide_indexes_to_delete:
        requests.append({
            "deleteObject": {
                "objectId": presentation['slides'][slide_index]['objectId']
            }
        })
    return requests

def update_definition_reach(slides_service, source_file_id, definition_slide_index, audience_forecast, definition):
    audience_forecast = get_forecast_number_in_format(audience_forecast)
    total_count = len(audience_forecast.keys())
    slides_to_delete = []
    for i in range(6):
        if i!=total_count-1:
            slides_to_delete.append(definition_slide_index+i)
    slide_index_to_update = definition_slide_index+total_count-1
    alt_data = get_alt_description_mappings(audience_forecast, definition)
    update_requests = update_preset_data(slides_service, source_file_id, slide_index_to_update, alt_data)
    delete_requests = delete_slides(slides_service, source_file_id, slides_to_delete)
    return update_requests, delete_requests

