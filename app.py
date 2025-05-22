import os
import logging
import secrets
import atexit
from datetime import timedelta, datetime
from logging.handlers import RotatingFileHandler
from flask import Flask, request, jsonify, render_template, redirect, url_for, session, send_from_directory, flash, abort
from flask_cors import CORS
from config import Config
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, login_required, login_user, logout_user, UserMixin, current_user
from db import db
from models import User, Startup
from flask_wtf.csrf import CSRFProtect, generate_csrf
from functools import wraps
from flask_migrate import Migrate

# Initialize extensions before creating app
csrf = CSRFProtect()

# Initialize Flask app
app = Flask(__name__, 
    template_folder='templates',  # Explicitly specify templates folder
    static_folder='static',       # Explicitly specify static folder
    static_url_path='/static'     # Add static URL path
)

# Basic configuration
app.config.update(
    SECRET_KEY=os.environ.get('SECRET_KEY', secrets.token_hex(32)),
    SQLALCHEMY_DATABASE_URI='mysql://root:bhanu@localhost/StartupFundingTracker',
    SQLALCHEMY_TRACK_MODIFICATIONS=False,
    SESSION_TYPE='filesystem',
    PERMANENT_SESSION_LIFETIME=timedelta(days=7),
    SESSION_COOKIE_SECURE=False,
    SESSION_COOKIE_HTTPONLY=True,
    WTF_CSRF_ENABLED=True,
    WTF_CSRF_SECRET_KEY=secrets.token_hex(32),
    WTF_CSRF_TIME_LIMIT=3600,  # 1 hour token lifetime
    WTF_CSRF_SSL_STRICT=False,
    WTF_CSRF_CHECK_DEFAULT=False  # Disable default CSRF check
)

# Initialize extensions in correct order
db.init_app(app)
migrate = Migrate(app, db)  # Add this line after db initialization
with app.app_context():
    db.create_all()  # Create tables within app context

# Move csrf init after app configuration
csrf.init_app(app)
CORS(app)

# Initialize login manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'  # Changed from login_page
login_manager.login_message = 'Please log in to access this page.'
login_manager.session_protection = 'strong'

# Add after login_manager initialization
@login_manager.user_loader
def load_user(user_id):
    user = User.query.get(int(user_id))
    logging.info(f"user_loader loaded user with id: {user_id}, found: {user is not None}")
    return user

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash('Admin access required.')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Setup logging
if not os.path.exists('logs'):
    os.mkdir('logs')

# Clean up old handlers
for handler in app.logger.handlers[:]:
    app.logger.removeHandler(handler)
    handler.close()

# Use simple FileHandler instead of RotatingFileHandler
file_handler = logging.FileHandler('logs/app.log', mode='a', encoding='utf-8')
file_handler.setFormatter(logging.Formatter(
    '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
))
file_handler.setLevel(logging.INFO)

app.logger.setLevel(logging.INFO)
app.logger.addHandler(file_handler)

# Add cleanup on exit
def cleanup_handler():
    for handler in app.logger.handlers:
        handler.close()
        app.logger.removeHandler(handler)
atexit.register(cleanup_handler)

app.logger.info('Startup Fund Initialized')

# Add template directory check
template_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
if not os.path.exists(template_dir):
    os.makedirs(template_dir)
    app.logger.info(f'Created templates directory at {template_dir}')

# Add this after your other logging setup
app.logger.info(f'Template folder is set to: {app.template_folder}')
app.logger.info(f'Templates directory exists: {os.path.exists(template_dir)}')

# Database initialization
def init_db():
    try:
        db.create_all()
        app.logger.info('Database initialized successfully')
    except Exception as e:
        app.logger.error(f'Database initialization error: {str(e)}')

# Error handlers
@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(400)
def bad_request_error(e):
    if 'CSRF' in str(e):
        app.logger.warning(f'CSRF Error: {e.description}')
        flash('Session expired. Please try again.', 'error')
        return redirect(url_for('register'))
    return render_template('errors/400.html'), 400

