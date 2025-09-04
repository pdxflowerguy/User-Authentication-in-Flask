#!/usr/bin/env python3
"""
YouTube Automation Integration Module
Integrates the YouTube automation system with the Flask application
"""

import os
import sys
import json
import logging
import datetime
import subprocess
from pathlib import Path
from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("youtube_integration.log"),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger("youtube_integration")

# Create Blueprint
youtube_bp = Blueprint('youtube', __name__, url_prefix='/youtube')

# Configuration
YOUTUBE_AUTOMATION_DIR = Path('../youtube_automation')
CONFIG_PATH = YOUTUBE_AUTOMATION_DIR / 'config.json'
REPORTS_DIR = Path('reports')

def ensure_directories():
    """Ensure necessary directories exist"""
    REPORTS_DIR.mkdir(exist_ok=True)

@youtube_bp.route('/')
@login_required
def dashboard():
    """YouTube automation dashboard"""
    # Check if user has admin role
    if not current_user.is_admin:
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('main.dashboard'))
    
    # Get latest report
    latest_report = get_latest_report()
    
    # Get system status
    system_status = get_system_status()
    
    # Get recent videos
    recent_videos = get_recent_videos()
    
    # Get analytics summary
    analytics_summary = get_analytics_summary()
    
    return render_template(
        'youtube/dashboard.html',
        latest_report=latest_report,
        system_status=system_status,
        recent_videos=recent_videos,
        analytics_summary=analytics_summary
    )

@youtube_bp.route('/run', methods=['POST'])
@login_required
def run_automation():
    """Run the YouTube automation system"""
    # Check if user has admin role
    if not current_user.is_admin:
        return jsonify({'status': 'error', 'message': 'Permission denied'}), 403
    
    try:
        # Run the automation script
        result = subprocess.run(
            ['python', 'run_automation.py'],
            cwd=YOUTUBE_AUTOMATION_DIR,
            capture_output=True,
            text=True,
            check=True
        )
        
        logger.info(f"Automation run completed: {result.stdout}")
        
        # Get the latest report
        latest_report = get_latest_report()
        
        return jsonify({
            'status': 'success',
            'message': 'Automation run completed successfully',
            'report': latest_report
        })
    
    except subprocess.CalledProcessError as e:
        logger.error(f"Automation run failed: {e.stderr}")
        return jsonify({
            'status': 'error',
            'message': f'Automation run failed: {e.stderr}'
        }), 500
    
    except Exception as e:
        logger.error(f"Error running automation: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': f'Error running automation: {str(e)}'
        }), 500

@youtube_bp.route('/reports')
@login_required
def reports():
    """View automation reports"""
    # Check if user has admin role
    if not current_user.is_admin:
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('main.dashboard'))
    
    # Get all reports
    all_reports = get_all_reports()
    
    return render_template(
        'youtube/reports.html',
        reports=all_reports
    )

@youtube_bp.route('/reports/<report_id>')
@login_required
def view_report(report_id):
    """View a specific report"""
    # Check if user has admin role
    if not current_user.is_admin:
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('main.dashboard'))
    
    # Get the report
    report = get_report(report_id)
    
    if not report:
        flash('Report not found.', 'danger')
        return redirect(url_for('youtube.reports'))
    
    return render_template(
        'youtube/view_report.html',
        report=report
    )

@youtube_bp.route('/analytics')
@login_required
def analytics():
    """View YouTube analytics"""
    # Check if user has admin role
    if not current_user.is_admin:
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('main.dashboard'))
    
    # Get analytics data
    analytics_data = get_analytics_data()
    
    return render_template(
        'youtube/analytics.html',
        analytics=analytics_data
    )

