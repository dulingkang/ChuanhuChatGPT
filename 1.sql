-- CREATE DATABASE resume;
-- use resume;
CREATE TABLE `resume_detail` (
  `id` bigint not null AUTO_INCREMENT,
  `name` varchar(25) not null,
  `phone` varchar(30) not null default '',
  `mail` varchar(50) not null,
  `edu` json not null,
  `exp` json not null,
  `cert` varchar(300) default '',
  `language` varchar(200) default '',
  `tag` varchar(500) not null default '',
  `summary` text,
  `create_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_mail` (`mail`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
