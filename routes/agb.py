from flask import Blueprint, request, jsonify, render_template, session
from utils.decorators import login_required, two_factor_verified
from models.project import Project  
from datetime import datetime
import json

agb_bp = Blueprint('agb', __name__)

@agb_bp.route('/test', methods=['GET'])
@login_required
@two_factor_verified
def test_route():
    """Test if AGB route is accessible"""
    print("AGB test route called - authentication working")
    return jsonify({
        'success': True,
        'message': 'AGB route is working!',
        'user_id': session.get('user_id')
    })

@agb_bp.route('/debug-model', methods=['GET'])
@login_required
@two_factor_verified
def debug_model():
    """Test if ML model is working"""
    try:
        print("Testing ML model loading...")
        from ml.services.agb_predictor import agb_predictor
        
        print(f"Model loaded: {agb_predictor.model is not None}")
        print(f"Scaler loaded: {agb_predictor.scaler is not None}")
        print(f"Feature names: {agb_predictor.feature_names}")
        
        # Test prediction with coordinates (new method)
        test_lat = -1.2921
        test_lon = 36.8219
        
        prediction = agb_predictor.predict(test_lat, test_lon)
        print(f"Test prediction: {prediction} Mg/ha")
        
        return jsonify({
            'success': True,
            'message': 'ML model is working!',
            'test_prediction': prediction,
            'model_loaded': agb_predictor.model is not None,
            'scaler_loaded': agb_predictor.scaler is not None,
            'features_count': len(agb_predictor.feature_names) if agb_predictor.feature_names else 0
        })
        
    except Exception as e:
        print(f"ML model error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': f'ML model error: {str(e)}'
        }), 500
    
# ==================== PROJECT ROUTES ====================

@agb_bp.route('/project/register', methods=['GET'])
@login_required
@two_factor_verified
def project_registration():
    """Show project registration page"""
    return render_template('dashboard/project_registration.html')

