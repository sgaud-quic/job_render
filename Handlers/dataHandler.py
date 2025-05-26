# Copyright (c) Qualcomm Technologies, Inc. and/or its subsidiaries.
# SPDX-License-Identifier: BSD-3-Clause-Clear

import requests
from utils.generate_url_with_optional_node_id import build_url
from utils.filter_files import filter_data
import sys, json, os, logging

class DataHandler:
    def __init__(self, node_value=None, tree_value=None, build_url_main=None, local_json_path=None):
        self.node_value = node_value
        self.tree_value = tree_value or "mainline"
        self.is_buildurl_provided = build_url_main
        self.node_id_value = node_value
        self.build_url_main = build_url_main
        self.local_json_path = local_json_path
        self.data = None
        self.tests_count = 0
        logging.debug('DataHandler initialized with node_value: %s, tree_value: %s, build_url_main: %s, local_json_path: %s', node_value, tree_value, build_url_main, local_json_path)
        

        if self.local_json_path is not None:
            logging.debug('Local JSON path provided: %s', self.local_json_path)
        elif self.build_url_main is None: 
            if self.node_value is None:
                total_nodes_of_required_filter = self.fetch_total_nodes()
                self.build_url_main = build_url(id_value = self.node_id_value, tree = self.tree_value, offset = total_nodes_of_required_filter-1)
                logging.debug('Generated build_url_main with offset: %s', self.build_url_main)
            else:
                self.build_url_main = build_url(id_value = self.node_id_value, tree = self.tree_value)
                logging.debug('Generated build_url_main: %s', self.build_url_main)

    def fetch_total_nodes(self):
        target_kernelci_mainline_total_node_url = build_url(id_value=self.node_id_value, tree=self.tree_value)
        logging.debug('Fetching total nodes from URL: %s', target_kernelci_mainline_total_node_url)
        response = requests.get(target_kernelci_mainline_total_node_url)
        response.raise_for_status()
        total_nodes = response.json()["total"]
        logging.debug('Total nodes fetched: %d', total_nodes)
        return total_nodes #gets total number of nodes after applying filters
    
    def fetch_data(self):
        try:
            if self.local_json_path is not None:
                logging.debug('Fetching data from local JSON path: %s', self.local_json_path)
                with open(self.local_json_path, 'r') as data_file:
                    self.data = json.load(data_file)
                logging.debug('Data fetched from local JSON')
            else :
                logging.debug('Fetching data from URL: %s', self.build_url_main)
                response = requests.get(self.build_url_main)
                response.raise_for_status()
                self.data = response.json()
                logging.debug('Data fetched from URL')
                self.extract_data()
        except requests.exceptions.HTTPError as http_err:
            logging.error('HTTP error occurred: %s', http_err)
            print(f"HTTP error occurred: {http_err}")
            sys.exit(1)
        except requests.exceptions.ConnectionError as conn_err:
            logging.error('Connection error occurred: %s', conn_err)
            print(f"Connection error occurred: {conn_err}")
            sys.exit(1)
        except requests.exceptions.Timeout as timeout_err:
            logging.error('Timeout error occurred: %s', timeout_err)
            print(f"Timeout error occurred: {timeout_err}")
            sys.exit(1)
        except requests.exceptions.RequestException as req_err:
            logging.error('Request error occurred: %s', req_err)
            print(f"An error occurred: {req_err}")
            sys.exit(1)
        except ValueError as json_err:
            logging.error('JSON decoding error: %s', json_err)
            print(f"JSON decoding error: {json_err}")
            sys.exit(1)
        except Exception as e:
            logging.error('An unexpected error occurred in fetching data: %s', e)
            print(f"An unexpected error occurred in fetching data: {e}")
            sys.exit(1)

    def extract_data(self):
        logging.debug('Extracting data')
        if self.node_id_value is None and self.is_buildurl_provided is None:
            number_of_nodes = len(self.data['items'])
            self.data = self.data['items'][number_of_nodes-1]
            self.node_id_value = self.data['id']
            logging.debug('Extracted node_id_value: %s', self.node_id_value)

    def log_details(self):
        if self.node_value is not None:
            print(f"Successfully fetched JSON from Maestro Server using the provided node ID({self.node_value}).")
            print(f"Node value: {self.node_value}")
        elif self.is_buildurl_provided is not None:
            print(f"Successfully fetched JSON from the organization's internal server URL({self.is_buildurl_provided}).")
        elif self.local_json_path is not None:
            print(f"Successfully fetched JSON from the local path({self.local_json_path}).")
        else:
            print(f"Successfully fetched latest node's({self.node_id_value}) JSON from Maestro Server.")
            print(f"Node value: {self.node_id_value} (latest)")

        # print(f"Tree value: {self.tree_value}")
        print(f"Tree value: {self.tree_value}")

    def extract_folder_path(self):
        folder_path = os.path.dirname(self.local_json_path)
        return folder_path

    def fetch_and_update_dtb(self, target_database):
        target_dtb = target_database
        target_dtb = 'dtbs/qcom/'+target_dtb+'.dtb'
        logging.debug('Target DTB path: %s', target_dtb)

        if self.local_json_path is not None:
            logging.debug('Fetching DTB from local JSON path')
            folder_path = self.extract_folder_path()
            folder_path+='/metadata.json'
            try:
                with open(folder_path, 'r') as data_file:
                    json_metadata = json.load(data_file)
                response_artifacts = json_metadata['artifacts']
                response_target_dtb = response_artifacts[target_dtb]
                self.data['artifacts']['dtb'] = response_target_dtb
                logging.debug('DTB fetched and updated from local JSON: %s', response_target_dtb)
            except FileNotFoundError:
                logging.error('Local JSON file not found: %s', folder_path)
                sys.exit(1)
            except json.JSONDecodeError:
                logging.error('Error decoding JSON from local file: %s', folder_path)
                sys.exit(1)
            except Exception as e:
                logging.error('An unexpected error occurred: %s', e)
                sys.exit(1)
        else:
            logging.debug('Fetching DTB from remote URL')
            dtb_url = self.data['artifacts']['metadata']
            

            try:
                get_response_dtb = requests.get(dtb_url)
                get_response_dtb.raise_for_status()
                response_json = get_response_dtb.json()
                response_artifacts = response_json['artifacts']
                response_target_dtb = response_artifacts[target_dtb]
                self.data['artifacts']['dtb'] = response_target_dtb
                logging.debug('DTB fetched and updated from remote URL: %s', response_target_dtb)
            except requests.exceptions.RequestException as e:
                logging.error('Request error: %s', e)
                sys.exit(1)
            except ValueError:
                logging.error('Response is not in JSON format')
                print("Response is not in JSON format")
                sys.exit(1)
            except Exception as e:
                logging.error('An unexpected error occurred: %s', e)
                print(f"An unexpected error occurred: {e}")
                sys.exit(1)
        logging.info('DTB URL added successfully')
        print('dtb url added successfully')
    
    def extract_test_name(self, file_path):
        #extracting data and updating node_id_value
        # Split the path by '/' and get the last part
        file_name = file_path.split('/')[-1]
        # Remove the '.yaml' extension
        test_name = file_name.replace('.yaml', '')
        return test_name
    
    def put_tests_into_fetched_data(self, test_names, arg_parse_handler, test_data):
        logging.debug('put_tests_into_fetched_data called with test_names: %s', test_names)
        logging.debug('put_tests_into_fetched_data called with test_data: %s', test_data)
        for test_name in test_names:
            # arg_name_original = test_name["name"]
            arg_name = test_name["name"].removesuffix(".yaml").replace('-', '_')
            print("arg_name", arg_name)
            if arg_parse_handler.is_argname_passed(arg_name=arg_name):
                logging.info(f"You have used '--{arg_name}' argument")
                print(f"You have used '--{test_name['name']}' argument")
                # pushing tests into the data's tests list
                specific_test_paths = filter_data(test_data,folder_name='/'+test_name['name'], data_type='yaml')
                print("specific_test_paths",specific_test_paths)
                for specific_test_path in specific_test_paths:
                    specific_test_name = self.extract_test_name(specific_test_path)
                    self.data.setdefault("tests", []).append({
                        "repository": "https://github.com/qualcomm-linux/qcom-linux-testkit.git",
                        "from": "git",
                        "path": f"Runner/plans{specific_test_path}",
                        "name": f"{specific_test_name}-tests"
                    })
                    self.tests_count+=1
                    logging.debug('Added test: %s', specific_test_name)
                
        if self.tests_count==0:
            print("Job definition will be created without test.")
            logging.warning("Job definition will be created without test.")

    def get_fetched_data(self):
        logging.debug('get_fetched_data called')
        return self.data
    
    def get_count_of_tests(self):
        logging.debug('get_count_of_tests called')
        count_of_tests = self.tests_count
        logging.debug('Count of tests: %d', count_of_tests)
        return self.tests_count