@youtube_bp.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    """YouTube automation settings"""
    # Check if user has admin role
    if not current_user.is_admin:
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('main.dashboard'))
    
    if request.method == 'POST':
        try:
            # Update configuration
            config = {
                'youtube_api_key': request.form.get('youtube_api_key'),
                'youtube_channel_id': request.form.get('youtube_channel_id'),
                'videos_per_run': int(request.form.get('videos_per_run', 2)),
                'output_directory': request.form.get('output_directory', 'videos'),
                'templates_directory': request.form.get('templates_directory', 'templates'),
                'assets_directory': request.form.get('assets_directory', 'assets'),
                'analytics_directory': request.form.get('analytics_directory', 'analytics'),
                'publishing': {
                    'schedule': [
                        {'day': 'tuesday', 'time': '10:00'},
                        {'day': 'thursday', 'time': '15:00'},
                        {'day': 'saturday', 'time': '19:00'}
                    ],
                    'default_visibility': request.form.get('default_visibility', 'scheduled'),
                    'default_category': request.form.get('default_category', 'Entertainment')
                },
                'content_categories': {
                    'AI Tools': float(request.form.get('category_ai_tools', 0.25)),
                    'Monetization': float(request.form.get('category_monetization', 0.20)),
                    'Digital Products': float(request.form.get('category_digital_products', 0.15)),
                    'Audience Building': float(request.form.get('category_audience_building', 0.15)),
                    'Location Optimization': float(request.form.get('category_location_optimization', 0.15)),
                    'Automation Strategies': float(request.form.get('category_automation_strategies', 0.10))
                },
                'engagement': {
                    'auto_respond': request.form.get('auto_respond') == 'on',
                    'response_delay_min': int(request.form.get('response_delay_min', 1)),
                    'response_delay_max': int(request.form.get('response_delay_max', 4)),
                    'response_rate': float(request.form.get('response_rate', 0.9))
                },
                'notifications': {
                    'email': request.form.get('notification_email'),
                    'send_on_completion': request.form.get('send_on_completion') == 'on',
                    'send_on_failure': request.form.get('send_on_failure') == 'on'
                }
            }
            
            # Save configuration
            with open(CONFIG_PATH, 'w') as f:
                json.dump(config, f, indent=2)
            
            flash('Settings updated successfully.', 'success')
            return redirect(url_for('youtube.settings'))
        
        except Exception as e:
            logger.error(f"Error updating settings: {str(e)}")
            flash(f'Error updating settings: {str(e)}', 'danger')
    
    # Get current configuration
    config = get_config()
    
    return render_template(
        'youtube/settings.html',
        config=config
    )

@youtube_bp.route('/check-ffmpeg')
@login_required
def check_ffmpeg():
    """Check if FFmpeg is installed"""
    # Check if user has admin role
    if not current_user.is_admin:
        return jsonify({'status': 'error', 'message': 'Permission denied'}), 403
    
    try:
        # Check for FFmpeg
        result = subprocess.run(
            ['ffmpeg', '-version'],
            capture_output=True,
            text=True
        )
        
        return jsonify({
            'status': 'success',
            'installed': True,
            'version': result.stdout.split('\n')[0]
        })
    
    except Exception:
        return jsonify({
            'status': 'success',
            'installed': False
        })

@youtube_bp.route('/install-ffmpeg', methods=['POST'])
@login_required
def install_ffmpeg():
    """Install FFmpeg"""
    # Check if user has admin role
    if not current_user.is_admin:
        return jsonify({'status': 'error', 'message': 'Permission denied'}), 403
    
    try:
        # Install FFmpeg
        result = subprocess.run(
            ['sudo', 'apt-get', 'update'],
            capture_output=True,
            text=True,
            check=True
        )
        
        result = subprocess.run(
            ['sudo', 'apt-get', 'install', '-y', 'ffmpeg'],
            capture_output=True,
            text=True,
            check=True
        )
        
        # Check if installation was successful
        check_result = subprocess.run(
            ['ffmpeg', '-version'],
            capture_output=True,
            text=True
        )
        
        return jsonify({
            'status': 'success',
            'message': 'FFmpeg installed successfully',
            'version': check_result.stdout.split('\n')[0]
        })
    
    except subprocess.CalledProcessError as e:
        logger.error(f"FFmpeg installation failed: {e.stderr}")
        return jsonify({
            'status': 'error',
            'message': f'FFmpeg installation failed: {e.stderr}'
        }), 500
    
    except Exception as e:
        logger.error(f"Error installing FFmpeg: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': f'Error installing FFmpeg: {str(e)}'
        }), 500

# Helper functions

def get_config():
    """Get the current configuration"""
    try:
        with open(CONFIG_PATH, 'r') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error loading configuration: {str(e)}")
        return {}

