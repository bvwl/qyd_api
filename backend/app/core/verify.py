from fastapi import HTTPException
from uuid import UUID


class Verify:
    def __init__(self):
        pass

    # 检测是否为管理员
    def is_admin(self, roles, raise_exception=True):
        """检测是否为管理员
        
        Args:
            roles: 角色列表或单个角色字符串
            raise_exception: 是否抛出异常，默认True
        """
        # 兼容旧版本的单个角色字符串
        if isinstance(roles, str):
            roles = [roles]

        if "ADMIN" not in roles:
            if raise_exception:
                raise HTTPException(status_code=403, detail="权限不足")
            else:
                return False
        return True

    # 检测是否操作自己的数据
    def is_owner(self, pk: UUID, user_id: UUID, raise_exception=True):
        if pk != user_id:
            if raise_exception:
                raise HTTPException(status_code=403, detail="无法操作他人数据")
            else:
                return False
        return True

    # 检测是否为GM
    def is_gm(self, roles, raise_exception=True):
        """检测是否为GM
        
        Args:
            roles: 角色列表或单个角色字符串
            raise_exception: 是否抛出异常，默认True
        """
        # 兼容旧版本的单个角色字符串
        if isinstance(roles, str):
            roles = [roles]

        if "GM" not in roles:
            if raise_exception:
                raise HTTPException(status_code=403, detail="权限不足")
            else:
                return False
        return True

    # 检测是否为GM或自己
    def is_gm_or_owner(self, roles, pk: UUID, user_id: UUID, raise_exception=True):
        """检测是否为GM或自己
        
        Args:
            roles: 角色列表或单个角色字符串
            pk: 目标资源ID
            user_id: 当前用户ID
        """
        # 兼容旧版本的单个角色字符串
        if isinstance(roles, str):
            roles = [roles]

        if "GM" not in roles and pk != user_id:
            if raise_exception:
                raise HTTPException(status_code=403, detail="权限不足")
            else:
                return False
        return True

    # 检测是否为管理员或GM
    def is_admin_or_gm(self, roles, raise_exception=True):
        """检测是否为管理员或GM

        Args:
            roles: 角色列表或单个角色字符串
            raise_exception: 是否抛出异常，默认True
        """
        # 兼容旧版本的单个角色字符串
        if isinstance(roles, str):
            roles = [roles]

        if not any(role in roles for role in ['ADMIN', 'GM']):
            if raise_exception:
                raise HTTPException(status_code=403, detail="权限不足")
            else:
                return False
        return True

    # 检测是否管理员或自己操作自己的数据
    def is_admin_or_owner(self, roles, pk: UUID, user_id: UUID, raise_exception=True):
        """检测是否管理员或自己操作自己的数据
        
        Args:
            roles: 角色列表或单个角色字符串
            raise_exception: 是否抛出异常，默认True
            pk: 目标资源ID
            user_id: 当前用户ID
        """
        # 兼容旧版本的单个角色字符串
        if isinstance(roles, str):
            roles = [roles]

        if not any(role in roles for role in ['ADMIN', 'GM']) and pk != user_id:
            if raise_exception:
                raise HTTPException(status_code=403, detail="权限不足")
            else:
                return False
        return True

    # 检测是否管理员或gm或自己操作自己的数据
    def is_admin_or_gm_or_owner(self, roles: list, _user_id: UUID, user_id: UUID, raise_exception=True):
        """检测是否管理员或质检或gm或自己操作自己的数据

        Args:
            roles: 角色列表或单个角色字符串
            _user_id: 检查目标用户ID
            user_id: 当前用户ID
            raise_exception: 是否抛出异常，默认True
        """
        # 兼容旧版本的单个角色字符串
        if isinstance(roles, str):
            roles = [roles]

        _roles = ['ADMIN', 'GM']
        if not any(role in roles for role in _roles) and _user_id != user_id:
            if raise_exception:
                raise HTTPException(status_code=403, detail="权限不足")
            else:
                return False
        return True


verify = Verify()
