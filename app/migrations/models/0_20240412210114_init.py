from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS `author` (
    `uid` INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `name` VARCHAR(50) NOT NULL,
    `source` VARCHAR(50) NOT NULL,
    `lastUpdatedTime` DATETIME(6) NOT NULL
) CHARACTER SET utf8mb4;
CREATE TABLE IF NOT EXISTS `image` (
    `id` VARCHAR(50) NOT NULL  PRIMARY KEY,
    `location` VARCHAR(100) NOT NULL UNIQUE,
    `has_compressed` BOOL NOT NULL  DEFAULT 0,
    `url` VARCHAR(100) NOT NULL UNIQUE,
    `title` VARCHAR(50) NOT NULL,
    `likeCount` INT NOT NULL  DEFAULT 0,
    `viewCount` INT NOT NULL  DEFAULT 0,
    `datetime` DATETIME(6) NOT NULL  DEFAULT CURRENT_TIMESTAMP(6),
    `height` INT NOT NULL,
    `width` INT NOT NULL,
    `source` VARCHAR(50) NOT NULL,
    `author_id` INT NOT NULL,
    CONSTRAINT `fk_image_author_f83b94e7` FOREIGN KEY (`author_id`) REFERENCES `author` (`uid`) ON DELETE CASCADE
) CHARACTER SET utf8mb4;
CREATE TABLE IF NOT EXISTS `tag` (
    `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `name` VARCHAR(50) NOT NULL
) CHARACTER SET utf8mb4;
CREATE TABLE IF NOT EXISTS `user_info` (
    `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `name` VARCHAR(50) NOT NULL
) CHARACTER SET utf8mb4;
CREATE TABLE IF NOT EXISTS `aerich` (
    `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `version` VARCHAR(255) NOT NULL,
    `app` VARCHAR(100) NOT NULL,
    `content` JSON NOT NULL
) CHARACTER SET utf8mb4;
CREATE TABLE IF NOT EXISTS `image_tag` (
    `image_id` VARCHAR(50) NOT NULL,
    `tag_id` INT NOT NULL,
    FOREIGN KEY (`image_id`) REFERENCES `image` (`id`) ON DELETE CASCADE,
    FOREIGN KEY (`tag_id`) REFERENCES `tag` (`id`) ON DELETE CASCADE
) CHARACTER SET utf8mb4;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        """