@app.errorhandler(500)
def internal_error(error):
    app.logger.error(f'Server Error: {error}')
    return render_template('errors/500.html'), 500

# Request handlers
@app.before_request
def before_request():
    session.permanent = True  # Make session permanent
    if not session.get('cart'):
        session['cart'] = {}
    if 'csrf_token' not in session:
        session['csrf_token'] = generate_csrf()
    if not request.path.startswith('/static'):
        app.logger.info(f'Request: {request.method} {request.path} from {request.remote_addr}')

@app.after_request
def after_request(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    return response

@app.context_processor
def inject_csrf_token():
    token = generate_csrf()
    return dict(csrf_token=token)

@app.route('/')
@app.route('/home')
def home():
    return render_template('index.html')

# ... (previous imports remain the same)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        try:
            name = request.form.get('name')
            email = request.form.get('email')
            password = request.form.get('password')

            if not all([name, email, password]):
                flash('All fields are required', 'error')
                return render_template('register.html')

            existing_user = User.query.filter_by(email=email).first()
            if existing_user:
                flash('Email already registered', 'error')
                return render_template('register.html')

            new_user = User(
                name=name,
                email=email,
                password_hash=generate_password_hash(password),
                role='Viewer',
                created_at=datetime.utcnow()
            )

            db.session.add(new_user)
            db.session.commit()
            app.logger.info(f"User registered successfully: {email}")
            
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('login'))

        except Exception as e:
            db.session.rollback()
            app.logger.error(f"Registration error: {str(e)}")
            flash('Registration failed. Please try again.', 'error')
            return render_template('register.html')

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        if not email or not password:
            flash('Please enter both email and password.', 'error')
            return redirect(url_for('login'))
        
        user = User.query.filter_by(email=email).first()
        
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            flash('Login successful!', 'success')
            next_page = request.args.get('next')
            return redirect(next_page or url_for('dashboard'))
        
        flash('Invalid email or password.', 'error')
        return redirect(url_for('login'))
        
    return render_template('login.html')

@app.route('/logout')
def logout():
    logout_user()
    session.clear()
    flash('You have been logged out.')
    return redirect(url_for('home'))  # Changed from 'index' to 'home'

@app.route('/dashboard')
@login_required
def dashboard():
    try:
        # Only show startups from the database (do not add default_startups if deleted in DB)
        db_startups = Startup.query.all()
        startups = []
        for s in db_startups:
            startups.append({
                "name": s.name,
                "industry": s.industry,
                "founded_year": s.founded_year,
                "total_funding": s.total_funding,
                "valuation": s.valuation,
                "status": s.status
            })
        # Do NOT show default startups at all
        return render_template('dashboard.html', 
                            user=current_user,
                            startups=startups)
    except Exception as e:
        app.logger.error(f"Dashboard error: {str(e)}")
        flash('Error loading dashboard', 'error')
        return redirect(url_for('home'))

investors = []

@app.route('/api/investors', methods=['GET'])
def get_investors():
    return jsonify(investors)

@app.route('/api/investors', methods=['POST'])
def add_investor():
    data = request.json
    investor = {
        'id': len(investors) + 1,
        'name': data['name'],
        'firm': data.get('firm', ''),
        'investment_stage': data['investment_stage']
    }
    investors.append(investor)
    return jsonify({"message": "Investor added"}), 201

@app.route('/api/investors/<int:id>', methods=['DELETE'])
def delete_investor(id):
    global investors
    investors = [inv for inv in investors if inv['id'] != id]
    return jsonify({"message": "Investor deleted"})

@app.route('/api/investors/search', methods=['GET'])
def search_investors():
    term = request.args.get('term', '').lower()
    filtered = [
        inv for inv in investors 
        if term in inv['name'].lower() or term in inv['firm'].lower()
    ]
    return jsonify(filtered)


@app.route('/tracker')
@login_required  # If authentication is required
def tracker():
    try:
        # Your tracker data fetching logic here
        return render_template('tracker.html')
    except Exception as e:
        app.logger.error(f"Tracker error: {str(e)}")
        flash('Error loading tracker data', 'error')
        return redirect(url_for('dashboard'))

