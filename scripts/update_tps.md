# Training Package Update Script Documentation

## Overview

The `update_tps.py` script is designed to synchronize Australian training package metadata from the government's training.gov.au web service into a local MySQL database, and download associated XML files containing detailed training component information.

## Background Context

### What are Training Packages?
Training packages are standardized frameworks used in Australia's vocational education system. Each package contains:
- **Qualifications** (e.g., Certificate III in Carpentry)
- **Units of Competency** (individual skills/knowledge components)
- **Skill Sets** (grouped units for specific job roles)
- **Assessment Requirements** (how competency is measured)

Examples of training package codes:
- `CPC08` - Construction, Plumbing and Services
- `SIT60` - Tourism, Travel and Hospitality
- `ICT30` - Information and Communications Technology

### About training.gov.au
Training.gov.au is the Australian government's official repository for vocational education training information. It provides:
- A **SOAP web service** for programmatic access to training data
- **XML files** containing detailed training component specifications
- Regular updates as training standards evolve

The TGA web-services documents available from 
https://data.gov.au/data/dataset/training-gov-au-web-service-access-to-sandbox-environment outline the logical data model, data definitions, and web services specifications for the National Register component of training.gov.au (TGA). The National Register serves as a central repository for authoritative information on Registered Training Organisations (RTOs), Nationally Recognised Training (NRT) products, and the approved scope of each RTO to deliver and/or assess these products.

## Setup and Installation

### Prerequisites
- Python 3.6+
- MySQL 5.7+ or MariaDB equivalent
- Network access to training.gov.au

### Python Dependencies
Install the required packages:
```bash
pip install requests zeep mysql-connector-python python-dotenv
```

### Database Configuration

#### Step 1: Create Environment File
1. Copy the `.env.example` file to `.env`:
   ```bash
   cp .env.example .env
   ```

2. Edit the `.env` file with your actual database credentials:
   ```env
   # Database Configuration
   DB_USER=your_database_username
   DB_PASSWORD=your_database_password
   DB_HOST=127.0.0.1
   DB_NAME=your_database_name
   DB_PORT=3306
   ```

#### Step 2: Database Schema
Ensure your database has the `lol_tps` table:
```sql
CREATE TABLE `lol_tps` (
  `tpID` int(11) NOT NULL AUTO_INCREMENT,
  `tpCode` varchar(15) NOT NULL,
  `tpTitle` varchar(500) NOT NULL,
  `xmlFile` varchar(100) NOT NULL,
  `ReleaseDate` varchar(50) NOT NULL,
  `processed` char(1) NOT NULL DEFAULT 'N',
  PRIMARY KEY (`tpID`),
  UNIQUE KEY `tpCode` (`tpCode`)
);
```

#### Important Security Notes
- **Never commit your `.env` file** to version control
- The `.env` file contains sensitive database credentials
- Always use the `.env.example` template for sharing configuration structure
- Add `.env` to your `.gitignore` file:
  ```gitignore
  .env
  .env.local
  .env.*.local
  ```

## Technical Architecture

### SOAP Web Service Integration
The script uses **SOAP (Simple Object Access Protocol)** - an older but still widely used web service protocol that:
- Uses XML for message formatting
- Requires a **WSDL (Web Service Description Language)** file that describes available operations
- Uses structured request/response objects rather than simple REST endpoints

**Key SOAP concepts used:**
- **Client**: The `zeep` library creates a SOAP client from the WSDL
- **Authentication**: Uses both HTTP Basic Auth and WS-Security (WSSE) tokens
- **Operations**: Like `Search()` and `GetDetails()` - similar to REST endpoints but structured differently

### Environment Variables
The script uses environment variables for configuration:
- `DB_USER` - Database username
- `DB_PASSWORD` - Database password
- `DB_HOST` - Database host (defaults to 127.0.0.1)
- `DB_NAME` - Database name
- `DB_PORT` - Database port (defaults to 3306)

