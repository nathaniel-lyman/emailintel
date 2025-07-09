"""
Main Flask application for Retail Price Cut Summary App.
Web interface for displaying summaries and managing settings.
"""

from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_wtf import FlaskForm
from flask_wtf.csrf import CSRFProtect
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Length
import sqlite3
import logging
from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
import atexit
import os
import threading
import time

from config import Config, SettingsManager
from scraper import NewsScraper
from summarizer import Summarizer
from emailer import DailyDigest
from init_db import init_database, check_database_health

# Configure logging
logging.basicConfig(
    level=getattr(logging, Config.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = Config.SECRET_KEY
app.config['WTF_CSRF_TIME_LIMIT'] = 3600  # 1 hour

# Initialize CSRF protection
csrf = CSRFProtect(app)

# Global variables for background scheduler
scheduler = None
scheduler_lock = threading.Lock()


class SettingsForm(FlaskForm):
    """Form for updating search settings."""
    keywords = TextAreaField(
        'Keywords',
        validators=[DataRequired(), Length(min=1, max=500)],
        render_kw={'placeholder': 'Enter keywords separated by commas (e.g., retail price cut, markdown, rollback)'}
    )
    domains = TextAreaField(
        'Domains (Optional)',
        validators=[Length(max=500)],
        render_kw={'placeholder': 'Enter domains separated by commas (e.g., walmart.com, target.com)'}
    )
    submit = SubmitField('Update Settings')


def get_db_connection():
    """Get database connection."""
    conn = sqlite3.connect(Config.DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_app():
    """Initialize application components."""
    # Ensure database exists
    if not os.path.exists(Config.DATABASE_PATH):
        logger.info("Database not found, initializing...")
        init_database()
    
    # Check database health
    if not check_database_health():
        logger.error("Database health check failed")
        return False
    
    # Ensure default settings exist
    settings_manager = SettingsManager()
    settings_manager.ensure_defaults_exist()
    
    # Initialize scheduler
    init_scheduler()
    
    logger.info("Application initialized successfully")
    return True


def init_scheduler():
    """Initialize background scheduler."""
    global scheduler
    
    with scheduler_lock:
        if scheduler is not None:
            return
        
        scheduler = BackgroundScheduler()
        
        # Schedule daily digest at configured time
        scheduler.add_job(
            func=run_daily_digest,
            trigger=CronTrigger(
                hour=Config.DAILY_DIGEST_HOUR,
                minute=Config.DAILY_DIGEST_MINUTE,
                timezone=Config.SCHEDULER_TIMEZONE
            ),
            id='daily_digest',
            name='Daily Digest Email',
            replace_existing=True
        )
        
        # Schedule periodic scraping every 2 hours
        scheduler.add_job(
            func=run_scraping_and_summarization,
            trigger=CronTrigger(
                minute=0,
                hour='*/2',  # Every 2 hours
                timezone=Config.SCHEDULER_TIMEZONE
            ),
            id='periodic_scraping',
            name='Periodic News Scraping',
            replace_existing=True
        )
        
        scheduler.start()
        logger.info("Background scheduler started")


def run_daily_digest():
    """Run daily digest job with enhanced monitoring."""
    job_id = "daily_digest"
    logger.info(f"Starting {job_id} job")
    
    # Log job start
    log_job_execution(job_id, "started", "Daily digest job initiated")
    
    try:
        digest = DailyDigest()
        success = digest.send_daily_digest()
        
        if success:
            logger.info("Daily digest sent successfully")
            log_job_execution(job_id, "completed", "Daily digest sent successfully")
        else:
            logger.error("Daily digest failed")
            log_job_execution(job_id, "failed", "Daily digest failed to send")
            
    except Exception as e:
        error_msg = f"Daily digest job failed: {e}"
        logger.error(error_msg)
        log_job_execution(job_id, "error", error_msg)


def run_scraping_and_summarization():
    """Run scraping and summarization job with enhanced monitoring."""
    job_id = "scraping_summarization"
    logger.info(f"Starting {job_id} job")
    
    # Log job start
    log_job_execution(job_id, "started", "Scraping and summarization job initiated")
    
    try:
        # Scrape news
        scraper = NewsScraper()
        articles = scraper.scrape_news(hours_back=3)  # 3 hours overlap
        logger.info(f"Scraped {len(articles)} articles")
        
        # Summarize new headlines
        summarizer = Summarizer()
        summarized_count = summarizer.summarize_new_headlines()
        logger.info(f"Summarized {summarized_count} headlines")
        
        # Log successful completion
        message = f"Scraped {len(articles)} articles, summarized {summarized_count} headlines"
        log_job_execution(job_id, "completed", message)
        
    except Exception as e:
        error_msg = f"Scraping and summarization job failed: {e}"
        logger.error(error_msg)
        log_job_execution(job_id, "error", error_msg)


def log_job_execution(job_id: str, status: str, message: str):
    """Log job execution for monitoring."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO processing_log (operation_type, status, message, created_at)
            VALUES (?, ?, ?, datetime('now'))
        """, (job_id, status, message))
        
        conn.commit()
        conn.close()
        
    except Exception as e:
        logger.error(f"Failed to log job execution: {e}")


@app.route('/')
def index():
    """Dashboard showing recent summaries."""
    try:
        # Get recent summaries
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get summaries from past 7 days
        cursor.execute("""
            SELECT s.id, s.summary_text, s.topic, s.created_at,
                   h.title, h.link, h.source, h.published_date
            FROM summaries s
            JOIN headlines h ON s.headline_id = h.id
            WHERE s.created_at >= datetime('now', '-7 days')
            ORDER BY h.published_date DESC
            LIMIT 25
        """)
        
        summaries = []
        for row in cursor.fetchall():
            summaries.append({
                'id': row['id'],
                'summary': row['summary_text'],
                'topic': row['topic'] or 'General Retail',
                'title': row['title'],
                'link': row['link'],
                'source': row['source'],
                'published_date': row['published_date'],
                'created_at': row['created_at']
            })
        
        # Get current settings
        settings_manager = SettingsManager()
        settings = settings_manager.load_settings()
        
        # Get processing stats with proper keys for template
        stats = {}
        
        # Total summaries count
        cursor.execute("SELECT COUNT(*) as count FROM summaries")
        stats['total_summaries'] = cursor.fetchone()['count']
        
        # Get processing stats from last 24 hours
        cursor.execute("""
            SELECT operation_type, COUNT(*) as count
            FROM processing_log
            WHERE created_at >= datetime('now', '-24 hours')
            GROUP BY operation_type
        """)
        
        processing_stats = {row['operation_type']: row['count'] for row in cursor.fetchall()}
        
        # Map processing_log operation types to template expected keys
        stats['scrape'] = processing_stats.get('scraping_summarization', 0)
        stats['summarize'] = processing_stats.get('scraping_summarization', 0)
        stats['email'] = processing_stats.get('daily_digest', 0)
        
        conn.close()
        
        return render_template('index.html',
                             summaries=summaries,
                             settings=settings,
                             stats=stats)
        
    except Exception as e:
        logger.error(f"Error in index route: {e}")
        flash('Error loading dashboard', 'error')
        # Provide default settings structure
        default_settings = {
            'keywords': 'retail price cut,markdown,rollback,discount,price drop',
            'domains': 'walmart.com,target.com,amazon.com,costco.com,kroger.com',
            'updated_at': None
        }
        return render_template('index.html', summaries=[], settings=default_settings, stats={})


@app.route('/settings', methods=['GET', 'POST'])
def settings():
    """Settings page for managing search configuration."""
    settings_manager = SettingsManager()
    form = SettingsForm()
    
    if form.validate_on_submit():
        try:
            keywords = form.keywords.data.strip()
            domains = form.domains.data.strip()
            
            # Save settings
            success = settings_manager.save_settings(keywords, domains)
            
            if success:
                flash('Settings updated successfully!', 'success')
                return redirect(url_for('settings'))
            else:
                flash('Error updating settings. Please check the format.', 'error')
                
        except Exception as e:
            logger.error(f"Error updating settings: {e}")
            flash(f'Error updating settings: {str(e)}', 'error')
    
    # Load current settings
    current_settings = settings_manager.load_settings()
    
    # Pre-populate form with current settings
    if not form.keywords.data:
        form.keywords.data = current_settings['keywords']
    if not form.domains.data:
        form.domains.data = current_settings['domains']
    
    return render_template('settings.html', form=form, settings=current_settings)


@app.route('/refresh', methods=['POST'])
def refresh():
    """Manual refresh endpoint."""
    # Check API token if configured
    if Config.API_TOKEN:
        token = request.headers.get('Authorization')
        if not token or token != f'Bearer {Config.API_TOKEN}':
            return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        # Run scraping and summarization
        scraper = NewsScraper()
        articles = scraper.scrape_news(hours_back=24)
        
        summarizer = Summarizer()
        summarized_count = summarizer.summarize_new_headlines()
        
        # For htmx requests, return success message that will be shown as flash message
        if request.headers.get('HX-Request'):
            if summarized_count > 0:
                flash(f'Refresh successful! Scraped {len(articles)} articles and created {summarized_count} summaries.', 'success')
            else:
                flash(f'Refresh completed. Scraped {len(articles)} articles, no new summaries created.', 'info')
            
            # Redirect to index to refresh the page
            return redirect(url_for('index'))
        else:
            # For API requests, return JSON
            return jsonify({
                'success': True,
                'articles_scraped': len(articles),
                'summaries_created': summarized_count,
                'timestamp': datetime.now().isoformat()
            })
        
    except Exception as e:
        logger.error(f"Manual refresh failed: {e}")
        
        if request.headers.get('HX-Request'):
            flash(f'Refresh failed: {str(e)}', 'error')
            return redirect(url_for('index'))
        else:
            return jsonify({'error': str(e)}), 500


@app.route('/health')
def health():
    """Health check endpoint."""
    try:
        # Check database
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        conn.close()
        
        # Check scheduler
        scheduler_running = scheduler is not None and scheduler.running
        
        return jsonify({
            'status': 'healthy',
            'database': 'ok',
            'scheduler': 'running' if scheduler_running else 'stopped',
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500


@app.route('/stats')
def stats():
    """Statistics endpoint."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get various statistics
        stats = {}
        
        # Total summaries
        cursor.execute("SELECT COUNT(*) as count FROM summaries")
        stats['total_summaries'] = cursor.fetchone()['count']
        
        # Summaries today
        cursor.execute("""
            SELECT COUNT(*) as count FROM summaries
            WHERE created_at >= date('now')
        """)
        stats['summaries_today'] = cursor.fetchone()['count']
        
        # Recent processing log
        cursor.execute("""
            SELECT operation_type, status, COUNT(*) as count
            FROM processing_log
            WHERE created_at >= datetime('now', '-24 hours')
            GROUP BY operation_type, status
        """)
        
        processing_stats = {}
        for row in cursor.fetchall():
            operation = row['operation_type']
            if operation not in processing_stats:
                processing_stats[operation] = {}
            processing_stats[operation][row['status']] = row['count']
        
        stats['processing_24h'] = processing_stats
        
        conn.close()
        
        return jsonify(stats)
        
    except Exception as e:
        logger.error(f"Stats endpoint failed: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/jobs')
def jobs_status():
    """Job status tracking endpoint."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get recent job executions
        cursor.execute("""
            SELECT operation_type, status, message, created_at
            FROM processing_log
            WHERE operation_type IN ('daily_digest', 'scraping_summarization')
            ORDER BY created_at DESC
            LIMIT 50
        """)
        
        jobs = []
        for row in cursor.fetchall():
            jobs.append({
                'job_id': row['operation_type'],
                'status': row['status'],
                'message': row['message'],
                'timestamp': row['created_at']
            })
        
        # Get scheduler status
        scheduler_status = {
            'running': scheduler is not None and scheduler.running,
            'jobs': []
        }
        
        if scheduler and scheduler.running:
            for job in scheduler.get_jobs():
                next_run = job.next_run_time.isoformat() if job.next_run_time else None
                scheduler_status['jobs'].append({
                    'id': job.id,
                    'name': job.name,
                    'next_run': next_run,
                    'trigger': str(job.trigger)
                })
        
        conn.close()
        
        return jsonify({
            'recent_executions': jobs,
            'scheduler': scheduler_status
        })
        
    except Exception as e:
        logger.error(f"Jobs status endpoint failed: {e}")
        return jsonify({'error': str(e)}), 500


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    logger.error(f"Internal server error: {error}")
    return render_template('500.html'), 500


@app.errorhandler(Exception)
def handle_exception(error):
    """Handle all other exceptions."""
    logger.error(f"Unhandled exception: {error}")
    return render_template('500.html'), 500


def shutdown_scheduler():
    """Shutdown scheduler on app exit."""
    global scheduler
    if scheduler is not None:
        scheduler.shutdown()
        logger.info("Scheduler shutdown")


if __name__ == '__main__':
    # Initialize app
    if not init_app():
        logger.error("Failed to initialize app")
        exit(1)
    
    # Register shutdown handler
    atexit.register(shutdown_scheduler)
    
    # Run app
    debug = Config.FLASK_DEBUG
    port = int(os.environ.get('PORT', 5000))
    
    logger.info(f"Starting Flask app on port {port}, debug={debug}")
    app.run(host='0.0.0.0', port=port, debug=debug)