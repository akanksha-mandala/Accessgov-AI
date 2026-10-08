from typing import List, Union
from fastapi import Depends, HTTPException, status
from models.users import User, UserRole
from auth.dependencies import get_current_active_user


class RoleChecker:
    """
    Role-Based Access Control (RBAC) Dependency Class.
    Allows configuring route-level authorization checks by requiring specific user roles.
    
    Usage:
        @app.get("/admin/stats", dependencies=[Depends(RoleChecker([UserRole.ADMIN]))])
        def get_stats(): ...
    """

    def __init__(self, allowed_roles: List[Union[UserRole, str]]):
        self.allowed_roles = [
            role.value if isinstance(role, UserRole) else str(role)
            for role in allowed_roles
        ]

    def __call__(self, current_user: User = Depends(get_current_active_user)) -> User:
        user_role_str = current_user.role.value if isinstance(current_user.role, UserRole) else str(current_user.role)
        if user_role_str not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Operation not permitted. Required role(s): {', '.join(self.allowed_roles)}"
            )
        return current_user


def require_roles(*roles: Union[UserRole, str]) -> RoleChecker:
    """
    Convenience helper function creating a RoleChecker instance.
    """
    return RoleChecker(allowed_roles=list(roles))
