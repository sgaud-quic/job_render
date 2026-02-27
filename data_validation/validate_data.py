# Copyright (c) Qualcomm Technologies, Inc. and/or its subsidiaries.
# SPDX-License-Identifier: BSD-3-Clause-Clear

import sys

# Allowed boot methods
allowed_boot_methods = ['fastboot', 'u-boot', 'flash']


class Validator:
    def __init__(self, platform_config, test_method):
        self.platform_config = platform_config
        self.test_method = test_method


    def validate_platform_config(self):
        required_keys = {'boot_method', 'name'}
        
        # Check if all required keys are present
        if not required_keys.issubset(self.platform_config.keys()):
            return False, "Missing required keys in platform_config"
        
        # Check if boot_method is valid
        if self.platform_config['boot_method'] not in allowed_boot_methods:
            return False, f"Invalid boot_method: {self.platform_config['boot_method']}. Allowed values are {allowed_boot_methods},use export command to set environment variables"
        
        return True, "Valid platform_config"


    def validate_test_method(self):
        # Add any specific validation for test_method if needed
        if not isinstance(self.test_method, str):
            return False, "test_method should be a string"
        
        return True, "Valid test_method"
    

    def perform_validations_and_proceed(self):
        try:
            # Validate platform_config
            is_valid_platform_config, platform_config_message = self.validate_platform_config()
            print(platform_config_message)
            
            # Validate test_method
            is_valid_test_method, test_method_message = self.validate_test_method()
            print(test_method_message)
            
            # Check validation results and raise an exception if any validation fails
            if not is_valid_platform_config:
                raise ValueError(platform_config_message)
            if not is_valid_test_method:
                raise ValueError(test_method_message)
            
            print("All validations passed. Proceeding with the program...")
        except ValueError as val_err:
            print(f"Validation error: {val_err}")
            sys.exit(1)
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            sys.exit(1)
