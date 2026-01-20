from tortoise import BaseDBAsyncClient

RUN_IN_TRANSACTION = True


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE `route_permission_rel` (
    `frontend_routes_id` CHAR(36) NOT NULL REFERENCES `frontend_routes` (`id`) ON DELETE CASCADE,
    `permission_id` CHAR(36) NOT NULL REFERENCES `permissions` (`id`) ON DELETE CASCADE
) CHARACTER SET utf8mb4 COMMENT='路由权限关联';
        CREATE TABLE `user_role_rel` (
    `users_id` CHAR(36) NOT NULL REFERENCES `users` (`id`) ON DELETE CASCADE,
    `userrole_id` CHAR(36) NOT NULL REFERENCES `user_roles` (`id`) ON DELETE CASCADE
) CHARACTER SET utf8mb4 COMMENT='用户角色关联';
        CREATE TABLE `role_permission_rel` (
    `user_roles_id` CHAR(36) NOT NULL REFERENCES `user_roles` (`id`) ON DELETE CASCADE,
    `permission_id` CHAR(36) NOT NULL REFERENCES `permissions` (`id`) ON DELETE CASCADE
) CHARACTER SET utf8mb4 COMMENT='角色权限关联';
        CREATE TABLE `project_user_rel` (
    `project_info_id` CHAR(36) NOT NULL REFERENCES `project_info` (`id`) ON DELETE CASCADE,
    `user_id` CHAR(36) NOT NULL REFERENCES `users` (`id`) ON DELETE CASCADE
) CHARACTER SET utf8mb4 COMMENT='项目与用户关联';"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        DROP TABLE IF EXISTS `route_permission_rel`;
        DROP TABLE IF EXISTS `role_permission_rel`;
        DROP TABLE IF EXISTS `user_role_rel`;
        DROP TABLE IF EXISTS `project_user_rel`;"""


MODELS_STATE = (
    "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"
)
