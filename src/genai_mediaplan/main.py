#!/usr/bin/env python
import sys
import warnings
import os
from datetime import datetime

from genai_mediaplan.crew import GenaiMediaplan
from genai_mediaplan.utils.forecast_data import export_table_as_json
from genai_mediaplan.utils.helper import extract_json_from_markdown_or_json
from genai_mediaplan.utils.update_google_slides_content import get_copy_of_presentation
from dotenv import load_dotenv

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

# This main file is intended to be a way for you to run your
# crew locally, so refrain from adding unnecessary logic into this file.
# Replace with inputs you want to test with, it will automatically
# interpolate any tasks and agents information

def run():
    """
    Run the crew with email content.
    """
    load_dotenv(override=True)
    
    # Example email content - replace with actual email data
    email_subject = "Q4 Marketing Campaign Performance Review"
    email_body = """
    Hi Team,
    
    I wanted to share the Q4 marketing campaign results. We achieved 15% increase in conversion rates 
    and 25% growth in customer acquisition. The digital campaigns performed exceptionally well with 
    $2.5M in revenue generated.
    
    Key highlights:
    - Social media campaigns: 40% engagement rate
    - Email marketing: 22% open rate, 8% click-through rate
    - Paid advertising: 3.2x ROI
    
    Action items for next quarter:
    1. Scale successful campaigns to new markets
    2. Optimize budget allocation based on performance
    3. Implement A/B testing for creative assets
    
    Please review the attached detailed report and let me know your thoughts.
    
    Best regards,
    Marketing Team
    """
    
    email_subject = "Need audience data"
    email_body = "Need data for the below brief.  Job Seeking Professionals, 20-30 years old, Tier 1 and 2 cities, TOI and NBT Standard banners"
    
    # inputs = {
    #     'email_subject': email_subject,
    #     'email_body': email_body,
    #     'email_info': email_info,
    #     'presentation_title': context['presentation_title'],
    #     'audience_data': context['audience_data']
    # }
    
    audience_data = {'2ws': {'name': 'INT_Job', 'description': 'Individuals looking for jobs'}, '6ef': {'name': 'INT_Bank Jobs', 'description': 'Individuals interested in bank jobs such as IBPS,SBI, PO,clerk etc.'}, '6eg': {'name': 'INT_Government Jobs', 'description': 'Individuals interested in government jobs such as SSC,Railways etc.'}, '6yi': {'name': 'DEMO_AnnuaI Income_Above 7 LPA', 'description': 'Individuals with declared annual income of above 7 L'}, '7dn': {'name': 'INT_Job & Career', 'description': 'Individuals who are interested in searching for jobs and career options and info related to it'}, '9r0': {'name': 'DEMO_AnnuaI Income_10 to 20 LPA', 'description': 'Individuals with declared annual income between 10 L to 20L'}, '9r1': {'name': 'DEMO_AnnuaI Income_20 to 30 LPA', 'description': 'Individuals with declared annual income between 20 L to 30L'}, '9r2': {'name': 'DEMO_AnnuaI Income_30 to 50 LPA', 'description': 'Individuals with declared annual income between 30 L to 50L'}, 'buq': {'name': 'Package_High Net Worth Individuals', 'description': 'People with high net worth income of or above Rs. 40 LPA or who transact amounts equal to or larger than INR 1 Lakh'}, 'h62': {'name': 'UAG_Mobile Device - Rs 40001 to 60000', 'description': 'Users with a mobile phone of price Rs 40001 to 60000'}, 'h64': {'name': 'UAG_Mobile Device - Rs 60000+', 'description': 'Users with a mobile phone of price Rs 60000+'}, 'hsz': {'name': 'DEMO_Job Function_Automobile Sector', 'description': 'Individuals working in Automobile Sector'}, 'ht0': {'name': 'DEMO_Job Function_BFSI Sector', 'description': 'Individuals working in BFSI Sector'}, 'ht1': {'name': 'DEMO_Job Function_Education or Teaching Sector', 'description': 'Individuals working in Education/ Teaching Sector'}, 'ht2': {'name': 'DEMO_Job Function_Management Sector', 'description': 'Individuals working in Management Sector'}, 'ht3': {'name': 'DEMO_Job Function_FMCG Sector', 'description': 'Individuals working in FMCG Sector'}, 'ht4': {'name': 'DEMO_Job Function_Manufacturing Sector', 'description': 'Individuals working in Manufacturing Sector'}, 'ht5': {'name': 'DEMO_Job Function_Advertising Sector', 'description': 'Individuals working in Advertising Sector'}, 'ht7': {'name': 'DEMO_Job Function_IT_Tech Sector', 'description': 'Individuals working in IT-Tech Sector'}, 'ht8': {'name': 'DEMO_Job Function_IT_Non_Tech Sector', 'description': 'Individuals working in IT-Non-Tech Sector'}, 'ht9': {'name': 'DEMO_Job Function_IT Sector', 'description': 'Individuals working in IT Sector'}, 'n32': {'name': 'Industry_Automobiles_Four Wheeler_Luxury Cars_Impr', 'description': 'Automobile industry enthusiasts who view content or ads about luxury cars'}, 'nlx': {'name': 'InM_Mtag_Jobs & Careers', 'description': 'People who search for and read articles related to Jobs & Careers and all other related keywords'}, 'nyw': {'name': 'Package_Luxury Products', 'description': 'People who search for or buy high value products and services like booking international travel packages, investing in real estate etc.'}, 'o1t': {'name': 'Package_Travel - International', 'description': 'People interested in gathering international travel related info or have apps in their devices for such cab bookings, hotel or flight booking'}, 'o23': {'name': 'Package_Real Estate - Luxurious Properties', 'description': 'People interested in high-end residential, commercial or agricultural properties and have spending capacity of above 1 crore'}, 'o2c': {'name': 'Package_Top and Mid Management', 'description': 'People who are at a managerial position with a work experience of 8+ years and read management related articles online'}, 'o3b': {'name': 'Package_Young Working Professionals', 'description': 'People who are freshers or young professionals in corporate world with an experience of 0 to 8 years'}, 'out': {'name': 'Industry_CAN_Automobiles_Four Wheeler_Luxury Cars_Impr', 'description': 'Automobile industry enthusiasts who view content or ads about luxury cars on CAN Adserver'}, 'pv1': {'name': 'DEMO_Job Function_Engineers', 'description': 'Individuals working as Engineer'}, 'pv4': {'name': 'DEMO_Job Function_Executives', 'description': 'Individuals working as Executive'}, 'pvn': {'name': 'InM_Mtag_Jobs & Careers_Medical Staff', 'description': 'People who search for and read articles related to Jobs & Careers for Medical Staff like nurses, ward boys and all other related keywords'}}
    
    forecast_data={'TIL_All_Cluster_RNF': {'Tier1 Cities': {'user': 38.31, 'impr': 174.23}, 'Tier2 Cities': {'user': 43.07, 'impr': 167.53}, 'Tier3': {'user': 26.7, 'impr': 105.27}, 'Top 8 Metro Cities': {'user': 38.33, 'impr': 174.16}, 'Top 10 Cities': {'user': 39.99, 'impr': 180.18}, 'Maharashtra': {'user': 14.55, 'impr': 71.83}, 'Telangana': {'user': 6.83, 'impr': 30.61}, 'India': {'user': 9.95, 'impr': 50.45}}, 'TIL_TOI_Only_RNF': {'Tier1 Cities': {'user': 18.46, 'impr': 86.56}, 'Tier2 Cities': {'user': 13.08, 'impr': 49.8}, 'Tier3': {'user': 10.4, 'impr': 41.21}, 'Top 8 Metro Cities': {'user': 18.46, 'impr': 86.56}, 'Top 10 Cities': {'user': 18.77, 'impr': 87.64}, 'Maharashtra': {'user': 7.19, 'impr': 35.3}, 'Telangana': {'user': 2.58, 'impr': 11.77}, 'India': {'user': 5.06, 'impr': 25.71}}, 'TIL_ET_Only_RNF': {'Tier1 Cities': {'user': 9.06, 'impr': 35.14}, 'Tier2 Cities': {'user': 6.46, 'impr': 21.04}, 'Tier3': {'user': 4.92, 'impr': 16.5}, 'Top 8 Metro Cities': {'user': 9.06, 'impr': 35.12}, 'Top 10 Cities': {'user': 9.23, 'impr': 35.56}, 'Maharashtra': {'user': 3.53, 'impr': 14.8}, 'Telangana': {'user': 1.14, 'impr': 4.21}, 'India': {'user': 2.5, 'impr': 10.55}}, 'TIL_ET_And_TOI_RNF': {'Tier1 Cities': {'user': 18.2, 'impr': 86.53}, 'Tier2 Cities': {'user': 12.81, 'impr': 50.03}, 'Tier3': {'user': 10.21, 'impr': 40.99}, 'Top 8 Metro Cities': {'user': 18.21, 'impr': 86.58}, 'Top 10 Cities': {'user': 18.5, 'impr': 87.62}, 'Maharashtra': {'user': 7.08, 'impr': 35.87}, 'Telangana': {'user': 2.38, 'impr': 10.88}, 'India': {'user': 4.86, 'impr': 25.05}}, 'TIL_NBT_Only_RNF': {'Tier1 Cities': {'user': 5.81, 'impr': 25.3}, 'Tier2 Cities': {'user': 14.77, 'impr': 63.99}, 'Tier3': {'user': 6.03, 'impr': 22.92}, 'Top 8 Metro Cities': {'user': 5.81, 'impr': 25.3}, 'Top 10 Cities': {'user': 6.7, 'impr': 28.78}, 'Maharashtra': {'user': 2.74, 'impr': 12.84}, 'Telangana': {'user': 0.17, 'impr': 0.62}, 'India': {'user': 0.31, 'impr': 1.35}}, 'TIL_All_Languages_RNF': {'Tier1 Cities': {'user': 11.35, 'impr': 48.77}, 'Tier2 Cities': {'user': 17.65, 'impr': 74.11}, 'Tier3': {'user': 10.18, 'impr': 40.15}, 'Top 8 Metro Cities': {'user': 11.35, 'impr': 48.77}, 'Top 10 Cities': {'user': 12.25, 'impr': 52.23}, 'Maharashtra': {'user': 4.17, 'impr': 20.65}, 'Telangana': {'user': 2.87, 'impr': 12.26}, 'India': {'user': 2.97, 'impr': 14.86}}}
    
    inputs = {
        'email_subject': email_subject,
        'email_body': email_body,
        'audience_data': audience_data,
    }
    
    try:
        # GenaiMediaplan().crew().kickoff(inputs=inputs)
        model_output_json = extract_json_from_markdown_or_json("final_report.md")
        presentation_title = model_output_json.get("title", "")
        get_copy_of_presentation(presentation_title, model_output_json, forecast_data)
    except Exception as e:
        raise Exception(f"An error occurred while running the crew: {e}")

def run_with_email(email_subject, email_body, audience_data, forecast_data):
    """
    Run the crew with provided email content.
    
    Args:
        email_subject: Subject line of the email
        email_body: Body content of the email
    """
    load_dotenv(override=True)
    
    inputs = {
        'email_subject': email_subject,
        'email_body': email_body,
        'forecast_data': forecast_data,
        'audience_data': audience_data
    }
    
    try:
        GenaiMediaplan().crew().kickoff(inputs=inputs)
        model_output_json = extract_json_from_markdown_or_json("final_report.md")
        title = model_output_json.get("title")
        return get_copy_of_presentation(title, model_output_json, forecast_data)
    except Exception as e:
        raise Exception(f"An error occurred while running the crew: {e}")