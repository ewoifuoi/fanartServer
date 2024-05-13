from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS `service` (
    `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `service_name` VARCHAR(30) NOT NULL,
    `function` VARCHAR(30) NOT NULL,
    `last_updated` DATETIME(6) NOT NULL  DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    `duration` INT NOT NULL  DEFAULT 0
) CHARACTER SET utf8mb4;
        ALTER TABLE `tag` ADD UNIQUE INDEX `uid_tag_name_a7b9a6` (`name`);"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `tag` DROP INDEX `idx_tag_name_a7b9a6`;
        DROP TABLE IF EXISTS `service`;"""