@agb_bp.route('/project/create', methods=['POST'])
@login_required
@two_factor_verified
def create_project():
    """Create a new carbon project"""
    try:
        print("Creating new project...")
        
        data = request.get_json()
        user_id = session.get('user_id')
        
        # Validate required fields
        required_fields = ['project_name', 'project_type', 'country', 'region']
        for field in required_fields:
            if not data.get(field):
                return jsonify({
                    'success': False,
                    'error': f'Missing required field: {field}'
                }), 400
        
        # Determine initial status based on whether we have estimates
        has_estimates = data.get('estimated_agb') or data.get('estimated_carbon') or data.get('estimated_co2')
        initial_status = 'in_progress' if has_estimates else 'draft'
        
        print(f"Project creation - Has estimates: {has_estimates}, Status: {initial_status}")
        
        # Create the project
        project = Project.create(
            user_id=user_id,
            project_name=data.get('project_name'),
            project_type=data.get('project_type'),
            country=data.get('country'),
            region=data.get('region'),
            description=data.get('description', ''),
            area_hectares=data.get('area_hectares', 0),
            boundary_coordinates=data.get('boundary_coordinates', []),
            estimated_agb=data.get('estimated_agb'),
            estimated_carbon=data.get('estimated_carbon'),
            estimated_co2=data.get('estimated_co2'),
            status=initial_status
        )
        
        if project:
            print(f"Project created successfully with ID: {project.id}, Status: {project.status}")
            return jsonify({
                'success': True,
                'message': 'Project created successfully!',
                'project': project.to_dict()
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to create project'
            }), 500
            
    except Exception as e:
        print(f"Error creating project: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@agb_bp.route('/project/<int:project_id>/update-status', methods=['POST'])
@login_required
@two_factor_verified
def update_project_status(project_id):
    """Update project status"""
    try:
        data = request.get_json()
        new_status = data.get('status')
        
        # Validate status
        valid_statuses = ['draft', 'in_progress', 'completed']
        if new_status not in valid_statuses:
            return jsonify({
                'success': False,
                'error': f'Invalid status. Must be one of: {", ".join(valid_statuses)}'
            }), 400
        
        project = Project.get_by_id(project_id)
        
        if not project:
            return jsonify({
                'success': False,
                'error': 'Project not found'
            }), 404
        
        # Check if user owns this project
        if project.user_id != session.get('user_id'):
            return jsonify({
                'success': False,
                'error': 'Unauthorized'
            }), 403
        
        # Update status
        project.update_status(new_status)
        
        return jsonify({
            'success': True,
            'message': f'Project status updated to {new_status}',
            'project': project.to_dict()
        })
        
    except Exception as e:
        print(f"Error updating project status: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@agb_bp.route('/project/<int:project_id>/complete', methods=['POST'])
@login_required
@two_factor_verified
def complete_project(project_id):
    """Mark project as completed"""
    try:
        project = Project.get_by_id(project_id)
        
        if not project:
            return jsonify({
                'success': False,
                'error': 'Project not found'
            }), 404
        
        # Check if user owns this project
        if project.user_id != session.get('user_id'):
            return jsonify({
                'success': False,
                'error': 'Unauthorized'
            }), 403
        
        # Update status to completed
        project.update_status('completed')
        
        return jsonify({
            'success': True,
            'message': 'Project marked as completed!',
            'project': project.to_dict()
        })
        
    except Exception as e:
        print(f"Error completing project: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@agb_bp.route('/project/<int:project_id>', methods=['GET'])
@login_required
@two_factor_verified
def get_project(project_id):
    """Get a specific project"""
    try:
        project = Project.get_by_id(project_id)
        
        if not project:
            return jsonify({
                'success': False,
                'error': 'Project not found'
            }), 404
        
        # Check if user owns this project
        if project.user_id != session.get('user_id'):
            return jsonify({
                'success': False,
                'error': 'Unauthorized'
            }), 403
        
        return jsonify({
            'success': True,
            'project': project.to_dict()
        })
        
    except Exception as e:
        print(f"Error fetching project: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
    
@agb_bp.route('/test-project-creation', methods=['POST'])
@login_required
@two_factor_verified
def test_project_creation():
    """Test project creation with current user session"""
    try:
        user_id = session.get('user_id')
        print(f"Testing project creation for user_id: {user_id} (type: {type(user_id)})")
        
        # Test data
        test_project = Project.create(
            user_id=user_id,
            project_name=f"Test Project {datetime.now().strftime('%H:%M:%S')}",
            project_type='agroforestry',
            country='Kenya',
            region='Test Region',
            description='Test project creation',
            area_hectares=10.5,
            boundary_coordinates=[{"lat": -1.2921, "lng": 36.8219}],
            estimated_agb=25.5,
            estimated_carbon=12.75,
            estimated_co2=46.79
        )
        
        if test_project:
            return jsonify({
                'success': True,
                'message': 'Project creation test PASSED!',
                'project': test_project.to_dict()
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Project creation test FAILED - no project returned'
            }), 500
            
    except Exception as e:
        print(f"Project creation test error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': f'Project creation test FAILED: {str(e)}'
        }), 500
    
@agb_bp.route('/projects', methods=['GET'])
@login_required
@two_factor_verified
def projects_page():
    """Show projects page"""
    return render_template('dashboard/projects.html')

# Add this for the JSON API that your dashboard needs
@agb_bp.route('/api/projects', methods=['GET'])
@login_required
@two_factor_verified
def get_user_projects_api():
    """API endpoint to get projects data (for dashboard)"""
    try:
        user_id = session.get('user_id')
        print(f"DEBUG: Fetching projects for user_id: {user_id}")
        
        projects = Project.get_by_user(user_id)
        print(f"DEBUG: Found {len(projects)} projects")
        
        # Debug each project
        for i, project in enumerate(projects):
            print(f"DEBUG: Project {i}: {project.project_name}, ID: {project.id}")
        
        projects_dict = [p.to_dict() for p in projects]
        
        return jsonify({
            'success': True,
            'projects': projects_dict
        })
        
    except Exception as e:
        print(f"ERROR in get_user_projects: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# ==================== AGB PREDICTION ROUTES ====================

# @agb_bp.route('/predict', methods=['POST'])
# @login_required  
# @two_factor_verified
# def predict_agb():
#     """API endpoint for AGB prediction"""
#     print("========== AGB PREDICTION REQUEST START ==========")
    
#     try:
#         # Check if we have JSON data
#         if not request.is_json:
#             print("Request is not JSON")
#             return jsonify({'success': False, 'error': 'Content-Type must be application/json'}), 400
        
#         data = request.get_json()
#         print(f"Received JSON data: {data}")
        
#         if not data:
#             print("No JSON data received")
#             return jsonify({'success': False, 'error': 'No JSON data received'}), 400
        
#         # Extract coordinates
#         latitude = data.get('latitude')
#         longitude = data.get('longitude')
        
#         print(f"Raw coordinates - lat: {latitude} (type: {type(latitude)}), lng: {longitude} (type: {type(longitude)})")
        
#         if latitude is None or longitude is None:
#             print("Missing coordinates")
#             return jsonify({'success': False, 'error': 'Missing latitude or longitude'}), 400
        
#         # Convert to float
#         try:
#             latitude = float(latitude)
#             longitude = float(longitude)
#         except (TypeError, ValueError) as e:
#             print(f"Coordinate conversion error: {e}")
#             return jsonify({'success': False, 'error': f'Invalid coordinates: {latitude}, {longitude}'}), 400
        
#         print(f"Processed coordinates: {latitude}, {longitude}")
        
#         # Predict AGB using new predictor that handles feature extraction
#         print("Loading ML model...")
#         from ml.services.agb_predictor import agb_predictor
#         print(f"Model loaded: {agb_predictor.model is not None}")
        
#         print("Making prediction with coordinate-based method...")
#         agb_estimate = agb_predictor.predict(latitude, longitude)
#         print(f"AGB Prediction: {agb_estimate} Mg/ha")
        
#         # Calculate carbon equivalent (using IPCC standard conversion)
#         carbon_stock = agb_estimate * 0.47  # 47% carbon content
#         co2_equivalent = carbon_stock * 3.67  # CO2 to carbon ratio
        
#         print("========== PREDICTION SUCCESSFUL ==========")
#         return jsonify({
#             'success': True,
#             'agb_estimate': round(agb_estimate, 2),
#             'carbon_stock': round(carbon_stock, 2),
#             'co2_equivalent': round(co2_equivalent, 2),
#             'coordinates': {
#                 'latitude': latitude,
#                 'longitude': longitude
#             },
#             'units': 'Mg/ha'
#         })
        
#     except Exception as e:
#         print(f"========== PREDICTION FAILED ==========")
#         print(f"Error type: {type(e).__name__}")
#         print(f"Error message: {str(e)}")
#         import traceback
#         print(f"Traceback: {traceback.format_exc()}")
#         return jsonify({
#             'success': False,
#             'error': str(e)
#         }), 400
# routes/agb.py - Updated predict route

@agb_bp.route('/predict', methods=['POST'])
@login_required  
@two_factor_verified
def predict_agb():
    """API endpoint for AGB prediction using ACTUAL model"""
    print("========== AGB PREDICTION WITH ACTUAL MODEL ==========")
    
    try:
        data = request.get_json()
        latitude = data.get('latitude')
        longitude = data.get('longitude')
        country = data.get('country', 'kenya')  # Get country from frontend
        
        print(f"Coordinates: {latitude}, {longitude}, Country: {country}")
        
        # Predict AGB using your ACTUAL model with country context
        from ml.services.agb_predictor import agb_predictor
        agb_estimate = agb_predictor.predict(latitude, longitude, country)
        
        # Calculate carbon equivalent (using IPCC standard conversion)
        carbon_stock = agb_estimate * 0.47  # 47% carbon content
        co2_equivalent = carbon_stock * 3.67  # CO2 to carbon ratio
        
        print("========== PREDICTION SUCCESSFUL ==========")
        return jsonify({
            'success': True,
            'agb_estimate': round(agb_estimate, 2),
            'carbon_stock': round(carbon_stock, 2),
            'co2_equivalent': round(co2_equivalent, 2),
            'country': country,
            'coordinates': {
                'latitude': latitude,
                'longitude': longitude
            },
            'units': 'Mg/ha'
        })
        
    except Exception as e:
        print(f"========== PREDICTION FAILED ==========")
        print(f"Error: {str(e)}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400

@agb_bp.route('/predict-polygon', methods=['POST'])
@login_required
@two_factor_verified
def predict_polygon():
    """Predict AGB for a polygon area"""
    try:
        data = request.get_json()
        coordinates = data.get('coordinates', [])
        
        if not coordinates or len(coordinates) < 3:
            return jsonify({
                'success': False,
                'error': 'Need at least 3 coordinates for a polygon'
            }), 400
        
        # Calculate centroid
        lat_sum = sum(coord['lat'] for coord in coordinates)
        lng_sum = sum(coord['lng'] for coord in coordinates)
        centroid_lat = lat_sum / len(coordinates)
        centroid_lng = lng_sum / len(coordinates)
        
        print(f"Polygon centroid: {centroid_lat}, {centroid_lng}")
        
        # Predict at centroid using new coordinate-based method
        from ml.services.agb_predictor import agb_predictor
        agb_estimate = agb_predictor.predict(centroid_lat, centroid_lng)
        
        # Calculate totals based on area
        area_hectares = data.get('area_hectares', 0)
        
        # Calculate carbon equivalent (using IPCC standard conversion)
        carbon_stock = agb_estimate * 0.47  # 47% carbon content
        co2_equivalent = carbon_stock * 3.67  # CO2 to carbon ratio
        
        # Total carbon for entire area
        total_carbon = carbon_stock * area_hectares
        total_co2 = co2_equivalent * area_hectares
        
        print(f"Area prediction: {agb_estimate} Mg/ha over {area_hectares} ha")
        
        return jsonify({
            'success': True,
            'agb_per_hectare': round(agb_estimate, 2),
            'carbon_per_hectare': round(carbon_stock, 2),
            'co2_per_hectare': round(co2_equivalent, 2),
            'total_carbon': round(total_carbon, 2),
            'total_co2': round(total_co2, 2),
            'area_hectares': area_hectares,
            'units': 'Mg/ha'
        })
        
    except Exception as e:
        print(f"Polygon prediction failed: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400

@agb_bp.route('/estimate', methods=['GET'])
@login_required
@two_factor_verified
def estimate_agb_page():
    """Show AGB estimation page"""
    return render_template('agb_estimation.html')

@agb_bp.route('/analytics', methods=['GET'])
@login_required
@two_factor_verified
def analytics_dashboard():
    """Show analytics dashboard"""
    return render_template('dashboard/analytics.html')

@agb_bp.route('/api/analytics/project-stats', methods=['GET'])
@login_required
@two_factor_verified
def get_project_stats():
    """API endpoint for project statistics"""
    try:
        user_id = session.get('user_id')
        projects = Project.get_by_user(user_id)
        
        # Calculate statistics
        total_projects = len(projects)
        total_area = sum(p.area_hectares or 0 for p in projects)
        total_carbon = sum((p.estimated_carbon or 0) * (p.area_hectares or 0) for p in projects)
        avg_agb = sum(p.estimated_agb or 0 for p in projects) / total_projects if total_projects > 0 else 0
        
        # Project status distribution
        status_counts = {}
        for project in projects:
            status = project.status or 'draft'
            status_counts[status] = status_counts.get(status, 0) + 1
        
        # Project type distribution
        type_counts = {}
        for project in projects:
            project_type = project.project_type or 'other'
            type_counts[project_type] = type_counts.get(project_type, 0) + 1
        
        return jsonify({
            'success': True,
            'stats': {
                'total_projects': total_projects,
                'total_area': round(total_area, 2),
                'total_carbon': round(total_carbon, 2),
                'avg_agb': round(avg_agb, 2),
                'status_distribution': status_counts,
                'type_distribution': type_counts
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
    

@agb_bp.route('/api/analytics/carbon-timeline', methods=['GET'])
@login_required
@two_factor_verified
def get_carbon_timeline():
    """API endpoint for carbon timeline data"""
    try:
        user_id = session.get('user_id')
        projects = Project.get_by_user(user_id)
        
        # Generate timeline data (mock for now - you can enhance with actual dates)
        timeline_data = []
        for i, project in enumerate(projects):
            if project.created_at:
                timeline_data.append({
                    'date': project.created_at.strftime('%Y-%m-%d'),
                    'carbon_stock': (project.estimated_carbon or 0) * (project.area_hectares or 0),
                    'project_name': project.project_name,
                    'project_type': project.project_type
                })
        
        return jsonify({
            'success': True,
            'timeline': timeline_data
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
    
@agb_bp.route('/api/reports/generate-pdf', methods=['GET'])
@login_required
@two_factor_verified
def generate_pdf_report():
    """Generate PDF report"""
    try:
        # For now, return a mock response
        # In production, you'd use libraries like ReportLab or WeasyPrint
        return jsonify({
            'success': True,
            'message': 'PDF report generation would be implemented here'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@agb_bp.route('/api/reports/generate-csv', methods=['GET'])
@login_required
@two_factor_verified
def generate_csv_report():
    """Generate CSV report"""
    try:
        user_id = session.get('user_id')
        projects = Project.get_by_user(user_id)
        
        import csv
        import io
        
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow(['Project Name', 'Type', 'Area (ha)', 'AGB (Mg/ha)', 'Carbon Stock (t C)', 'CO₂ Equivalent (t CO₂e)', 'Status'])
        
        # Write data
        for project in projects:
            writer.writerow([
                project.project_name,
                project.project_type,
                project.area_hectares or 0,
                project.estimated_agb or 0,
                project.estimated_carbon or 0,
                project.estimated_co2 or 0,
                project.status or 'draft'
            ])
        
        from flask import make_response
        response = make_response(output.getvalue())
        response.headers['Content-Disposition'] = 'attachment; filename=carbon-projects-export.csv'
        response.headers['Content-type'] = 'text/csv'
        return response
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@agb_bp.route('/api/reports/generate-json', methods=['GET'])
@login_required
@two_factor_verified
def generate_json_report():
    """Generate JSON report"""
    try:
        user_id = session.get('user_id')
        projects = Project.get_by_user(user_id)
        
        report_data = {
            'export_date': datetime.now().isoformat(),
            'total_projects': len(projects),
            'projects': [p.to_dict() for p in projects]
        }
        
        from flask import make_response
        response = make_response(json.dumps(report_data, indent=2))
        response.headers['Content-Disposition'] = 'attachment; filename=carbon-projects-export.json'
        response.headers['Content-type'] = 'application/json'
        return response
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
    