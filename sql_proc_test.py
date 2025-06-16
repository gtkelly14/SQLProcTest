import os
import sys
import yaml
import pyodbc
import pandas as pd
import logging
from datetime import datetime
from pathlib import Path

class SQLProcTester:
    def __init__(self, config_path='config.yaml'):
        self.config = self._load_config(config_path)
        self.conn = None
        self.baseline_dir = Path(self.config['application']['baseline_dir'])
        self.baseline_dir.mkdir(exist_ok=True)
        self._setup_logging()
        self._connect_db()

    def _setup_logging(self):
        """Configure logging based on config settings"""
        log_level = getattr(logging, self.config['application']['log_level'])
        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)

    def _load_config(self, config_path):
        """Load configuration from YAML file"""
        try:
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)
            
            # Validate required configuration sections
            required_sections = ['database', 'application']
            for section in required_sections:
                if section not in config:
                    raise ValueError(f"Missing required configuration section: {section}")
            
            return config
        except Exception as e:
            print(f"Error loading configuration: {str(e)}")
            sys.exit(1)

    def _connect_db(self):
        """Establish database connection using configuration"""
        try:
            db_config = self.config['database']
            conn_str = (
                f"DRIVER={{{db_config['driver']}}};"
                f"SERVER={db_config['server']};"
                f"DATABASE={db_config['name']};"
                f"UID={db_config['username']};"
                f"PWD={db_config['password']}"
            )
            self.conn = pyodbc.connect(conn_str, timeout=self.config['application']['timeout'])
            self.logger.info("Successfully connected to database")
        except Exception as e:
            self.logger.error(f"Error connecting to database: {str(e)}")
            sys.exit(1)

    def get_proc_info(self, proc_name):
        """Get stored procedure information from config if available"""
        return self.config.get('stored_procedures', {}).get(proc_name)

    def execute_proc(self, proc_name, params=None):
        """Execute stored procedure and return results as DataFrame"""
        try:
            cursor = self.conn.cursor()
            
            # Build parameter string
            param_str = ""
            if params:
                param_str = ",".join([f"@{i+1}={p}" for i, p in enumerate(params.split(','))])
            
            # Execute stored procedure
            query = f"EXEC {proc_name} {param_str}"
            self.logger.info(f"Executing: {query}")
            cursor.execute(query)
            
            # Convert results to DataFrame
            columns = [column[0] for column in cursor.description]
            data = cursor.fetchall()
            return pd.DataFrame.from_records(data, columns=columns)
            
        except Exception as e:
            self.logger.error(f"Error executing stored procedure: {str(e)}")
            return None

    def save_baseline(self, proc_name, params, results):
        """Save baseline results to file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{proc_name}_{timestamp}.csv"
        filepath = self.baseline_dir / filename
        
        # Save results to CSV
        results.to_csv(filepath, index=False)
        self.logger.info(f"Baseline saved to: {filepath}")

    def compare_results(self, current_results, baseline_file):
        """Compare current results with baseline"""
        try:
            baseline = pd.read_csv(baseline_file)
            
            # Compare DataFrames
            if current_results.equals(baseline):
                self.logger.info("Results match baseline exactly!")
                return True
            
            # Find differences
            differences = pd.concat([current_results, baseline]).drop_duplicates(keep=False)
            self.logger.info("\nDifferences found:")
            print(differences)
            return False
            
        except Exception as e:
            self.logger.error(f"Error comparing results: {str(e)}")
            return False

def main():
    if len(sys.argv) < 3:
        print("Usage: python sql_proc_test.py [baseline|test] proc_name [params]")
        sys.exit(1)

    mode = sys.argv[1].lower()
    proc_name = sys.argv[2]
    params = sys.argv[3] if len(sys.argv) > 3 else None

    tester = SQLProcTester()
    
    # Log procedure information if available
    proc_info = tester.get_proc_info(proc_name)
    if proc_info:
        logging.info(f"Procedure: {proc_name}")
        logging.info(f"Description: {proc_info['description']}")
        if proc_info['parameters']:
            logging.info("Parameters:")
            for param in proc_info['parameters']:
                logging.info(f"  - {param['name']} ({param['type']})")

    results = tester.execute_proc(proc_name, params)

    if results is None:
        sys.exit(1)

    if mode == "baseline":
        tester.save_baseline(proc_name, params, results)
    elif mode == "test":
        # Find most recent baseline for this proc
        baseline_files = list(tester.baseline_dir.glob(f"{proc_name}_*.csv"))
        if not baseline_files:
            print("No baseline found for this procedure")
            sys.exit(1)
        
        latest_baseline = max(baseline_files, key=lambda x: x.stat().st_mtime)
        tester.compare_results(results, latest_baseline)
    else:
        print("Invalid mode. Use 'baseline' or 'test'")
        sys.exit(1)

if __name__ == "__main__":
    main() 