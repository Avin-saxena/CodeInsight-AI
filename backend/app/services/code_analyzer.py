import tree_sitter_python as tspython
from tree_sitter import Language, Parser
import os
import json

# Initializing the language
PY_LANGUAGE = Language(tspython.language())
parser = Parser(PY_LANGUAGE)

def get_node_text(node, source_code):
    return source_code[node.start_byte:node.end_byte].decode('utf-8')

def extract_function_parameters(func_node, source_code):
    parameters = []
    params_node = func_node.child_by_field_name('parameters')
    if params_node:
        for param in params_node.named_children:
            param_info = {'name': get_node_text(param, source_code)}
            
         
            if param.type == 'typed_parameter':
                name_node = param.child_by_field_name('name')
                type_node = param.child_by_field_name('type')
                if name_node:
                    param_info['name'] = get_node_text(name_node, source_code)
                if type_node:
                    param_info['type'] = get_node_text(type_node, source_code)
            
          
            if param.type == 'default_parameter':
                name_node = param.child_by_field_name('name')
                value_node = param.child_by_field_name('value')
                if name_node:
                    param_info['name'] = get_node_text(name_node, source_code)
                if value_node:
                    param_info['default'] = get_node_text(value_node, source_code)
            
            parameters.append(param_info)
    return parameters

def handle_imports(node, source_code, collected_info):
    if node.type == 'import_statement':
        for child in node.named_children:
            if child.type == 'dotted_name':
                module_name = get_node_text(child, source_code)
                collected_info['imports'].append({'module': module_name})
            elif child.type == 'aliased_import':
                module_name_node = child.child_by_field_name('name')
                alias_node = child.child_by_field_name('alias')
                if module_name_node:
                    module_name = get_node_text(module_name_node, source_code)
                    if alias_node:
                        alias = get_node_text(alias_node, source_code)
                        collected_info['imports'].append({'module': module_name, 'alias': alias})
                    else:
                        collected_info['imports'].append({'module': module_name})
    elif node.type == 'import_from_statement':
        module_name_node = node.child_by_field_name('module')
        names_node = node.child_by_field_name('names')
        if module_name_node and names_node:
            module_name = get_node_text(module_name_node, source_code)
            for child in names_node.named_children:
                imported_name = get_node_text(child, source_code)
                collected_info['imports'].append({'module': module_name, 'name': imported_name})
                collected_info['imported_functions'][imported_name] = module_name

def handle_decorated_function(node, source_code, collected_info):
    decorator_nodes = []
    current_node = node
    
    # collecting all decorator nodes
    while current_node.type == 'decorated_definition':
        decorator_node = current_node.child_by_field_name('decorator')
        if decorator_node:
            decorator_nodes.append(decorator_node)
        current_node = current_node.child_by_field_name('definition')
    
    # getting the actual function node
    if not current_node or current_node.type not in ['function_definition', 'async_function_definition']:
        return
    
    
    name_node = current_node.child_by_field_name('name')
    if not name_node:
        return
        
    function_info = {
        'name': get_node_text(name_node, source_code),
        'decorators': [],
        'is_async': current_node.type == 'async_function_definition',
        'parameters': extract_function_parameters(current_node, source_code)
    }
    
    # processing each decorator
    for decorator_node in decorator_nodes:
        # finding the identifier node (skipping the @ symbol)
        for child in decorator_node.children:
            if child.type == 'identifier':
                function_info['decorators'].append({
                    'name': get_node_text(child, source_code),
                    'arguments': []
                })
                break
            elif child.type == 'call':
                func_node = child.child_by_field_name('function')
                if func_node:
                    decorator_name = get_node_text(func_node, source_code)
                    decorator_info = {
                        'name': decorator_name,
                        'arguments': []
                    }
                    
                 
                    args_node = child.child_by_field_name('arguments')
                    if args_node:
                        for arg in args_node.named_children:
                            arg_text = get_node_text(arg, source_code)
                            decorator_info['arguments'].append(arg_text)
                            
                    function_info['decorators'].append(decorator_info)
                    break
    

    collected_info['decorated_functions'].append(function_info)
    
 
    if function_info['name'] not in collected_info['functions']:
        collected_info['functions'].append(function_info['name'])