# Add static file handler
@app.route('/static/<path:filename>')
def static_files(filename):
    return send_from_directory(app.static_folder, filename)

# API Routes
@app.route('/api/register', methods=['POST'])
def register_api():
    try:
        data = request.json
        app.logger.info(f'Registration attempt for email: {data.get("email")}')
        
        if not all(key in data for key in ['name', 'email', 'password']):
            app.logger.warning('Missing required fields in registration attempt')
            return jsonify({
                'success': False,
                'message': 'Missing required fields'
            }), 400
            
        existing_user = User.query.filter_by(email=data['email']).first()
        if existing_user:
            app.logger.warning(f'Registration attempted with existing email: {data["email"]}')
            return jsonify({
                'success': False,
                'message': 'Email already registered'
            }), 400
        
        user = User(
            name=data['name'],
            email=data['email'],
            password_hash=generate_password_hash(data['password'], method='pbkdf2:sha256'),
            role='Viewer',
            created_at=datetime.now()
        )
        
        db.session.add(user)
        db.session.commit()
        
        # Return login URL instead of dashboard
        return jsonify({
            'success': True,
            'message': 'Registration successful. Please login.',
            'redirect': url_for('login')
        }), 201
            
    except Exception as e:
        db.session.rollback()
        app.logger.error(f'Registration error: {str(e)}')
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@app.route('/api/login', methods=['POST'])
@csrf.exempt
def login_api():
    try:
        data = request.json
        if not data or 'email' not in data or 'password' not in data:
            return jsonify({'success': False, 'message': 'Missing credentials'}), 400

        user = User.query.filter_by(email=data['email']).first()
        
        if user and check_password_hash(user.password_hash, data['password']):
            login_user(user, remember=True)
            user.last_login = datetime.now()
            db.session.commit()
            
            return jsonify({
                'success': True,
                'message': 'Login successful',
                'redirect': url_for('dashboard', _external=True)
            })
        
        return jsonify({'success': False, 'message': 'Invalid email or password'}), 401
        
    except Exception as e:
        app.logger.error(f'Login error: {str(e)}')
        return jsonify({'success': False, 'message': 'Login failed'}), 500

