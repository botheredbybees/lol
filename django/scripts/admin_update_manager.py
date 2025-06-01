#!/usr/bin/env python3
"""
Admin Update Manager for Training Package Data
Orchestrates the update process for training packages, qualifications, units, etc.
"""

import os
import sys
import json
from datetime import datetime
from dotenv import load_dotenv
import mysql.connector
from mysql.connector import errorcode

# Import your existing update scripts
from update_tps import get_current_training_packages, upsert_training_packages_to_db

class UpdateManager:
    def __init__(self):
        load_dotenv()
        self.config_file = 'update_config.json'
        self.load_config()
        
    def load_config(self):
        """Load configuration from JSON file"""
        default_config = {
            "selected_training_packages": [],
            "update_settings": {
                "download_xml": True,
                "process_qualifications": True,
                "process_units": True,
                "process_elements": True,
                "process_required_skills": True,
                "batch_size": 50
            },
            "last_full_update": None
        }
        
        try:
            with open(self.config_file, 'r') as f:
                self.config = json.load(f)
        except FileNotFoundError:
            self.config = default_config
            self.save_config()
    
    def save_config(self):
        """Save configuration to JSON file"""
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=2, default=str)
    
    def get_db_connection(self):
        """Get database connection using environment variables"""
        return mysql.connector.connect(
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD'),
            host=os.getenv('DB_HOST', '127.0.0.1'),
            database=os.getenv('DB_NAME'),
            port=int(os.getenv('DB_PORT', '3306'))
        )
    
    def get_available_training_packages(self):
        """Get list of available training packages from database"""
        try:
            cnx = self.get_db_connection()
            cursor = cnx.cursor()
            
            query = "SELECT tpCode, tpTitle, ReleaseDate, processed FROM lol_tps ORDER BY tpCode"
            cursor.execute(query)
            
            packages = []
            for (code, title, release_date, processed) in cursor:
                packages.append({
                    'code': code,
                    'title': title,
                    'release_date': release_date,
                    'processed': processed
                })
            
            cursor.close()
            cnx.close()
            return packages
            
        except mysql.connector.Error as err:
            print(f"Database error: {err}")
            return []
    
    def update_training_packages(self):
        """Step 1: Update training packages list"""
        print("=== Updating Training Package List ===")
        training_packages = get_current_training_packages()
        if training_packages:
            upsert_training_packages_to_db(training_packages, debug=False)
            print("Training packages updated successfully")
            return True
        else:
            print("Failed to retrieve training packages")
            return False
    
    def select_training_packages_interactive(self):
        """Interactive training package selection"""
        packages = self.get_available_training_packages()
        if not packages:
            print("No training packages found. Run update_training_packages first.")
            return
        
        print("\n=== Available Training Packages ===")
        for i, pkg in enumerate(packages, 1):
            status = "✓" if pkg['processed'] == 'Y' else "○"
            print(f"{i:3d}. {status} {pkg['code']} - {pkg['title'][:60]}...")
        
        print("\nSelect packages to process:")
        print("Enter numbers separated by spaces (e.g., 1 3 5 10-15)")
        print("Or 'all' for all packages")
        
        selection = input("Selection: ").strip()
        
        selected_codes = []
        if selection.lower() == 'all':
            selected_codes = [pkg['code'] for pkg in packages]
        else:
            try:
                for part in selection.split():
                    if '-' in part:
                        start, end = map(int, part.split('-'))
                        for i in range(start, end + 1):
                            if 1 <= i <= len(packages):
                                selected_codes.append(packages[i-1]['code'])
                    else:
                        i = int(part)
                        if 1 <= i <= len(packages):
                            selected_codes.append(packages[i-1]['code'])
            except ValueError:
                print("Invalid selection format")
                return
        
        self.config['selected_training_packages'] = list(set(selected_codes))
        self.save_config()
        
        print(f"\nSelected {len(selected_codes)} training packages:")
        for code in selected_codes:
            pkg = next((p for p in packages if p['code'] == code), None)
            if pkg:
                print(f"  - {code}: {pkg['title'][:50]}...")
    
    def process_selected_packages(self):
        """Process the selected training packages"""
        selected = self.config.get('selected_training_packages', [])
        if not selected:
            print("No training packages selected. Use select_packages first.")
            return
        
        settings = self.config.get('update_settings', {})
        
        print(f"\n=== Processing {len(selected)} Training Packages ===")
        
        # Process qualifications
        if settings.get('process_qualifications', True):
            print("\n--- Processing Qualifications ---")
            self.process_qualifications(selected)
        
        # Process units
        if settings.get('process_units', True):
            print("\n--- Processing Units ---")
            self.process_units(selected)
        
        # Process elements and performance criteria
        if settings.get('process_elements', True):
            print("\n--- Processing Elements and Performance Criteria ---")
            self.process_elements_and_pcs(selected)
        
        # Process required skills
        if settings.get('process_required_skills', True):
            print("\n--- Processing Required Skills ---")
            self.process_required_skills(selected)
        
        # Update last run timestamp
        self.config['last_full_update'] = datetime.now().isoformat()
        self.save_config()
        
        print("\n=== Processing Complete ===")
    
    def process_qualifications(self, tp_codes):
        """Placeholder for qualification processing"""
        print("Qualification processing not yet implemented")
        print(f"Would process qualifications for: {', '.join(tp_codes)}")
    
    def process_units(self, tp_codes):
        """Placeholder for unit processing"""
        print("Unit processing not yet implemented")
        print(f"Would process units for: {', '.join(tp_codes)}")
    
    def process_elements_and_pcs(self, tp_codes):
        """Placeholder for elements and performance criteria processing"""
        print("Elements/PC processing not yet implemented")
        print(f"Would process elements/PCs for: {', '.join(tp_codes)}")
    
    def process_required_skills(self, tp_codes):
        """Placeholder for required skills processing"""
        print("Required skills processing not yet implemented")
        print(f"Would process required skills for: {', '.join(tp_codes)}")
    
    def show_status(self):
        """Show current status of training packages"""
        packages = self.get_available_training_packages()
        
        total = len(packages)
        processed = len([p for p in packages if p['processed'] == 'Y'])
        unprocessed = total - processed
        
        print(f"\n=== Training Package Status ===")
        print(f"Total packages: {total}")
        print(f"Processed: {processed}")
        print(f"Unprocessed: {unprocessed}")
        
        selected = self.config.get('selected_training_packages', [])
        if selected:
            print(f"Selected for processing: {len(selected)}")
            
        last_update = self.config.get('last_full_update')
        if last_update:
            print(f"Last full update: {last_update}")
    
    def interactive_menu(self):
        """Interactive menu for administrators"""
        while True:
            print("\n" + "="*50)
            print("Training Package Update Manager")
            print("="*50)
            print("1. Update training package list from training.gov.au")
            print("2. Show current status")
            print("3. Select training packages to process")
            print("4. Process selected training packages")
            print("5. Configuration settings")
            print("0. Exit")
            
            choice = input("\nEnter your choice (0-5): ").strip()
            
            if choice == '0':
                break
            elif choice == '1':
                self.update_training_packages()
            elif choice == '2':
                self.show_status()
            elif choice == '3':
                self.select_training_packages_interactive()
            elif choice == '4':
                self.process_selected_packages()
            elif choice == '5':
                self.configure_settings()
            else:
                print("Invalid choice. Please try again.")
    
    def configure_settings(self):
        """Configure update settings"""
        settings = self.config.get('update_settings', {})
        
        print("\n=== Configuration Settings ===")
        print(f"1. Process qualifications: {settings.get('process_qualifications', True)}")
        print(f"2. Process units: {settings.get('process_units', True)}")
        print(f"3. Process elements: {settings.get('process_elements', True)}")
        print(f"4. Process required skills: {settings.get('process_required_skills', True)}")
        print(f"5. Batch size: {settings.get('batch_size', 50)}")
        print("6. Back to main menu")
        
        choice = input("\nChange setting (1-6): ").strip()
        
        if choice in ['1', '2', '3', '4']:
            setting_map = {
                '1': 'process_qualifications',
                '2': 'process_units',
                '3': 'process_elements',
                '4': 'process_required_skills'
            }
            key = setting_map[choice]
            current = settings.get(key, True)
            settings[key] = not current
            self.config['update_settings'] = settings
            self.save_config()
            print(f"Changed {key} to {not current}")
        elif choice == '5':
            try:
                new_size = int(input("Enter new batch size: "))
                settings['batch_size'] = new_size
                self.config['update_settings'] = settings
                self.save_config()
                print(f"Batch size changed to {new_size}")
            except ValueError:
                print("Invalid batch size")

def main():
    if len(sys.argv) > 1:
        # Command line mode
        manager = UpdateManager()
        
        if sys.argv[1] == 'update_tps':
            manager.update_training_packages()
        elif sys.argv[1] == 'process':
            if len(sys.argv) > 2:
                # Process specific packages
                codes = sys.argv[2].split(',')
                manager.config['selected_training_packages'] = codes
                manager.process_selected_packages()
            else:
                manager.process_selected_packages()
        elif sys.argv[1] == 'status':
            manager.show_status()
        else:
            print("Usage: python admin_update_manager.py [update_tps|process|status]")
    else:
        # Interactive mode
        manager = UpdateManager()
        manager.interactive_menu()

if __name__ == "__main__":
    main()