def analyze_api_calls(node, source_code, collected_info):
    if node.type == 'call':
        func_node = node.child_by_field_name('function')
        if func_node:
            func_name = get_node_text(func_node, source_code)
            
           
            if any(func_name.endswith(method) for method in ['.post', '.get', '.put', '.delete']):
                call_info = {
                    'client_library': func_name.split('.')[0],
                    'method': func_name.split('.')[-1],
                    'arguments': {}
                }
                
                args_node = node.child_by_field_name('arguments')
                if args_node:
                    for arg in args_node.named_children:
                        if arg.type == 'keyword_argument':
                            key_node = arg.child_by_field_name('name')
                            value_node = arg.child_by_field_name('value')
                            if key_node and value_node:
                                key = get_node_text(key_node, source_code)
                                value = get_node_text(value_node, source_code)
                                call_info['arguments'][key] = value
                        elif arg.type == 'string':
                            url = get_node_text(arg, source_code)
                            if 'url' not in call_info['arguments'] and ('ask_url' in url or 'ask_file' in url):
                                call_info['arguments']['url'] = url
                                call_info['endpoint'] = url.split('/')[-1]
                
                collected_info['api_calls'].append(call_info)

def walk(node, source_code, parent_type=None, collected_info=None):
    if collected_info is None:
        collected_info = {
            'functions': [],
            'classes': [],
            'function_calls': [],
            'imports': [],
            'node_types': {},
            'relationships': [],
            'current_class': None,
            'imported_functions': {},
            'imported_modules': {},
            'api_calls': [],
            'endpoints': {},
            'decorated_functions': [],
            'async_functions': set(),
            'parameter_relationships': {},
            'function_dependencies': {},
            'class_hierarchy': {},
            'variable_usage': {},
            'current_function': None,
            'error_handling': set()
        }

    node_type = node.type
    collected_info['node_types'][node_type] = collected_info['node_types'].get(node_type, 0) + 1

    # handling regular function definitions
    if node_type in ['function_definition', 'async_function_definition']:
        func_name_node = node.child_by_field_name('name')
        if func_name_node:
            collected_info['current_function'] = get_node_text(func_name_node, source_code)
            func_name = collected_info['current_function']
            if func_name not in collected_info['functions']:
                collected_info['functions'].append(func_name)
            
            # checking for async functions
            if node_type == 'async_function_definition' or any(child.type == 'async' for child in node.children):
                collected_info['async_functions'].add(func_name)
            
            if collected_info['current_class']:
                collected_info['relationships'].append({
                    'class': collected_info['current_class'],
                    'function': func_name,
                    'is_async': node_type == 'async_function_definition'
                })
                
                if collected_info['current_class'] not in collected_info['class_hierarchy']:
                    collected_info['class_hierarchy'][collected_info['current_class']] = {
                        'methods': [],
                        'parent_classes': []
                    }
                collected_info['class_hierarchy'][collected_info['current_class']]['methods'].append(func_name)

            collected_info['function_dependencies'][func_name] = set()

    # Handling decorated functions
    elif node_type == 'decorated_definition':
        definition_node = node.child_by_field_name('definition')
        if definition_node:
            is_async = definition_node.type == 'async_function_definition' or any(child.type == 'async' for child in definition_node.children)
            func_name_node = definition_node.child_by_field_name('name')
            if func_name_node:
                func_name = get_node_text(func_name_node, source_code)
                if is_async:
                    collected_info['async_functions'].add(func_name)
                collected_info['current_function'] = func_name
                if func_name not in collected_info['functions']:
                    collected_info['functions'].append(func_name)
                collected_info['function_dependencies'][func_name] = set()
        handle_decorated_function(node, source_code, collected_info)

    # Handling class definitions
    elif node_type == 'class_definition':
        class_name_node = node.child_by_field_name('name')
        if class_name_node:
            class_name = get_node_text(class_name_node, source_code)
            collected_info['classes'].append(class_name)
            collected_info['current_class'] = class_name
            
            bases_node = node.child_by_field_name('bases')
            if bases_node:
                if class_name not in collected_info['class_hierarchy']:
                    collected_info['class_hierarchy'][class_name] = {
                        'methods': [],
                        'parent_classes': []
                    }
                for base in bases_node.named_children:
                    base_name = get_node_text(base, source_code)
                    collected_info['class_hierarchy'][class_name]['parent_classes'].append(base_name)

    # Handling function calls and API calls
    elif node_type == 'call':
        analyze_api_calls(node, source_code, collected_info)
        func_node = node.child_by_field_name('function')
        if func_node:
            func_name = get_node_text(func_node, source_code)
            collected_info['function_calls'].append(func_name)
            
            if collected_info['current_function']:
                collected_info['function_dependencies'][collected_info['current_function']].add(func_name)

    # handle error handling (try statements)
    elif node_type == 'try_statement':
        if collected_info['current_function']:
            collected_info['error_handling'].add(collected_info['current_function'])

    # Handling imports
    elif node_type in ['import_statement', 'import_from_statement']:
        handle_imports(node, source_code, collected_info)

    # Processing all children
    for child in node.children:
        walk(child, source_code, node_type, collected_info)

    if node_type == 'class_definition':
        collected_info['current_class'] = None
    elif node_type in ['function_definition', 'async_function_definition', 'decorated_definition']:
        collected_info['current_function'] = None

    return collected_info