@app.route('/api/startups', methods=['GET', 'POST'])
@login_required
def startup_api():
    if request.method == 'GET':
        try:
            search = request.args.get('search', '').lower()
            startups = []
              # Always include default startups
            default_startups = [
                {"name": "CRED", "industry": "Fintech", "founded_year": 2018, "headquarters": "Bengaluru, India", "total_funding": "₹290,00,00,000", "valuation": "₹6800,00,00,000", "status": "Active"},
                {"name": "Unacademy", "industry": "Edtech", "founded_year": 2015, "headquarters": "Bengaluru, India", "total_funding": "₹150,00,00,000", "valuation": "₹3440,00,00,000", "status": "Active"},
                {"name": "Razorpay", "industry": "Fintech", "founded_year": 2014, "headquarters": "Bengaluru, India", "total_funding": "₹260,00,00,000", "valuation": "₹7500,00,00,000", "status": "Active"},
                {"name": "Ola", "industry": "Transportation", "founded_year": 2010, "headquarters": "Bengaluru, India", "total_funding": "₹320,00,00,000", "valuation": "₹7300,00,00,000", "status": "Active"},
                {"name": "Flipkart", "industry": "E-commerce", "founded_year": 2007, "headquarters": "Bengaluru, India", "total_funding": "₹1,60,00,00,000", "valuation": "₹3,760,00,00,000", "status": "Exited"},
                {"name": "Paytm", "industry": "Fintech", "founded_year": 2010, "headquarters": "Noida, India", "total_funding": "₹250,00,00,000", "valuation": "₹5500,00,00,000", "status": "Active"},
                {"name": "Zomato", "industry": "Food Delivery", "founded_year": 2008, "headquarters": "Gurgaon, India", "total_funding": "₹296,00,00,000", "valuation": "₹5400,00,00,000", "status": "Active"},
                {"name": "Byju's", "industry": "Edtech", "founded_year": 2011, "headquarters": "Bengaluru, India", "total_funding": "₹72,00,00,000", "valuation": "₹22000,00,00,000", "status": "Active"},
                {"name": "Swiggy", "industry": "Food Delivery", "founded_year": 2014, "headquarters": "Bengaluru, India", "total_funding": "₹450,00,00,000", "valuation": "₹10700,00,00,000", "status": "Active"},
                {"name": "Nykaa", "industry": "E-commerce", "founded_year": 2012, "headquarters": "Mumbai, India", "total_funding": "₹180,00,00,000", "valuation": "₹2300,00,00,000", "status": "Active"},
                {"name": "Dream11", "industry": "Gaming", "founded_year": 2008, "headquarters": "Mumbai, India", "total_funding": "₹340,00,00,000", "valuation": "₹8000,00,00,000", "status": "Active"},
                {"name": "PhonePe", "industry": "Fintech", "founded_year": 2015, "headquarters": "Bengaluru, India", "total_funding": "₹420,00,00,000", "valuation": "₹12000,00,00,000", "status": "Active"}
            ]
            
            if search:
                # Filter default startups
                startups = [s for s in default_startups if search in s["name"].lower() or search in s["industry"].lower()]
                
                # Add database results
                db_startups = Startup.query.filter(
                    db.or_(
                        Startup.name.ilike(f'%{search}%'),
                        Startup.industry.ilike(f'%{search}%')
                    )
                ).all()
                
                startups.extend([s.to_dict() for s in db_startups])
            else:
                startups = default_startups + [s.to_dict() for s in Startup.query.all()]
            
            return jsonify(startups)
        except Exception as e:
            app.logger.error(f'Error fetching startups: {str(e)}')
            return jsonify({'error': 'Failed to fetch startups'}), 500
    
    elif request.method == 'POST':
        try:
            data = request.json
            startup = Startup(
                name=data['name'],
                industry=data.get('industry', 'N/A'),
                founded_year=data.get('founded_year', datetime.now().year),
                headquarters=data.get('headquarters', 'Unknown'),
                total_funding=data.get('total_funding', '₹1,00,00,000'),
                valuation=data.get('valuation', '₹10,00,00,000'),
                status=data.get('status', 'Active')
            )
            db.session.add(startup)
            db.session.commit()
            return jsonify({'success': True, 'message': 'Startup added successfully'})
        except Exception as e:
            db.session.rollback()
            return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/startup/update', methods=['POST'])
@login_required
def update_startup():
    try:
        data = request.json
        startup = Startup.query.filter_by(name=data['name']).first()
        
        if not startup:
            return jsonify({'error': 'Startup not found'}), 404

        startup.total_funding = data['total_funding']
        startup.valuation = data['valuation']
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Startup details updated successfully'})
    except Exception as e:
        db.session.rollback()
        app.logger.error(f'Error updating startup: {str(e)}')
        return jsonify({'error': 'Failed to update startup'}), 500

@app.route('/api/startup/delete', methods=['POST'])
@login_required
def delete_startup_api():
    try:
        data = request.json
        name = data.get('name')
        if not name:
            return jsonify({'error': 'Startup name required'}), 400

        startup = Startup.query.filter_by(name=name).first()
        if not startup:
            return jsonify({'error': 'Startup not found'}), 404

        db.session.delete(startup)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Startup deleted successfully'})
    except Exception as e:
        db.session.rollback()
        app.logger.error(f'Error deleting startup: {str(e)}')
        return jsonify({'error': 'Failed to delete startup'}), 500

@app.route('/tracker')
@login_required
def tracker_page():
    return render_template('tracker.html')