def get_latest_report():
    """Get the latest automation report"""
    try:
        # Find the latest output directory
        output_dir = Path(get_config().get('output_directory', 'videos'))
        if not output_dir.exists():
            return None
        
        # Get all timestamped directories
        dirs = [d for d in output_dir.iterdir() if d.is_dir() and d.name[0].isdigit()]
        if not dirs:
            return None
        
        # Sort by name (timestamp) and get the latest
        latest_dir = sorted(dirs)[-1]
        
        # Check for report file
        report_file = latest_dir / "daily_report.md"
        if not report_file.exists():
            return None
        
        # Read the report
        with open(report_file, 'r') as f:
            report_content = f.read()
        
        return {
            'id': latest_dir.name,
            'date': datetime.datetime.strptime(latest_dir.name.split('_')[0], '%Y%m%d').strftime('%B %d, %Y'),
            'content': report_content
        }
    
    except Exception as e:
        logger.error(f"Error getting latest report: {str(e)}")
        return None

def get_all_reports():
    """Get all automation reports"""
    try:
        # Find all output directories
        output_dir = Path(get_config().get('output_directory', 'videos'))
        if not output_dir.exists():
            return []
        
        # Get all timestamped directories
        dirs = [d for d in output_dir.iterdir() if d.is_dir() and d.name[0].isdigit()]
        if not dirs:
            return []
        
        # Sort by name (timestamp) in descending order
        sorted_dirs = sorted(dirs, reverse=True)
        
        reports = []
        for dir_path in sorted_dirs:
            # Check for report file
            report_file = dir_path / "daily_report.md"
            if not report_file.exists():
                continue
            
            # Read the report
            with open(report_file, 'r') as f:
                report_content = f.read()
            
            # Extract status from report
            status = "Completed"
            if "FAILED" in report_content:
                status = "Failed"
            elif "with issues" in report_content:
                status = "Completed with issues"
            
            reports.append({
                'id': dir_path.name,
                'date': datetime.datetime.strptime(dir_path.name.split('_')[0], '%Y%m%d').strftime('%B %d, %Y'),
                'time': dir_path.name.split('_')[1],
                'status': status,
                'content': report_content
            })
        
        return reports
    
    except Exception as e:
        logger.error(f"Error getting all reports: {str(e)}")
        return []

def get_report(report_id):
    """Get a specific report by ID"""
    try:
        # Find the report directory
        output_dir = Path(get_config().get('output_directory', 'videos'))
        report_dir = output_dir / report_id
        
        if not report_dir.exists():
            return None
        
        # Check for report file
        report_file = report_dir / "daily_report.md"
        if not report_file.exists():
            return None
        
        # Read the report
        with open(report_file, 'r') as f:
            report_content = f.read()
        
        # Get video data
        videos_file = report_dir / "videos.json"
        videos_data = []
        if videos_file.exists():
            with open(videos_file, 'r') as f:
                videos_data = json.load(f)
        
        # Get analytics data
        analytics_file = report_dir / "analytics.json"
        analytics_data = {}
        if analytics_file.exists():
            with open(analytics_file, 'r') as f:
                analytics_data = json.load(f)
        
        # Get engagement data
        engagement_file = report_dir / "engagement.json"
        engagement_data = {}
        if engagement_file.exists():
            with open(engagement_file, 'r') as f:
                engagement_data = json.load(f)
        
        return {
            'id': report_id,
            'date': datetime.datetime.strptime(report_id.split('_')[0], '%Y%m%d').strftime('%B %d, %Y'),
            'time': report_id.split('_')[1],
            'content': report_content,
            'videos': videos_data,
            'analytics': analytics_data,
            'engagement': engagement_data
        }
    
    except Exception as e:
        logger.error(f"Error getting report {report_id}: {str(e)}")
        return None

def get_system_status():
    """Get the current system status"""
    try:
        # Check for FFmpeg
        ffmpeg_installed = False
        try:
            subprocess.run(['ffmpeg', '-version'], capture_output=True, check=True)
            ffmpeg_installed = True
        except:
            pass
        
        # Check for config file
        config_exists = CONFIG_PATH.exists()
        
        # Check for recent runs
        latest_report = get_latest_report()
        recent_run = latest_report is not None and datetime.datetime.strptime(
            latest_report['date'], '%B %d, %Y'
        ) > datetime.datetime.now() - datetime.timedelta(days=2)
        
        # Determine overall status
        if ffmpeg_installed and config_exists and recent_run:
            status = "Operational"
        elif not ffmpeg_installed:
            status = "FFmpeg Missing"
        elif not config_exists:
            status = "Configuration Missing"
        elif not recent_run:
            status = "No Recent Runs"
        else:
            status = "Unknown Issue"
        
        return {
            'status': status,
            'ffmpeg_installed': ffmpeg_installed,
            'config_exists': config_exists,
            'recent_run': recent_run,
            'last_run': latest_report['date'] if latest_report else "Never"
        }
    
    except Exception as e:
        logger.error(f"Error getting system status: {str(e)}")
        return {
            'status': "Error",
            'ffmpeg_installed': False,
            'config_exists': False,
            'recent_run': False,
            'last_run': "Never"
        }

