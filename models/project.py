from datetime import datetime
from utils.database import execute_query
import json

class Project:
    def __init__(self, id, user_id, project_name, project_type, country, region,
                 description, area_hectares, boundary_coordinates, 
                 estimated_agb=None, estimated_carbon=None, estimated_co2=None,
                 status='draft', created_at=None, updated_at=None):
        self.id = id
        self.user_id = str(user_id) if user_id else None
        self.project_name = project_name
        self.project_type = project_type
        self.country = country
        self.region = region
        self.description = description
        self.area_hectares = area_hectares
        self.boundary_coordinates = boundary_coordinates
        self.estimated_agb = estimated_agb
        self.estimated_carbon = estimated_carbon
        self.estimated_co2 = estimated_co2
        self.status = status
        self.created_at = created_at
        self.updated_at = updated_at

    @staticmethod
    def create(user_id, project_name, project_type, country, region, 
               description, area_hectares, boundary_coordinates,
               estimated_agb=None, estimated_carbon=None, estimated_co2=None):
        """Create a new project - let database generate SERIAL ID"""
        
        print(f"🔄 Creating project for user_id: {user_id}")
        
        # Keep user_id as string
        user_id_str = str(user_id) if user_id else None
        
        # Convert boundary coordinates to JSON string if it's a list/dict
        if isinstance(boundary_coordinates, (list, dict)):
            boundary_coordinates = json.dumps(boundary_coordinates)
        
        # ✅ FIX: Remove ID from INSERT - let database generate SERIAL ID automatically
        query = """
            INSERT INTO projects (
                user_id, project_name, project_type, country, region,
                description, area_hectares, boundary_coordinates,
                estimated_agb, estimated_carbon, estimated_co2, status
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id, user_id, project_name, project_type, country, region,
                      description, area_hectares, boundary_coordinates,
                      estimated_agb, estimated_carbon, estimated_co2, status,
                      created_at, updated_at
        """
        
        params = (
            user_id_str, project_name, project_type, country, region,
            description, area_hectares, boundary_coordinates,
            estimated_agb, estimated_carbon, estimated_co2, 'draft'
        )
        
        print(f"📝 Executing query with {len(params)} parameters")
        print(f"📝 Project Name: {project_name}")
        print(f"📝 User ID: {user_id_str}")
        
        result = execute_query(query, params, fetch_one=True)
        
        if result:
            print(f"✅ Project created successfully with ID: {result['id']}")
            return Project(**result)
        
        print("❌ Project creation failed - no result returned")
        return None

    @staticmethod
    def get_by_id(project_id):
        """Get a project by ID"""
        query = """
            SELECT id, user_id, project_name, project_type, country, region,
                   description, area_hectares, boundary_coordinates,
                   estimated_agb, estimated_carbon, estimated_co2, status,
                   created_at, updated_at
            FROM projects
            WHERE id = %s
        """
        
        result = execute_query(query, (project_id,), fetch_one=True)
        
        if result:
            return Project(**result)
        return None

    @staticmethod
    def get_by_user(user_id):
        """Get all projects for a user"""
        
        user_id_str = str(user_id) if user_id else None
        
        query = """
            SELECT id, user_id, project_name, project_type, country, region,
                   description, area_hectares, boundary_coordinates,
                   estimated_agb, estimated_carbon, estimated_co2, status,
                   created_at, updated_at
            FROM projects
            WHERE user_id = %s
            ORDER BY created_at DESC
        """
        
        results = execute_query(query, (user_id_str,), fetch_all=True)
        
        if results:
            return [Project(**row) for row in results]
        return []

    @staticmethod
    def get_user_stats(user_id):
        """Get project statistics for a user"""
        
        user_id_str = str(user_id) if user_id else None
        
        query = """
            SELECT 
                COUNT(*) as total_projects,
                COUNT(CASE WHEN status = 'completed' THEN 1 END) as completed_projects,
                COUNT(CASE WHEN status = 'in_progress' THEN 1 END) as in_progress_projects,
                COALESCE(SUM(area_hectares), 0) as total_area,
                COALESCE(SUM(estimated_agb), 0) as total_agb,
                COALESCE(SUM(estimated_carbon), 0) as total_carbon,
                COALESCE(SUM(estimated_co2), 0) as total_co2
            FROM projects
            WHERE user_id = %s
        """
        
        result = execute_query(query, (user_id_str,), fetch_one=True)
        
        if result:
            return result
        
        return {
            'total_projects': 0,
            'completed_projects': 0,
            'in_progress_projects': 0,
            'total_area': 0,
            'total_agb': 0,
            'total_carbon': 0,
            'total_co2': 0
        }

    def update_estimates(self, agb, carbon, co2):
        """Update AGB estimates for the project"""
        query = """
            UPDATE projects 
            SET estimated_agb = %s, 
                estimated_carbon = %s, 
                estimated_co2 = %s,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = %s
        """
        
        execute_query(query, (agb, carbon, co2, self.id))
        self.estimated_agb = agb
        self.estimated_carbon = carbon
        self.estimated_co2 = co2

    def update_status(self, status):
        """Update project status"""
        query = """
            UPDATE projects 
            SET status = %s, updated_at = CURRENT_TIMESTAMP
            WHERE id = %s
        """
        
        execute_query(query, (status, self.id))
        self.status = status

    def delete(self):
        """Delete the project"""
        query = "DELETE FROM projects WHERE id = %s"
        execute_query(query, (self.id,))

    def to_dict(self):
        """Convert project to dictionary"""
        return {
            'id': self.id,
            'user_id': str(self.user_id) if self.user_id else None,
            'project_name': self.project_name,
            'project_type': self.project_type,
            'country': self.country,
            'region': self.region,
            'description': self.description,
            'area_hectares': float(self.area_hectares) if self.area_hectares else 0,
            'boundary_coordinates': json.loads(self.boundary_coordinates) if isinstance(self.boundary_coordinates, str) else self.boundary_coordinates,
            'estimated_agb': float(self.estimated_agb) if self.estimated_agb else 0,
            'estimated_carbon': float(self.estimated_carbon) if self.estimated_carbon else 0,
            'estimated_co2': float(self.estimated_co2) if self.estimated_co2 else 0,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }