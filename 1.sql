CREATE DATABASE resume;
use resume;
CREATE TABLE `detail` (
  `id` bigint not null AUTO_INCREMENT,
  `name` varchar(20) not null,
  `phone` varchar(20) not null default '',
  `email` varchar(20) not null,
  `edu` json not null,
  `exp` json not null,
  `tag` varchar(200) not null default '',
  `summary` text,
  `create_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_email` (`email`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