def get_recent_videos():
    """Get recent videos"""
    try:
        # Get the latest report
        latest_report = get_latest_report()
        if not latest_report:
            return []
        
        # Find the report directory
        output_dir = Path(get_config().get('output_directory', 'videos'))
        report_dir = output_dir / latest_report['id']
        
        # Check for videos file
        videos_file = report_dir / "videos.json"
        if not videos_file.exists():
            return []
        
        # Read the videos data
        with open(videos_file, 'r') as f:
            videos_data = json.load(f)
        
        # Extract video information
        videos = []
        for video in videos_data.get('videos', []):
            videos.append({
                'title': video.get('title', 'Untitled'),
                'status': video.get('status', 'unknown'),
                'category': video.get('category', 'Unknown'),
                'format': video.get('format', 'Unknown'),
                'thumbnail': video.get('thumbnail_path', ''),
                'output': video.get('output_path', '')
            })
        
        return videos
    
    except Exception as e:
        logger.error(f"Error getting recent videos: {str(e)}")
        return []

def get_analytics_summary():
    """Get analytics summary"""
    try:
        # Get analytics directory
        analytics_dir = Path(get_config().get('analytics_directory', 'analytics'))
        if not analytics_dir.exists():
            return {}
        
        # Find the latest category performance file
        category_files = list(analytics_dir.glob('category_performance_*.json'))
        if not category_files:
            return {}
        
        latest_file = sorted(category_files)[-1]
        
        # Read the category performance data
        with open(latest_file, 'r') as f:
            category_data = json.load(f)
        
        # Extract category performance
        categories = []
        for category, data in category_data.items():
            categories.append({
                'name': category,
                'average_views': data.get('average_views', 0),
                'videos_count': data.get('videos_count', 0),
                'trend': data.get('trend', 'stable')
            })
        
        # Sort by average views
        categories.sort(key=lambda x: x['average_views'], reverse=True)
        
        return {
            'categories': categories,
            'date': datetime.datetime.strptime(latest_file.stem.split('_')[-1], '%Y%m%d').strftime('%B %d, %Y')
        }
    
    except Exception as e:
        logger.error(f"Error getting analytics summary: {str(e)}")
        return {}

def get_analytics_data():
    """Get detailed analytics data"""
    try:
        # Get analytics directory
        analytics_dir = Path(get_config().get('analytics_directory', 'analytics'))
        if not analytics_dir.exists():
            return {}
        
        # Find the latest analytics files
        channel_files = list(analytics_dir.glob('channel_stats_*.json'))
        audience_files = list(analytics_dir.glob('audience_stats_*.json'))
        video_files = list(analytics_dir.glob('video_stats_*.csv'))
        category_files = list(analytics_dir.glob('category_performance_*.json'))
        
        if not channel_files or not audience_files:
            return {}
        
        # Get the latest files
        latest_channel = sorted(channel_files)[-1]
        latest_audience = sorted(audience_files)[-1]
        latest_video = sorted(video_files)[-1] if video_files else None
        latest_category = sorted(category_files)[-1] if category_files else None
        
        # Read the data
        with open(latest_channel, 'r') as f:
            channel_data = json.load(f)
        
        with open(latest_audience, 'r') as f:
            audience_data = json.load(f)
        
        video_data = []
        if latest_video:
            with open(latest_video, 'r') as f:
                import csv
                reader = csv.DictReader(f)
                video_data = list(reader)
        
        category_data = {}
        if latest_category:
            with open(latest_category, 'r') as f:
                category_data = json.load(f)
        
        return {
            'channel': channel_data,
            'audience': audience_data,
            'videos': video_data,
            'categories': category_data,
            'date': datetime.datetime.strptime(latest_channel.stem.split('_')[-1], '%Y%m%d').strftime('%B %d, %Y')
        }
    
    except Exception as e:
        logger.error(f"Error getting analytics data: {str(e)}")
        return {}

# Initialize
ensure_directories()