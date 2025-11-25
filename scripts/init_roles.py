"""
Initialize roles and permissions
Run this after database initialization to set up RBAC
"""
from sqlalchemy.orm import Session
from models.base import engine, SessionLocal
from models.user import Role, Permission

def init_roles():
    """Initialize default roles and permissions"""
    db = SessionLocal()
    
    try:
        print("Initializing roles and permissions...")
        
        # Define roles
        roles_data = [
            {
                "name": "admin",
                "description": "Full system access"
            },
            {
                "name": "analyst",
                "description": "Can verify claims and draft advisories"
            },
            {
                "name": "verifier",
                "description": "Can verify claims but not publish"
            },
            {
                "name": "public",
                "description": "Read-only access"
            }
        ]
        
        # Create roles
        roles = {}
        for role_data in roles_data:
            role = db.query(Role).filter(Role.name == role_data["name"]).first()
            if not role:
                role = Role(
                    name=role_data["name"],
                    description=role_data["description"]
                )
                db.add(role)
                print(f"  Created role: {role_data['name']}")
            else:
                print(f"  Role already exists: {role_data['name']}")
            roles[role_data["name"]] = role
        
        db.commit()
        
        # Define permissions for each role
        permissions_data = [
            # Admin - full access
            {"role": "admin", "resource": "items", "action": "read"},
            {"role": "admin", "resource": "items", "action": "create"},
            {"role": "admin", "resource": "items", "action": "update"},
            {"role": "admin", "resource": "items", "action": "delete"},
            {"role": "admin", "resource": "claims", "action": "read"},
            {"role": "admin", "resource": "claims", "action": "create"},
            {"role": "admin", "resource": "claims", "action": "update"},
            {"role": "admin", "resource": "claims", "action": "delete"},
            {"role": "admin", "resource": "claims", "action": "verify"},
            {"role": "admin", "resource": "advisories", "action": "read"},
            {"role": "admin", "resource": "advisories", "action": "create"},
            {"role": "admin", "resource": "advisories", "action": "update"},
            {"role": "admin", "resource": "advisories", "action": "publish"},
            {"role": "admin", "resource": "users", "action": "manage"},
            
            # Analyst - can verify and draft
            {"role": "analyst", "resource": "items", "action": "read"},
            {"role": "analyst", "resource": "claims", "action": "read"},
            {"role": "analyst", "resource": "claims", "action": "verify"},
            {"role": "analyst", "resource": "advisories", "action": "read"},
            {"role": "analyst", "resource": "advisories", "action": "create"},
            {"role": "analyst", "resource": "advisories", "action": "update"},
            {"role": "analyst", "resource": "advisories", "action": "publish"},
            
            # Verifier - can verify claims
            {"role": "verifier", "resource": "items", "action": "read"},
            {"role": "verifier", "resource": "claims", "action": "read"},
            {"role": "verifier", "resource": "claims", "action": "verify"},
            {"role": "verifier", "resource": "advisories", "action": "read"},
            
            # Public - read only
            {"role": "public", "resource": "items", "action": "read"},
            {"role": "public", "resource": "advisories", "action": "read"},
        ]
        
        # Create permissions
        for perm_data in permissions_data:
            role = roles[perm_data["role"]]
            
            existing_perm = db.query(Permission).filter(
                Permission.role_id == role.id,
                Permission.resource == perm_data["resource"],
                Permission.action == perm_data["action"]
            ).first()
            
            if not existing_perm:
                permission = Permission(
                    role_id=role.id,
                    resource=perm_data["resource"],
                    action=perm_data["action"]
                )
                db.add(permission)
        
        db.commit()
        print("\nRoles and permissions initialized successfully!")
        
        # Print summary
        print("\nRole Summary:")
        for role_name in ["admin", "analyst", "verifier", "public"]:
            role = roles[role_name]
            perms = db.query(Permission).filter(Permission.role_id == role.id).all()
            print(f"  {role_name}: {len(perms)} permissions")
        
    except Exception as e:
        print(f"Error initializing roles: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    init_roles()
