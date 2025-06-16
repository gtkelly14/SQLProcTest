# SQLProcTest
Simple app for testing SQL Server proc changes

## Overview
This application helps test stored procedures on a Microsoft SQL Server Database. It can execute stored procedures with parameters and compare results against baseline data.

## Features
- Execute SQL Server stored procedures with parameters
- Two modes of operation:
  - Baseline mode: Execute proc and store results locally
  - Test mode: Execute proc, compare with baseline, show differences
- Stores baseline results in CSV format
- Compares results and shows differences when found
- Configuration-based setup with YAML
- Detailed logging
- Support for documenting stored procedures and their parameters

## Requirements
- Python 3.8 or higher
- SQL Server ODBC Driver
- Required Python packages (see requirements.txt)

## Setup
1. Clone this repository
2. Install required packages:
   ```
   pip install -r requirements.txt
   ```
3. Copy `config.yaml.example` to `config.yaml` and update with your settings:
   ```yaml
   database:
     server: your_server_name
     name: your_database_name
     username: your_username
     password: your_password
     driver: SQL Server

   application:
     baseline_dir: baselines
     log_level: INFO
     timeout: 30

   # Optional: Define your stored procedures
   stored_procedures:
     YourProcName:
       description: "Description of your procedure"
       parameters:
         - name: param1
           type: int
   ```

## Usage
The application can be run in two modes:

### Baseline Mode
To create a baseline:
```
python sql_proc_test.py baseline YourProcName [param1,param2,...]
```

### Test Mode
To test against baseline:
```
python sql_proc_test.py test YourProcName [param1,param2,...]
```

### Examples
1. Create baseline for a procedure without parameters:
   ```
   python sql_proc_test.py baseline GetCustomers
   ```

2. Create baseline for a procedure with parameters:
   ```
   python sql_proc_test.py baseline GetCustomerOrders "123,2024-01-01"
   ```

3. Test against baseline:
   ```
   python sql_proc_test.py test GetCustomerOrders "123,2024-01-01"
   ```

## Configuration
The `config.yaml` file supports the following sections:

### Database Configuration
- `server`: SQL Server instance name
- `name`: Database name
- `username`: Database username
- `password`: Database password
- `driver`: ODBC driver name

### Application Configuration
- `baseline_dir`: Directory to store baseline results
- `log_level`: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- `timeout`: Database connection timeout in seconds

### Stored Procedures (Optional)
Document your stored procedures with their parameters:
```yaml
stored_procedures:
  ProcName:
    description: "Procedure description"
    parameters:
      - name: param_name
        type: param_type
```

## Notes
- Baseline results are stored in the configured baseline directory
- Each baseline is saved with a timestamp
- When testing, the most recent baseline for the procedure is used for comparison
- Detailed logs are available for troubleshooting