def analyze_cross_references(app_info, api_info):
    """Analyze cross-references between app.py and api.py"""
    cross_references = {
        'direct_function_calls': set(),
        'imported_functions': set(),
        'endpoint_usage': {},
        'shared_dependencies': set()
    }

    api_functions = set(api_info['functions'])
    api_imports = {imp.get('module') or imp.get('name') for imp in api_info['imports']}
    app_imports = {imp.get('module') or imp.get('name') for imp in app_info['imports']}

    cross_references['shared_dependencies'] = api_imports.intersection(app_imports)

    for api_call in app_info['api_calls']:
        if 'endpoint' in api_call and api_call['endpoint']:
            endpoint_name = api_call['endpoint']
            
            # Matching with decorated functions in api.py
            for func in api_info['decorated_functions']:
                if func['name'] == endpoint_name or endpoint_name in [arg.strip("'\"") for dec in func['decorators'] for arg in dec.get('arguments', [])]:
                    cross_references['endpoint_usage'][endpoint_name] = {
                        'method': api_call['method'],
                        'handler': func['name'],
                        'call_pattern': api_call['arguments']
                    }
        elif func_call in api_functions:
            cross_references['imported_functions'].add(func_call)

    for imp in app_info['imports']:
        if imp.get('module') == 'api' or imp.get('name') in api_functions:
            if 'name' in imp:
                cross_references['imported_functions'].add(imp['name'])

    for api_call in app_info['api_calls']:
        url = api_call['arguments'].get('url', '').strip('"\' ')
        if '/ask_' in url:
            endpoint = '/' + url.split('/')[-1]
            if endpoint in api_info['endpoints']:
                cross_references['endpoint_usage'][endpoint] = {
                    'method': api_call['method'],
                    'handler': api_info['endpoints'][endpoint]['function'],
                    'call_pattern': api_call['arguments']
                }

    return cross_references