@app.route('/api/tracker', methods=['GET'])
@login_required
def api_tracker():
    # Ensure the following columns exist in your Startups table:
    # name, industry, total_funding, valuation, status
    # If your schema uses different names, update the queries below accordingly.
    def row_to_dict(row):
        mapping = row._mapping  # Correct way to extract dict-like access
        return {
            'name': mapping['name'],
            'industry': mapping['industry'],
            'total_funding': mapping['total_funding'],
            'valuation': mapping['valuation'],
            'status': mapping['status']
        }

    most_funded = [
        row_to_dict(row) for row in db.session.execute("""
            SELECT name, industry, total_funding, valuation, status
            FROM Startups
            ORDER BY CAST(REPLACE(REPLACE(REPLACE(total_funding, '₹', ''), ',', ''), '.', '') AS UNSIGNED) DESC
            LIMIT 5
        """)
    ]

    least_funded = [
        row_to_dict(row) for row in db.session.execute("""
            SELECT name, industry, total_funding, valuation, status
            FROM Startups
            ORDER BY CAST(REPLACE(REPLACE(REPLACE(total_funding, '₹', ''), ',', ''), '.', '') AS UNSIGNED) ASC
            LIMIT 5
        """)
    ]

    most_valued = [
        row_to_dict(row) for row in db.session.execute("""
            SELECT name, industry, total_funding, valuation, status
            FROM Startups
            ORDER BY CAST(REPLACE(REPLACE(REPLACE(valuation, '₹', ''), ',', ''), '.', '') AS UNSIGNED) DESC
            LIMIT 5
        """)
    ]

    industry_counts = []
    for row in db.session.execute("""
        SELECT industry, COUNT(*) AS startup_count
        FROM Startups
        GROUP BY industry
        ORDER BY startup_count DESC
    """):
        industry_counts.append({
            'industry': row._mapping['industry'],
            'startup_count': row._mapping['startup_count']
        })

    return jsonify({
        'most_funded': most_funded,
        'least_funded': least_funded,
        'most_valued': most_valued,
        'industry_counts': industry_counts
    })

@app.route('/startup/add', methods=['GET', 'POST'])
@login_required
def add_startup():
    if request.method == 'POST':
        try:
            # Check if startup with same name already exists
            existing_startup = Startup.query.filter_by(name=request.form['name']).first()
            if existing_startup:
                flash('A startup with this name already exists!', 'error')
                return render_template('add_startup.html')

            startup = Startup(
                name=request.form['name'],
                industry=request.form['industry'],
                founded_year=request.form['founded_year'],
                headquarters=request.form['headquarters'],
                total_funding=request.form['total_funding'],
                valuation=request.form['valuation'],
                status=request.form['status']
            )
            db.session.add(startup)
            db.session.commit()
            flash('Startup added successfully!', 'success')
            return redirect(url_for('dashboard'))
        except Exception as e:
            db.session.rollback()
            app.logger.error(f'Error adding startup: {str(e)}')
            flash(f'Error adding startup: {str(e)}', 'error')
            return render_template('add_startup.html')
    
    return render_template('add_startup.html')

@app.route('/startup/update/<name>', methods=['GET', 'POST'])
@login_required
def update_startup_page(name):
    startup = Startup.query.filter_by(name=name).first_or_404()
    
    if request.method == 'POST':
        try:
            startup.total_funding = request.form.get('total_funding')
            startup.valuation = request.form.get('valuation')
            db.session.commit()
            flash('Startup updated successfully!', 'success')
            return redirect(url_for('dashboard'))
        except Exception as e:
            db.session.rollback()
            flash('Error updating startup', 'error')
    
    return render_template('update.html', startup=startup)

@app.route('/investors')
@login_required
def investors_page():
    try:
        return render_template('investors.html')
    except Exception as e:
        app.logger.error(f"Investors page error: {str(e)}")
        flash('Error loading investors page', 'error')
        return redirect(url_for('dashboard'))

# Error handler for unauthorized access
@login_manager.unauthorized_handler
def unauthorized():
    return redirect(url_for('login'))  # Changed from login_page

if __name__ == '__main__':
    app.run(debug=True)