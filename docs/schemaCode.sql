USE stagelinks;

CREATE TABLE `users` (
  `id` varchar(255) PRIMARY KEY,
  `username` varchar(50) UNIQUE,
  `email` varchar(255),
  `password_hash` varchar(255),
  `account_type` varchar(255),
  `created_at` timestamp
);

CREATE TABLE `actor_profiles` (
  `user_id` varchar(255) PRIMARY KEY,
  `name` varchar(255),
  `bio` text,
  `vocal_range` varchar(255),
  `dance_experience` varchar(255),
  `city` varchar(255),
  `state` varchar(255),
  `zip_code` varchar(255),
  `profile_photo` varchar(255),
  `created_at` timestamp
);

CREATE TABLE `company_profiles` (
  `user_id` varchar(255) PRIMARY KEY,
  `name` varchar(255),
  `bio` text,
  `city` varchar(255),
  `state` varchar(255),
  `zip_code` varchar(255),
  `profile_photo` varchar(255),
  `website` varchar(255),
  `created_at` timestamp
);

CREATE TABLE `photos` (
  `id` varchar(255) PRIMARY KEY,
  `user_id` varchar(255),
  `photo_url` varchar(255),
  `caption` varchar(255),
  `uploaded_at` timestamp
);

CREATE TABLE `actor_credits` (
  `id` varchar(255) PRIMARY KEY,
  `user_id` varchar(255),
  `show_name` varchar(255),
  `theater_name` varchar(255),
  `role` varchar(255),
  `year` int
);

CREATE TABLE `prev_company_shows` (
  `id` varchar(255) PRIMARY KEY,
  `user_id` varchar(255),
  `show_name` varchar(255),
  `year` int,
  `description` text
);

CREATE TABLE `auditions` (
  `id` varchar(255) PRIMARY KEY,
  `user_id` varchar(255),
  `show_name` varchar(255),
  `description` text,
  `audition_date` date,
  `location` varchar(255),
  `contact_email` varchar(255),
  `created_at` timestamp
);

CREATE TABLE `socials` (
  `id` varchar(255) PRIMARY KEY,
  `user_id` varchar(255),
  `platform` varchar(255),
  `url` varchar(255)
);

ALTER TABLE `actor_profiles` ADD FOREIGN KEY (`user_id`) REFERENCES `users` (`id`);

ALTER TABLE `company_profiles` ADD FOREIGN KEY (`user_id`) REFERENCES `users` (`id`);

ALTER TABLE `photos` ADD FOREIGN KEY (`user_id`) REFERENCES `users` (`id`);

ALTER TABLE `actor_credits` ADD FOREIGN KEY (`user_id`) REFERENCES `users` (`id`);

ALTER TABLE `prev_company_shows` ADD FOREIGN KEY (`user_id`) REFERENCES `users` (`id`);

ALTER TABLE `auditions` ADD FOREIGN KEY (`user_id`) REFERENCES `users` (`id`);

ALTER TABLE `socials` ADD FOREIGN KEY (`user_id`) REFERENCES `users` (`id`);
