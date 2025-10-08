from flask import Blueprint, request, jsonify, render_template, session
from utils.decorators import login_required, two_factor_verified
from models.project import Project  
from datetime import datetime

agb_bp = Blueprint('agb', __name__)

@agb_bp.route('/test', methods=['GET'])
@login_required
@two_factor_verified
def test_route():
    """Test if AGB route is accessible"""
    print(" AGB test route called - authentication working")
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
        print(" Testing ML model loading...")
        from ml.services.agb_predictor import agb_predictor
        
        print(f" Model loaded: {agb_predictor.model is not None}")
        print(f" Scaler loaded: {agb_predictor.scaler is not None}")
        
        # Test prediction
        test_features = [
            822.0, 1212.0, 1510.0, 2958.0, 4034.0, 3024.5,  # S2 bands
            2804.0, 1292.0, 42.0, 36.8219, -1.2921,          # ALOS, DEM, coords
            0.32, 0.14, 0.56, 2.17                           # Vegetation indices
        ]
        
        prediction = agb_predictor.predict(test_features)
        print(f" Test prediction: {prediction} Mg/ha")
        
        return jsonify({
            'success': True,
            'message': 'ML model is working!',
            'test_prediction': prediction,
            'model_loaded': agb_predictor.model is not None,
            'scaler_loaded': agb_predictor.scaler is not None
        })
        
    except Exception as e:
        print(f" ML model error: {e}")
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
        print(" Creating new project...")
        
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
            estimated_co2=data.get('estimated_co2')
        )
        
        if project:
            print(f" Project created with ID: {project.id}")
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
        print(f" Error creating project: {e}")
        import traceback
        traceback.print_exc()
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
        print(f" Error fetching project: {e}")
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
        print(f"🧪 Testing project creation for user_id: {user_id} (type: {type(user_id)})")
        
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
        print(f"❌ Project creation test error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': f'Project creation test FAILED: {str(e)}'
        }), 500
    
@agb_bp.route('/projects', methods=['GET'])
@login_required
@two_factor_verified
def get_user_projects():
    """Get all projects for the current user"""
    try:
        user_id = session.get('user_id')
        projects = Project.get_by_user(user_id)
        
        return jsonify({
            'success': True,
            'projects': [p.to_dict() for p in projects]
        })
        
    except Exception as e:
        print(f" Error fetching projects: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

#  ==================== AGB PREDICTION ROUTES ====================

@agb_bp.route('/predict', methods=['POST'])  # ONLY ONE ROUTE DECORATOR
@login_required  
@two_factor_verified
def predict_agb():
    """API endpoint for AGB prediction"""
    print("🎯 ========== AGB PREDICTION REQUEST START ==========")
    
    try:
        # Debug: Print request details
        # print(f"📦 Request method: {request.method}")
        # print(f"📦 Content-Type: {request.content_type}")
        # print(f"📦 Headers: {dict(request.headers)}")
        # print(f"📦 Form data: {request.form}")
        # print(f"📦 JSON data: {request.get_data()}")
        
        # Check if we have JSON data
        if not request.is_json:
            print(" Request is not JSON")
            return jsonify({'success': False, 'error': 'Content-Type must be application/json'}), 400
        
        data = request.get_json()
        print(f" Received JSON data: {data}")
        
        if not data:
            print(" No JSON data received")
            return jsonify({'success': False, 'error': 'No JSON data received'}), 400
        
        # Extract coordinates
        latitude = data.get('latitude')
        longitude = data.get('longitude')
        
        print(f" Raw coordinates - lat: {latitude} (type: {type(latitude)}), lng: {longitude} (type: {type(longitude)})")
        
        if latitude is None or longitude is None:
            print(" Missing coordinates")
            return jsonify({'success': False, 'error': 'Missing latitude or longitude'}), 400
        
        # Convert to float
        try:
            latitude = float(latitude)
            longitude = float(longitude)
        except (TypeError, ValueError) as e:
            print(f" Coordinate conversion error: {e}")
            return jsonify({'success': False, 'error': f'Invalid coordinates: {latitude}, {longitude}'}), 400
        
        print(f" Processed coordinates: {latitude}, {longitude}")
        
        # Extract features (mock for now)
        features = extract_features_for_point(latitude, longitude)
        # print(f" Features extracted: {len(features)} features")
        # print(f" First few features: {features[:5]}")
        
        # Predict AGB
        print(" Loading ML model...")
        from ml.services.agb_predictor import agb_predictor
        print(f" Model loaded: {agb_predictor.model is not None}")
        
        print(" Making prediction...")
        agb_estimate = agb_predictor.predict(features)
        print(f"🌿 AGB Prediction: {agb_estimate} Mg/ha")
        
        # Calculate carbon equivalent
        carbon_stock = agb_estimate * 0.5
        co2_equivalent = carbon_stock * 3.67
        
        print(" ========== PREDICTION SUCCESSFUL ==========")
        return jsonify({
            'success': True,
            'agb_estimate': round(agb_estimate, 2),
            'carbon_stock': round(carbon_stock, 2),
            'co2_equivalent': round(co2_equivalent, 2),
            'units': 'Mg/ha'
        })
        
    except Exception as e:
        print(f" ========== PREDICTION FAILED ==========")
        print(f" Error type: {type(e).__name__}")
        print(f" Error message: {str(e)}")
        import traceback
        print(f" Traceback: {traceback.format_exc()}")
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
        
        print(f" Polygon centroid: {centroid_lat}, {centroid_lng}")
        
        # Predict at centroid
        features = extract_features_for_point(centroid_lat, centroid_lng)
        from ml.services.agb_predictor import agb_predictor
        agb_estimate = agb_predictor.predict(features)
        
        # Calculate totals based on area
        area_hectares = data.get('area_hectares', 0)
        carbon_stock = agb_estimate * 0.5
        co2_equivalent = carbon_stock * 3.67
        
        # Total carbon for entire area
        total_carbon = carbon_stock * area_hectares
        total_co2 = co2_equivalent * area_hectares
        
        print(f" Area prediction: {agb_estimate} Mg/ha over {area_hectares} ha")
        
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
        print(f" Polygon prediction failed: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400

# ==================== HELPER FUNCTIONS ====================

def extract_features_for_point(lat, lon):
    """Extract features for a point (mock version)"""
    # TODO: Implement actual GEE feature extraction
    return [
        822.0,    # B2
        1212.0,   # B3  
        1510.0,   # B4
        2958.0,   # B8
        4034.0,   # B11
        3024.5,   # B12
        2804.0,   # HH
        1292.0,   # HV
        42.0,     # elevation
        lon,      # longitude
        lat,      # latitude
        0.32,     # NDVI
        0.14,     # NBR
        0.56,     # EVI
        2.17      # SAR_ratio
    ]

@agb_bp.route('/estimate', methods=['GET'])
@login_required
@two_factor_verified
def estimate_agb_page():
    """Show AGB estimation page"""
    return render_template('agb_estimation.html')