def convert_analysis_to_json(analysis):
    """Convert analysis results to JSON format."""
    if not analysis:
        return {"error": "No analysis results available"}

    app_info = analysis['app_info']
    api_info = analysis['api_info']
    cross_refs = analysis['cross_refs']

    return {
        "cross_reference_analysis": {
            "function_usage": {
                "direct_function_calls": list(cross_refs.get('direct_function_calls', [])),
                "imported_functions": list(cross_refs.get('imported_functions', []))
            },
            "api_integration": {
                "api_calls": [
                    {
                        "endpoint": call.get('endpoint', 'Unknown'),
                        "http_method": call['method'],
                        "client_library": call['client_library'],
                        "arguments": call['arguments']
                    }
                    for call in app_info.get('api_calls', [])
                ]
            },
            "shared_dependencies": list(cross_refs.get('shared_dependencies', []))
        },
        "function_call_chains": {
            "app_py": {
                function: list(dependencies)
                for function, dependencies in app_info.get('function_dependencies', {}).items()
                if dependencies
            },
            "api_py": {
                function: list(dependencies)
                for function, dependencies in api_info.get('function_dependencies', {}).items()
                if dependencies
            }
        },
        "node_type_frequencies": {
            "app_py": dict(app_info.get('node_types', {})),
            "api_py": dict(api_info.get('node_types', {}))
        },
        "error_handling": {
            "app_py": list(app_info.get('error_handling', [])),
            "api_py": list(api_info.get('error_handling', []))
        },
        "async_functions": {
            "app_py": list(app_info.get('async_functions', [])),
            "api_py": list(api_info.get('async_functions', []))
        },
        "decorated_functions": {
            "app_py": [
                {
                    "name": func['name'],
                    "decorators": [
                        {
                            "name": decorator['name'],
                            "arguments": decorator.get('arguments', [])
                        }
                        for decorator in func['decorators']
                    ]
                }
                for func in app_info.get('decorated_functions', [])
            ],
            "api_py": [
                {
                    "name": func['name'],
                    "decorators": [
                        {
                            "name": decorator['name'],
                            "arguments": decorator.get('arguments', [])
                        }
                        for decorator in func['decorators']
                    ]
                }
                for func in api_info.get('decorated_functions', [])
            ]
        },
        "function_parameters": {
            "app_py": [
                {
                    "function": func['name'],
                    "parameters": [
                        {
                            "name": param['name'],
                            "type": param.get('type'),
                            "default": param.get('default')
                        }
                        for param in func['parameters']
                    ]
                }
                for func in app_info.get('decorated_functions', [])
            ],
            "api_py": [
                {
                    "function": func['name'],
                    "parameters": [
                        {
                            "name": param['name'],
                            "type": param.get('type'),
                            "default": param.get('default')
                        }
                        for param in func['parameters']
                    ]
                }
                for func in api_info.get('decorated_functions', [])
            ]
        }
    }

def display_json_analysis(analysis):
    """Display analysis results in JSON format."""
    import json
    json_analysis = convert_analysis_to_json(analysis)
    print(json.dumps(json_analysis, indent=2))

def analyze_files(app_path, api_path):
    """Analyze both app.py and api.py files."""
    try:
        # Reading and parsing files
        with open(app_path, 'r', encoding='utf-8') as f:
            app_code = f.read()
        with open(api_path, 'r', encoding='utf-8') as f:
            api_code = f.read()

        app_tree = parser.parse(bytes(app_code, 'utf-8'))
        api_tree = parser.parse(bytes(api_code, 'utf-8'))

        # Analyzing both files
        app_info = walk(app_tree.root_node, bytes(app_code, 'utf-8'))
        api_info = walk(api_tree.root_node, bytes(api_code, 'utf-8'))

        # Performing cross-reference analysis
        cross_refs = analyze_cross_references(app_info, api_info)

        return {'app_info': app_info, 'api_info': api_info, 'cross_refs': cross_refs}

    except Exception as e:
        print(f"Error analyzing files: {str(e)}")
        return None

if __name__ == "__main__":
    analysis_result = analyze_files('app.py', 'api.py')
    if analysis_result:
        # first converting the analysis result to JSON format
        json_output = convert_analysis_to_json(analysis_result)
        
        # Save to file
        with open('code_analyzer_output.json', 'w', encoding='utf-8') as f:
            json.dump(json_output, f, indent=2)
        print("Analysis complete! Results saved to code_analyzer_output.json")
      
    else:
        print("Analysis failed to produce results")