## Code Structure

### Dependencies
```python
import requests          # HTTP client library
from zeep import Client  # SOAP client library
import mysql.connector   # MySQL database connector
import urllib.request    # For file downloads
import os               # File system operations
from dotenv import load_dotenv  # Environment variable loading
```

### Configuration
```python
# Load environment variables from .env file
load_dotenv()

# Web service endpoints
base_url = "https://ws.sandbox.training.gov.au/Deewr.Tga.Webservices/"
wsdl_url = f"{base_url}TrainingComponentServiceV12.svc?wsdl"
xml_base_url = "https://training.gov.au/TrainingComponentFiles/"

# Authentication credentials
username = "WebService.Read"
password = "Asdf098"
```

**Note**: The training.gov.au credentials are public sandbox credentials provided for testing/development.

### Main Functions

#### `get_current_training_packages()`
**Purpose**: Retrieves a list of all current training packages from the web service.

**SOAP Operation**: Calls the `Search` method with filters to get only training packages (not individual units or qualifications).

**Returns**: A SOAP response object containing training package summaries with basic metadata.

#### `get_xml_file_info(code, debug=False)`
**Purpose**: For a specific training package code, gets detailed information about available XML files.

**Process**:
1. Calls the `GetDetails` SOAP method for the training package
2. Searches through the response for the "Current" release
3. Examines all files associated with that release
4. Identifies the main XML file (shortest filename - excludes header/credit files)
5. Looks for assessment requirements files (separate XML with assessment criteria)

**Returns**: Tuple of `(xml_filename, relative_path, assessment_requirements_file)`

**Why the complexity?**: Training packages can have multiple XML files and releases. The script needs to find the current, canonical version.

#### `download_xml_files(tp_code, debug=False)`
**Purpose**: Downloads XML files for a training package to local storage.

**Process**:
1. Gets XML file information using `get_xml_file_info()`
2. Creates local directory structure: `xml/{tp_code}/`
3. Downloads main XML file from training.gov.au
4. Downloads assessment requirements file if it exists
5. Handles download errors gracefully

**File Organization**:
```
xml/
├── CPC08/
│   ├── CPC08_R1.xml              # Main training package XML
│   └── CPC08_AssessmentReq.xml   # Assessment requirements (if exists)
├── SIT60/
│   └── SIT60_R2.xml
└── ICT30/
    └── ICT30_R1.xml
```

#### `upsert_training_packages_to_db(training_packages_response, debug=False)`
**Purpose**: Main processing function that updates the database and downloads XML files when needed.

**Database Connection**: Now uses environment variables for secure credential management:
```python
cnx = mysql.connector.connect(
    user=os.getenv('DB_USER'),
    password=os.getenv('DB_PASSWORD'),
    host=os.getenv('DB_HOST', '127.0.0.1'),
    database=os.getenv('DB_NAME'),
    port=int(os.getenv('DB_PORT', '3306'))
)
```

**Process for each training package**:
1. **Extract data** from SOAP response (code, title, release date)
2. **Check if exists** in database using training package code
3. **Compare dates** - if web service has newer date than database:
   - Download fresh XML files
   - Set `processed = 'N'` (marks for reprocessing by other systems)
   - Update database record
4. **If new training package**:
   - Download XML files
   - Insert new database record
   - Set `processed = 'N'`
5. **If no changes**: Update title but keep existing XML file reference

## Key Design Decisions

### Secure Configuration Management
The script now uses environment variables to separate configuration from code:
- **Security**: Database credentials are not hardcoded in the source
- **Flexibility**: Easy to deploy in different environments
- **Best Practice**: Follows 12-factor app principles for configuration

### Date Comparison Logic
The script compares `ReleaseDate` values to determine if XML files need refreshing:
```python
if release_date_for_comparison > existing_release_date:
    processed = 'N'
    should_download_xml = True
```

**Why this matters**: Training standards evolve over time. When the government updates a training package, the XML files contain the new requirements. The script ensures local copies stay synchronized.

