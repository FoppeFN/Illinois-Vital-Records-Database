import json
import psycopg2 # The Python-PostgreSQL library
from urllib.parse import parse_qs
import os 
import datetime 

# ====================================================================
# *** NEW DEBUGGING FUNCTION ***
# ====================================================================
def log_to_file(message):
    log_path = '/srv/iivrd/debug.log'
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    try:
        with open(log_path, 'a') as f:
            f.write(f'[{timestamp}] {message}\n')
    except Exception as e:
        try:
            with open(log_path, 'a') as f:
                f.write(f'[{timestamp}] LOGGING FAILED: {str(e)}\n')
        except:
            pass 

# ====================================================================
# API LOGIC (Unchanged)
# ====================================================================
def handle_api_search(environ, start_response):
    log_to_file('Inside handle_api_search') 
    allowed_origin = 'https.home.cs.siue.edu'
    if environ.get('HTTP_ORIGIN') == 'http://localhost:5173':
        allowed_origin = 'http://localhost:5173'

    try:
        qs = environ.get('QUERY_STRING', '')
        params_dict = parse_qs(qs)
        log_to_file(f'Query Params: {params_dict}')
        
        def get_param(key):
            val_list = params_dict.get(key)
            if val_list and len(val_list) > 0:
                return val_list[0]
            return None

        first_name = get_param('first_name')
        last_name = get_param('last_name')
        year = get_param('year')
        county = get_param('county')
        record_type = get_param('record_type')

    except Exception as e:
        log_to_file(f'API Error (Parsing Params): {str(e)}')
        status = '400 Bad Request'
        output = json.dumps({'error': 'Error parsing query string', 'details': str(e)}).encode('utf-8')
        response_headers = [('Content-type', 'application/json'), ('Content-Length', str(len(output)))]
        start_response(status, response_headers)
        return [output]

    query = "SELECT record_id, first_name, last_name, county, year FROM iva.records WHERE 1=1"
    params = []

    if first_name:
        query += " AND first_name ILIKE %s"
        params.append(f"%{first_name}%")
    if last_name:
        query += " AND last_name ILIKE %s"
        params.append(f"%{last_name}%")
    if year:
        try:
            int_year = int(year)
            query += " AND year = %s"
            params.append(int_year)
        except ValueError:
            pass
    if county:
        query += " AND county ILIKE %s"
        params.append(f"%{county}%")
    if record_type:
        query += " AND record_type = %s"
        params.append(record_type)
    
    query += " ORDER BY year, last_name, first_name LIMIT 100"
    log_to_file(f'SQL Query: {query}')

    results = []
    try:
        conn = psycopg2.connect(
            dbname='iivrd',
            user='iivrd',
            password='camunian rose',
        )
        cursor = conn.cursor()
        cursor.execute(query, tuple(params))
        
        columns = [col[0] for col in cursor.description]
        results = [
            dict(zip(columns, row))
            for row in cursor.fetchall()
        ]
        
        cursor.close()
        conn.close()
        log_to_file(f'Found {len(results)} results.')

    except Exception as e:
        log_to_file(f'API Error (Database): {str(e)}')
        status = '500 Internal Server Error'
        output = json.dumps({'error': 'Database query failed', 'details': str(e)}).encode('utf-8')
        response_headers = [
            ('Content-type', 'application/json'),
            ('Content-Length', str(len(output))),
            ('Access-Control-Allow-Origin', allowed_origin) 
        ]
        start_response(status, response_headers)
        return [output]

    status = '200 OK'
    output_data = {'results': results}
    output = json.dumps(output_data).encode('utf-8')
    
    response_headers = [
        ('Content-type', 'application/json'),
        ('Content-Length', str(len(output))),
        ('Access-Control-Allow-Origin', allowed_origin),
        ('Access-Control-Allow-Methods', 'GET, OPTIONS'),
        ('Access-Control-Allow-Headers', 'Content-Type')
    ]
    
    start_response(status, response_headers)
    return [output]


# ====================================================================
# MAIN WSGI ROUTER (This part is updated)
# ====================================================================
def application(environ, start_response):
    """
    The main WSGI application.
    """
    
    path = environ.get('PATH_INFO', '/')
    qs = environ.get('QUERY_STRING', '') # <-- We now read the query string
    static_dir = '/srv/iivrd/static'
    
    log_to_file(f"Request received. PATH_INFO: '{path}', QUERY_STRING: '{qs}'")
    
    allowed_origin = 'https.home.cs.siue.edu'
    if environ.get('HTTP_ORIGIN') == 'http://localhost:5173':
        allowed_origin = 'http://localhost:5173'
    
    # --- Rule 1: Handle CORS "preflight" request (for OPTIONS) ---
    if environ['REQUEST_METHOD'] == 'OPTIONS':
        log_to_file("Handling OPTIONS request.")
        status = '204 No Content'
        response_headers = [
            ('Access-Control-Allow-Origin', allowed_origin),
            ('Access-Control-Allow-Methods', 'GET, OPTIONS'),
            ('Access-Control-Allow-Headers', 'Content-Type'),
            ('Content-Length', '0')
        ]
        start_response(status, response_headers)
        return []

    # --- *** NEW ROUTING LOGIC *** ---
    # --- Rule 2: Handle API calls (if there is ANY query string) ---
    if qs: 
        log_to_file("Routing to API (query string detected).")
        return handle_api_search(environ, start_response)
    
    # --- Rule 3: Handle static files ---
    if path.startswith('/assets/'):
        log_to_file("Routing to static asset.")
        try:
            file_path = os.path.join(static_dir, path.lstrip('/'))
            if not os.path.realpath(file_path).startswith(os.path.realpath(static_dir)):
                 raise FileNotFoundError

            with open(file_path, 'rb') as f:
                output = f.read()
            
            content_type = 'text/javascript' if path.endswith('.js') else 'text/css'
            status = '200 OK'
            response_headers = [
                ('Content-type', content_type),
                ('Content-Length', str(len(output)))
            ]
            start_response(status, response_headers)
            return [output]

        except FileNotFoundError:
            log_to_file(f"Asset not found: {file_path}")
            status = '404 Not Found'
            output = f'Static file not found at {file_path}'.encode('utf-8')
            response_headers = [('Content-type', 'text/plain'), ('Content-Length', str(len(output)))]
            start_response(status, response_headers)
            return [output]

    # --- Rule 4: Handle all other requests (serve the React app) ---
    log_to_file("Routing to index.html (no path, no query string).")
    try:
        html_path = os.path.join(static_dir, 'index.html')
        with open(html_path, 'rb') as f:
            output = f.read()
        
        status = '200 OK'
        response_headers = [
            ('Content-type', 'text/html'),
            ('Content-Length', str(len(output)))
        ]
        start_response(status, response_headers)
        return [output]
    
    except FileNotFoundError:
        log_to_file("index.html not found.")
        status = '404 Not Found'
        output = b'React index.html not found. Have you built and deployed your app?'
        response_headers = [('Content-type', 'text/plain'), ('Content-Length', str(len(output)))]
        start_response(status, response_headers)
        return [output]
