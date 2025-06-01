import requests
from requests.auth import HTTPBasicAuth
from requests import Session
from zeep import Client, Settings
from zeep.transports import Transport
from zeep.wsse.username import UsernameToken
import mysql.connector
from mysql.connector import errorcode
from datetime import datetime
import os
import urllib.request
import urllib.error
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Define the base URL for the sandbox environment
base_url = "https://ws.sandbox.training.gov.au/Deewr.Tga.Webservices/"
wsdl_url = f"{base_url}TrainingComponentServiceV12.svc?wsdl"
xml_base_url = "https://training.gov.au/TrainingComponentFiles/"

# Define the login details
username = "WebService.Read"
password = "Asdf098"

# Create a session with basic authentication
session = Session()
session.auth = HTTPBasicAuth(username, password)
transport = Transport(session=session)

# Create a SOAP client with WSSE authentication
settings = Settings(strict=False, xml_huge_tree=True)
client = Client(wsdl=wsdl_url, transport=transport, wsse=UsernameToken(username, password), settings=settings)

def remote_file_exists(url):
    """Check if a remote file exists"""
    try:
        response = urllib.request.urlopen(urllib.request.Request(url, method='HEAD'))
        return response.status == 200
    except (urllib.error.HTTPError, urllib.error.URLError):
        return False

def get_xml_file_info(code, debug=False):
    """
    Get XML file information for a given training package code
    Returns tuple: (xml_filename, relative_path, assessment_requirements_file)
    """
    if debug:
        print(f"Getting XML for {code}")
    
    try:
        # Create request objects similar to PHP version
        payload = {
            "Code": code,
            "InformationRequest": {
                "ShowReleases": True,
                "ShowUnitGrid": True,
                "ShowFiles": True
            },
            "IncludeLegacyData": False
        }
        
        # Get details for the training component
        response = client.service.GetDetails(request=payload)
        
        if not hasattr(response, 'Releases') or not response.Releases:
            if debug:
                print(f"No releases found for {code}")
            return None
            
        # Find current release
        target = None
        releases = response.Releases.Release
        
        if isinstance(releases, list):
            for release in releases:
                if hasattr(release, 'Currency') and release.Currency == 'Current':
                    target = release
                    break
        else:
            # Only one release
            target = releases
            
        if not target:
            if debug:
                print(f"No current release found for {code}")
            return None
            
        if debug:
            print(f"Found target release for {code}")
            
        # Find the shortest XML file (ignoring header and credit files)
        target_file = ""
        assessment_requirements_file = ""
        
        if hasattr(target, 'Files') and hasattr(target.Files, 'ReleaseFile'):
            release_files = target.Files.ReleaseFile
            if not isinstance(release_files, list):
                release_files = [release_files]
                
            for file_obj in release_files:
                if hasattr(file_obj, 'RelativePath') and '.xml' in file_obj.RelativePath:
                    relative_path = file_obj.RelativePath.replace('\\', '/')
                    
                    # Look for assessment requirements file
                    if 'AssessmentRequirements' in relative_path:
                        assessment_requirements_file = relative_path
                        if debug:
                            print(f"Found assessment requirements file: {assessment_requirements_file}")
                    
                    # Find shortest XML file (main file)
                    if not target_file or len(relative_path) < len(target_file):
                        target_file = relative_path
                        if debug:
                            print(f"New target file: {target_file}")
        
        if target_file and '.xml' in target_file:
            return (os.path.basename(target_file), target_file, assessment_requirements_file)
        else:
            if debug:
                print(f"No XML file found for {code}")
            return None
            
    except Exception as e:
        print(f"Error getting XML info for {code}: {e}")
        return None

def download_file(url, local_path, debug=False):
    """Download a file from URL to local path"""
    try:
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(local_path), exist_ok=True)
        
        if debug:
            print(f"Downloading {url} to {local_path}")
        
        # Download the file
        urllib.request.urlretrieve(url, local_path)
        return True
    except Exception as e:
        print(f"Error downloading {url}: {e}")
        return False