### Error Handling Approach
The script uses defensive programming:
- **Network errors**: Checks if remote files exist before downloading
- **SOAP errors**: Catches and logs web service failures
- **Database errors**: Uses proper connection management and transactions
- **File system errors**: Creates directories as needed, handles permission issues

### XML File Selection Logic
Training packages often have multiple XML files. The script uses the "shortest filename" heuristic because:
- Main training package files have simple names like `CPC08_R1.xml`
- Header/credit/supplementary files have longer, descriptive names
- This matches the logic from the original PHP implementation

## Usage Examples

### Basic Usage
```bash
python update_tps.py
```

### Debug Mode
Enable verbose logging by setting `debug_mode = True` in the script:
```python
debug_mode = True  # Shows detailed SOAP requests and file operations
```

### First-Time Setup
1. Clone/download the script files
2. Install dependencies: `pip install requests zeep mysql-connector-python python-dotenv`
3. Copy `.env.example` to `.env`
4. Edit `.env` with your database credentials
5. Ensure your database has the required `lol_tps` table
6. Run the script: `python update_tps.py`

## Integration Points

### With Other Systems
The `processed` field serves as a flag for downstream systems:
- `processed = 'N'`: Training package has been updated, needs reprocessing
- `processed = 'Y'`: Training package is up to date

### File System Integration
Downloaded XML files are stored in a predictable structure that other applications can reference using the `xmlFile` field from the database.

## Troubleshooting

### Common Issues

**Environment Configuration Errors**:
- Ensure `.env` file exists and is in the same directory as the script
- Check that all required environment variables are set
- Verify database credentials are correct

**SOAP Authentication Failures**:
- Verify credentials are correct
- Check if sandbox vs production endpoint is intended
- Network firewall may block SOAP requests

**XML Download Failures**:
- training.gov.au servers may be temporarily unavailable
- Some training packages may not have XML files available
- File permissions in local `xml/` directory

**Database Connection Issues**:
- Verify MySQL credentials and host connectivity in `.env` file
- Check if database schema matches expected structure
- Ensure proper character encoding (UTF-8) for training package titles

### Debug Information
When `debug=True`, the script outputs:
- SOAP request/response details
- File download URLs and paths
- Database query results
- Error stack traces

## Security Best Practices

### Environment File Management
- **Never commit `.env` files** to version control
- Use different `.env` files for different environments (development, staging, production)
- Restrict file permissions on `.env` files: `chmod 600 .env`
- Use strong, unique passwords for database access

### Database Security
- Create a dedicated database user with minimal required permissions
- Use SSL connections for database access in production
- Regularly rotate database passwords
- Monitor database access logs

## Future Enhancements

### Potential Improvements
1. **Incremental updates**: Only check training packages modified since last run
2. **Parallel downloads**: Use threading to download multiple XML files simultaneously
3. **Retry logic**: Implement exponential backoff for failed downloads
4. **External configuration**: Support multiple configuration formats (YAML, JSON)
5. **Logging**: Replace print statements with proper logging framework
6. **Health checks**: Monitor web service availability and database connectivity
7. **Docker support**: Containerize the application for easy deployment

### Scalability Considerations
- Current approach processes all training packages on each run
- For large-scale deployments, consider pagination of SOAP requests
- Database connection pooling for high-frequency updates
- Caching of SOAP client objects to reduce initialization overhead

## Dependencies and Requirements

### Python Packages
```bash
pip install requests zeep mysql-connector-python python-dotenv
```

### System Requirements
- Python 3.6+
- MySQL 5.7+ or MariaDB equivalent
- Network access to training.gov.au
- Local file system write permissions

### External Services
- training.gov.au SOAP web service (requires internet connectivity)
- MySQL/MariaDB database server

This documentation should help future developers understand both the technical implementation and the business context of the training package synchronization system, while maintaining security best practices for credential management.