def analyze_code(app_code: str, api_code: str) -> dict:
    try:
        app_tree = parser.parse(bytes(app_code, 'utf-8'))
        api_tree = parser.parse(bytes(api_code, 'utf-8'))
        
        # getting the detailed analysis
        app_info = walk(app_tree.root_node, bytes(app_code, 'utf-8'))
        api_info = walk(api_tree.root_node, bytes(api_code, 'utf-8'))

        # Adding cross reference analysis
        cross_refs = {
            'direct_function_calls': set(),
            'imported_functions': set(),
            'endpoint_usage': {},
            'shared_dependencies': set()
        }

        # Analyzing cross references
        api_functions = set(api_info['functions'])
        api_imports = {imp.get('module') or imp.get('name') for imp in api_info['imports']}
        app_imports = {imp.get('module') or imp.get('name') for imp in app_info['imports']}

        # Finding shared dependencies
        cross_refs['shared_dependencies'] = api_imports.intersection(app_imports)

        # Analyzing API endpoints and function usage
        for api_call in app_info['api_calls']:
            if 'endpoint' in api_call and api_call['endpoint']:
                endpoint_name = api_call['endpoint']
                
                # Matching with decorated functions in api.py
                for func in api_info['decorated_functions']:
                    if func['name'] == endpoint_name or endpoint_name in [
                        arg.strip("'\"") for dec in func['decorators'] 
                        for arg in dec.get('arguments', [])
                    ]:
                        cross_refs['endpoint_usage'][endpoint_name] = {
                            'method': api_call['method'],
                            'handler': func['name'],
                            'call_pattern': api_call['arguments']
                        }

        # Analyzing imported functions
        for imp in app_info['imports']:
            if imp.get('module') == 'api' or imp.get('name') in api_functions:
                if 'name' in imp:
                    cross_refs['imported_functions'].add(imp['name'])

        # Converting sets to lists for JSON serialization
        app_info['async_functions'] = list(app_info['async_functions'])
        app_info['error_handling'] = list(app_info['error_handling'])
        api_info['async_functions'] = list(api_info['async_functions'])
        api_info['error_handling'] = list(api_info['error_handling'])

        # Converting function dependencies sets to lists
        for func_name, deps in app_info['function_dependencies'].items():
            app_info['function_dependencies'][func_name] = list(deps)
        for func_name, deps in api_info['function_dependencies'].items():
            api_info['function_dependencies'][func_name] = list(deps)

        # Creating the formatted output matching the first file
        return {
            "cross_reference_analysis": {
                "function_usage": {
                    "direct_function_calls": list(cross_refs['direct_function_calls']),
                    "imported_functions": list(cross_refs['imported_functions'])
                },
                "api_integration": {
                    "api_calls": [
                        {
                            "endpoint": call.get('endpoint', 'Unknown'),
                            "http_method": call['method'],
                            "client_library": call['client_library'],
                            "arguments": call['arguments']
                        }
                        for call in app_info.get('api_calls', [])
                    ]
                },
                "shared_dependencies": list(cross_refs['shared_dependencies'])
            },
            "function_call_chains": {
                "app_py": app_info['function_dependencies'],
                "api_py": api_info['function_dependencies']
            },
            "node_type_frequencies": {
                "app_py": app_info['node_types'],
                "api_py": api_info['node_types']
            },
            "error_handling": {
                "app_py": app_info['error_handling'],
                "api_py": api_info['error_handling']
            },
            "async_functions": {
                "app_py": app_info['async_functions'],
                "api_py": api_info['async_functions']
            },
            "decorated_functions": {
                "app_py": [
                    {
                        "name": func['name'],
                        "decorators": [
                            {
                                "name": decorator['name'],
                                "arguments": decorator.get('arguments', [])
                            }
                            for decorator in func['decorators']
                        ]
                    }
                    for func in app_info.get('decorated_functions', [])
                ],
                "api_py": [
                    {
                        "name": func['name'],
                        "decorators": [
                            {
                                "name": decorator['name'],
                                "arguments": decorator.get('arguments', [])
                            }
                            for decorator in func['decorators']
                        ]
                    }
                    for func in api_info.get('decorated_functions', [])
                ]
            },
            "function_parameters": {
                "app_py": [
                    {
                        "function": func['name'],
                        "parameters": [
                            {
                                "name": param['name'],
                                "type": param.get('type'),
                                "default": param.get('default')
                            }
                            for param in func['parameters']
                        ]
                    }
                    for func in app_info.get('decorated_functions', [])
                ],
                "api_py": [
                    {
                        "function": func['name'],
                        "parameters": [
                            {
                                "name": param['name'],
                                "type": param.get('type'),
                                "default": param.get('default')
                            }
                            for param in func['parameters']
                        ]
                    }
                    for func in api_info.get('decorated_functions', [])
                ]
            }
        }
    except Exception as e:
        return {'error': str(e)}