def download_xml_files(tp_code, debug=False):
    """
    Download XML files for a training package
    Returns the main XML filename if successful, None otherwise
    """
    xml_info = get_xml_file_info(tp_code, debug)
    
    if not xml_info:
        if debug:
            print(f"Could not get XML info for {tp_code}")
        return None
        
    xml_filename, relative_path, assessment_file = xml_info
    
    # Create local directory structure
    local_dir = f"xml/{tp_code}"
    os.makedirs(local_dir, exist_ok=True)
    
    # Download main XML file
    xml_url = xml_base_url + relative_path
    local_xml_path = os.path.join(local_dir, xml_filename)
    
    if remote_file_exists(xml_url):
        if download_file(xml_url, local_xml_path, debug):
            print(f"Downloaded main XML file for {tp_code}: {xml_filename}")
            
            # Download assessment requirements file if it exists
            if assessment_file:
                assessment_url = xml_base_url + assessment_file
                assessment_filename = os.path.basename(assessment_file)
                local_assessment_path = os.path.join(local_dir, assessment_filename)
                
                if remote_file_exists(assessment_url):
                    if download_file(assessment_url, local_assessment_path, debug):
                        print(f"Downloaded assessment file for {tp_code}: {assessment_filename}")
                    else:
                        print(f"Failed to download assessment file for {tp_code}: {assessment_filename}")
            
            return xml_filename
        else:
            print(f"Failed to download main XML file for {tp_code}")
            return None
    else:
        print(f"XML file does not exist at {xml_url}")
        return None

def get_current_training_packages():
    """
    Retrieve a list of all current training packages using the TrainingComponentService.
    This function sends a request to the TrainingComponentService to search for all current
    training packages and returns the results.
    Returns:
    list: A list of current training packages.
    """
    payload = {
        "Filter": "",
        "IncludeDeleted": False,
        "IncludeSuperseded": False,
        "SearchCode": False,
        "SearchIndustrySector": False,
        "SearchOccupation": False,
        "SearchTitle": True,
        "TrainingComponentTypes": {
            "IncludeTrainingPackage": True,
            "IncludeQualification": False,
            "IncludeSkillSet": False,
            "IncludeUnit": False,
            "IncludeAccreditedCourse": False,
            "IncludeAccreditedCourseModule": False,
            "IncludeUnitContextualisation": False
        }
    }
    try:
        response = client.service.Search(request=payload)
        return response
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

