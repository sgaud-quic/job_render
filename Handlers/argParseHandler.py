# Copyright (c) Qualcomm Technologies, Inc. and/or its subsidiaries.
# SPDX-License-Identifier: BSD-3-Clause-Clear

import argparse
import logging


class ArgParseHandler:
    def __init__(self, test_data):
        self.test_data = test_data
        logging.debug('Initializing ArgParseHandler')
        
        # Parsing the tests through command line arguments
        parser = argparse.ArgumentParser(description="parsing test names")
        logging.debug('Created ArgumentParser')

        # Adding optional arguments node and tree
        parser.add_argument('--node', type=str, help='Node value')
        parser.add_argument('--tree', type=str, help='Tree value')
        parser.add_argument('--buildurl', type=str, help='custom build json url')
        parser.add_argument('--localjson', type=str, help='local json parsing')
        parser.add_argument('--template', type=str, help='For parsing local path or web url for template')
        logging.debug('Added optional arguments')

        if self.test_data is not None:
            test_names = self.test_data[0]['contents']
            logging.debug('Parsed test names from test_data')

            for test_name in test_names:
                arg_name = test_name["name"].removesuffix(".yaml")
                parser.add_argument('--' + arg_name, help=f'Example: {test_name["name"]} argument', action="store_true")
                logging.debug(f'Added argument for test name: {arg_name}')

        self.argument = parser.parse_args()
        logging.debug('Parsed command line arguments') 
    
    def get_node_id(self):
        node_id = self.argument.node
        logging.debug(f'Node ID: {node_id}')
        return node_id
    
    def get_tree_value(self):
        tree_value = self.argument.tree or 'mainline'
        logging.debug(f'Tree value: {tree_value}')
        return tree_value
    
    def get_buildurl(self):
        buildurl = self.argument.buildurl
        logging.debug(f'Build URL: {buildurl}')
        return buildurl
    
    def get_local_json_path(self):
        local_json_path = self.argument.localjson
        logging.debug(f'Local JSON path: {local_json_path}')
        return local_json_path
    
    def is_argname_passed(self, arg_name):
        passed = getattr(self.argument, arg_name)
        logging.debug(f'Argument {arg_name} passed: {passed}')
        return passed
    
    def get_template_path(self):
        template_path = self.argument.template
        logging.debug(f'Template path: {template_path}')
        return template_path
