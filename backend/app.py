import os
import sys
import time
import uuid
import threading
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS

# Import CourtSearch scrapers from sibling directory
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'CourtSearch'))
from scrapers import SearchCriteria, search_court_records, get_api_response, get_scraper

# Resolve the dist directory (built React frontend)
DIST_DIR = os.path.join(os.path.dirname(__file__), '..', 'dist')

app = Flask(__name__, static_folder=DIST_DIR, static_url_path='')
CORS(app)

# In-memory job store: { job_id: { status, message, result, error } }
jobs = {}


OPEN_STATUSES = {'open', 'active', 'pending'}
COUNTIES = ['miami-dade', 'broward']


def run_search(job_id, criteria):
    """Run court search in background thread and update job store."""
    start_time = time.time()
    try:
        jobs[job_id]['status'] = 'running'

        # Only search Florida counties (Miami-Dade, Broward)
        all_cases = []
        for county in COUNTIES:
            jobs[job_id]['message'] = f'Searching {county.replace("-", " ").title()} County...'
            scraper = get_scraper(county)
            cases = scraper.search(criteria)
            all_cases.extend(cases)

        # Filter out closed cases — only keep open/active/pending
        open_cases = [c for c in all_cases if c.status.lower() in OPEN_STATUSES]

        jobs[job_id]['message'] = 'Compiling results...'
        result = get_api_response(open_cases, criteria)

        jobs[job_id]['result'] = result
        jobs[job_id]['status'] = 'complete'
        jobs[job_id]['message'] = 'Search complete'

        elapsed = time.time() - start_time
        print(f'[Search] {criteria.first_name} {criteria.last_name} — '
              f'{len(open_cases)} open cases (of {len(cases)} total) — '
              f'{elapsed:.1f}s')
    except Exception as e:
        elapsed = time.time() - start_time
        print(f'[Search] {criteria.first_name} {criteria.last_name} — '
              f'ERROR after {elapsed:.1f}s: {e}')
        jobs[job_id]['status'] = 'error'
        jobs[job_id]['error'] = str(e)
        jobs[job_id]['message'] = f'Error: {str(e)}'


@app.route('/api/search', methods=['POST'])
def start_search():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Request body required'}), 400

    first_name = (data.get('first_name') or '').strip()
    last_name = (data.get('last_name') or '').strip()

    if not first_name or not last_name:
        return jsonify({'error': 'first_name and last_name are required'}), 400

    middle_name = (data.get('middle_name') or '').strip() or None
    date_of_birth = (data.get('date_of_birth') or '').strip() or None

    criteria = SearchCriteria(
        first_name=first_name,
        last_name=last_name,
        middle_name=middle_name,
        date_of_birth=date_of_birth,
        county=None,  # Search all jurisdictions
    )

    job_id = str(uuid.uuid4())
    jobs[job_id] = {
        'status': 'running',
        'message': 'Starting search...',
        'result': None,
        'error': None,
    }

    thread = threading.Thread(target=run_search, args=(job_id, criteria), daemon=True)
    thread.start()

    return jsonify({'job_id': job_id}), 202


@app.route('/api/status/<job_id>', methods=['GET'])
def get_status(job_id):
    job = jobs.get(job_id)
    if not job:
        return jsonify({'error': 'Job not found'}), 404

    return jsonify({
        'status': job['status'],
        'message': job['message'],
    })


@app.route('/api/results/<job_id>', methods=['GET'])
def get_results(job_id):
    job = jobs.get(job_id)
    if not job:
        return jsonify({'error': 'Job not found'}), 404

    if job['status'] != 'complete':
        return jsonify({'error': 'Results not ready', 'status': job['status']}), 400

    return jsonify(job['result'])


# Serve React frontend (production)
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    if path and os.path.exists(os.path.join(DIST_DIR, path)):
        return send_from_directory(DIST_DIR, path)
    return send_from_directory(DIST_DIR, 'index.html')


if __name__ == '__main__':
    # Auto-build frontend if dist/ doesn't exist or is empty
    if not os.path.exists(DIST_DIR) or not os.listdir(DIST_DIR):
        import subprocess
        project_root = os.path.join(os.path.dirname(__file__), '..')
        print('Building frontend...')
        subprocess.run(['npm', 'run', 'build'], cwd=project_root, check=True)
        print('Frontend built.')

    port = int(os.environ.get('PORT', 5001))
    debug = os.environ.get('FLASK_ENV') != 'production'
    app.run(host='0.0.0.0', port=port, debug=debug)