def upsert_training_packages_to_db(training_packages_response, debug=False):
    """
    Upsert training packages to the lol_tps table in the learnonline database.
    If the ReleaseDate is later in the retrieved xml than the data in the table,
    set the processed flag to 'N' and download fresh XML files.
    """
    # Extract the actual training packages from the response
    if not training_packages_response or not hasattr(training_packages_response, 'Results'):
        print("No training packages found in response")
        return
    
    training_packages = training_packages_response.Results.TrainingComponentSummary
    
    try:
        # Load database configuration from environment variables
        cnx = mysql.connector.connect(
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD'),
            host=os.getenv('DB_HOST', '127.0.0.1'),
            database=os.getenv('DB_NAME'),
            port=int(os.getenv('DB_PORT', '3306'))
        )
        cursor = cnx.cursor()

        for package in training_packages:
            # Access attributes using dot notation for Zeep objects
            tpCode = package.Code
            tpTitle = package.Title
            
            # Extract the datetime from the UpdatedDate structure
            # Use hasattr to check if attributes exist
            if hasattr(package, 'UpdatedDate') and package.UpdatedDate:
                if hasattr(package.UpdatedDate, 'DateTime'):
                    ReleaseDate = package.UpdatedDate.DateTime
                else:
                    ReleaseDate = package.UpdatedDate
            elif hasattr(package, 'CreatedDate') and package.CreatedDate:
                if hasattr(package.CreatedDate, 'DateTime'):
                    ReleaseDate = package.CreatedDate.DateTime
                else:
                    ReleaseDate = package.CreatedDate
            else:
                print(f"Warning: No date found for package {tpCode}")
                continue

            # Check if record exists and handle accordingly
            query = ("SELECT tpID, ReleaseDate, processed, xmlFile FROM lol_tps WHERE tpCode = %s")
            cursor.execute(query, (tpCode,))
            result = cursor.fetchone()

            should_download_xml = False
            xmlfile = None

            if result:
                existing_tpID = result[0]
                existing_release_date = result[1]
                existing_processed = result[2]
                existing_xmlfile = result[3]
                
                # Convert existing_release_date to datetime if it's a string
                if isinstance(existing_release_date, str):
                    try:
                        # Try to parse the string as a datetime
                        existing_release_date = datetime.fromisoformat(existing_release_date.replace('Z', '+00:00'))
                    except ValueError:
                        try:
                            # Try alternative parsing formats
                            existing_release_date = datetime.strptime(existing_release_date, '%Y-%m-%d %H:%M:%S')
                        except ValueError:
                            print(f"Warning: Could not parse existing date {existing_release_date} for {tpCode}")
                            existing_release_date = datetime.min  # Set to very old date to force update
                
                # Compare dates - if new date is later, mark as unprocessed and download XML
                # Make sure ReleaseDate is timezone-naive for comparison if needed
                release_date_for_comparison = ReleaseDate
                if hasattr(ReleaseDate, 'replace') and ReleaseDate.tzinfo is not None:
                    release_date_for_comparison = ReleaseDate.replace(tzinfo=None)
                
                if hasattr(existing_release_date, 'tzinfo') and existing_release_date.tzinfo is not None:
                    existing_release_date = existing_release_date.replace(tzinfo=None)
                
                if release_date_for_comparison > existing_release_date:
                    processed = 'N'
                    should_download_xml = True
                    print(f"Fresher copy found for {tpCode} - will download XML")
                else:
                    processed = existing_processed
                    xmlfile = existing_xmlfile  # Keep existing xmlfile
                
                # Download XML if needed
                if should_download_xml:
                    downloaded_xmlfile = download_xml_files(tpCode, debug)
                    if downloaded_xmlfile:
                        xmlfile = downloaded_xmlfile
                    else:
                        xmlfile = f"{tpCode}.xml"  # Fallback
                
                # Update existing record
                update_query = (
                    "UPDATE lol_tps SET tpTitle = %s, ReleaseDate = %s, xmlFile = %s, processed = %s "
                    "WHERE tpID = %s"
                )
                cursor.execute(update_query, (tpTitle, ReleaseDate, xmlfile, processed, existing_tpID))
                
                if should_download_xml:
                    print(f"Updated with fresh XML: {tpCode} - {tpTitle}")
                else:
                    print(f"Updated: {tpCode} - {tpTitle}")
            else:
                # New training package - download XML
                processed = 'N'
                should_download_xml = True
                print(f"New training package found: {tpCode} - will download XML")
                
                downloaded_xmlfile = download_xml_files(tpCode, debug)
                if downloaded_xmlfile:
                    xmlfile = downloaded_xmlfile
                else:
                    xmlfile = f"{tpCode}.xml"  # Fallback
                
                # Insert new record
                insert_query = (
                    "INSERT INTO lol_tps (tpCode, tpTitle, ReleaseDate, xmlFile, processed) "
                    "VALUES (%s, %s, %s, %s, %s)"
                )
                cursor.execute(insert_query, (tpCode, tpTitle, ReleaseDate, xmlfile, processed))
                print(f"Inserted new: {tpCode} - {tpTitle}")

        cnx.commit()
        cursor.close()
        cnx.close()
        print(f"Successfully processed {len(training_packages)} training packages")
        
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Something is wrong with your user name or password")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("Database does not exist")
        else:
            print(err)
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        # Add debugging information
        print(f"Type of training_packages_response: {type(training_packages_response)}")
        if hasattr(training_packages_response, 'Results'):
            print(f"Type of Results: {type(training_packages_response.Results)}")
            if hasattr(training_packages_response.Results, 'TrainingComponentSummary'):
                print(f"Type of TrainingComponentSummary: {type(training_packages_response.Results.TrainingComponentSummary)}")
                if training_packages_response.Results.TrainingComponentSummary:
                    first_package = training_packages_response.Results.TrainingComponentSummary[0]
                    print(f"Type of first package: {type(first_package)}")
                    print(f"Available attributes: {dir(first_package)}")
    finally:
        if 'cnx' in locals() and cnx.is_connected():
            cnx.close()

if __name__ == "__main__":
    # Set debug to True for verbose output
    debug_mode = False
    
    print("Starting training package update process with XML download...")
    training_packages = get_current_training_packages()
    if training_packages:
        upsert_training_packages_to_db(training_packages, debug=debug_mode)
    else:
        print("Failed to retrieve training packages")
    print("Process completed.")