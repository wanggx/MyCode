-- 创建数据库
CREATE DATABASE IF NOT EXISTS `stock` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- 使用数据库
USE `stock`;

-- 创建用户表
CREATE TABLE IF NOT EXISTS `users` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `username` VARCHAR(50) UNIQUE NOT NULL COMMENT '用户名',
    `password` VARCHAR(255) NOT NULL COMMENT '密码(MD5加密)',
    `email` VARCHAR(100) COMMENT '邮箱',
    `role` VARCHAR(20) DEFAULT 'user' COMMENT '角色: admin/user',
    `status` TINYINT DEFAULT 1 COMMENT '状态: 1-启用, 0-禁用',
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    INDEX `idx_username` (`username`),
    INDEX `idx_role` (`role`),
    INDEX `idx_status` (`status`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='用户表';

-- 插入默认admin用户 (密码: 123456 的MD5值)
INSERT INTO `users` (`username`, `password`, `email`, `role`, `status`) 
VALUES ('admin', 'e10adc3949ba59abbe56e057f20f883e', 'admin@example.com', 'admin', 1)
ON DUPLICATE KEY UPDATE `updated_at` = CURRENT_TIMESTAMP;

-- 插入测试用户
INSERT INTO `users` (`username`, `password`, `email`, `role`, `status`) VALUES
('user1', 'e10adc3949ba59abbe56e057f20f883e', 'user1@example.com', 'user', 1),
('user2', 'e10adc3949ba59abbe56e057f20f883e', 'user2@example.com', 'user', 1),
('manager', 'e10adc3949ba59abbe56e057f20f883e', 'manager@example.com', 'admin', 1)
ON DUPLICATE KEY UPDATE `updated_at` = CURRENT_TIMESTAMP;

-- 查看创建的用户
SELECT `id`, `username`, `email`, `role`, `status`, `created_at` FROM `users`; 