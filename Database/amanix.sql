-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Mar 03, 2025 at 12:52 PM
-- Server version: 10.4.32-MariaDB
-- PHP Version: 8.2.12

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `amanix`
--

-- --------------------------------------------------------

--
-- Table structure for table `app_categories`
--

CREATE TABLE `app_categories` (
  `cat_id` int(11) NOT NULL,
  `cat_name` varchar(50) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;

--
-- Dumping data for table `app_categories`
--

INSERT INTO `app_categories` (`cat_id`, `cat_name`) VALUES
(3, 'Trending'),
(4, 'Action');

-- --------------------------------------------------------

--
-- Table structure for table `app_movies`
--

CREATE TABLE `app_movies` (
  `movie_id` int(11) NOT NULL,
  `movie_name` varchar(100) NOT NULL,
  `movie_description` longtext NOT NULL,
  `movie_director` varchar(100) NOT NULL,
  `movie_star` varchar(100) NOT NULL,
  `movie_rating` varchar(100) NOT NULL,
  `movie_duration` varchar(100) NOT NULL,
  `movie_release_date` varchar(100) NOT NULL,
  `movie_image` varchar(100) NOT NULL,
  `movie_video` varchar(100) DEFAULT NULL,
  `category_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;

--
-- Dumping data for table `app_movies`
--

INSERT INTO `app_movies` (`movie_id`, `movie_name`, `movie_description`, `movie_director`, `movie_star`, `movie_rating`, `movie_duration`, `movie_release_date`, `movie_image`, `movie_video`, `category_id`) VALUES
(1, 'Pushpa 2: The Rule', 'A smuggling kingpin faces off against a vengeful rival while manipulating politics, making big deals, and navigating tense confrontations.', 'Sukumar', 'Allu Arjun, Rashmika Mandanna, Fahadh Faasil', '6.2', '3h 21m', 'December 5, 2024', 'images/pushpa_2_QxCxwTp.jpg', 'movies/pushpa_2_LwFoIxv.mp4', 3),
(2, 'Chhaava', 'A Hindu Warrior life.', 'priyanshu', 'ram and sita', '9.2', '3h 21m', 'January 2, 2024', 'images/chaava.jpg', 'movies/pushpa_2_LwFoIxv_ef1bvmm.mp4', 3),
(3, 'Shiddat', 'A passionate love story involving two couples which highlights the...', 'Kunal Deshmukh', 'Sunny Kaushal , Radhika Madan , Mohit Raina', '7.6', '2h 26m', '2021', 'images/1710936380821-v.webp', 'movies/04_Wedding.mp4', 3),
(4, 'Vanvaas', 'Delves into the dynamics between an elderly father grappling with dementia and his family.', 'Anil Sharma', 'Amjad Ali , Anil Sharma , Sunil Sarvaiya', '6.7', '2h 40m', '2024', 'images/vanvash_GWwMWSD.jpg', 'movies/pushpa_2_LwFoIxv_8iaPdKo.mp4', 3),
(5, 'Love hurts', 'A realtor is pulled back into the life he left behind after his former partner-in-crime resurfaces with an ominous message.', 'Jonathan Eusebio', 'Ke Huy Quan , Ariana DeBose , Mustafa Shakir', '5.4', '1h 23m', '2025', 'images/love_hurts.jpg', 'movies/pushpa_2_LwFoIxv_Af1xml2.mp4', 3),
(6, 'Match Fixing', 'Match Fixing is an upcoming political thriller based on the book \"The Game Behind Saffron Terror\" by Col. Kanwar Khatana (Retd.).', 'Kedar Prabhakar Gaekwad', 'Vineet Kumar , SinghManoj , JoshiRaj Arjun', '6.6', '2h 26m', '2025', 'images/match_fixing.jpg', 'movies/pushpa_2_LwFoIxv_MHQC3uq.mp4', 3),
(7, 'Bahubali : The Beginning', 'A child from the Mahishmati kingdom is raised by tribal people and one day learns about his royal heritage, his father\'s bravery in battle and a mission to overthrow the incumbent ruler.', 'S.S. Rajamouli', 'Prabhas , Rana Daggubati , Anushka Shetty', '8.0', '2h 39m', '2015', 'images/bahubali.jpg', 'movies/pushpa_2_LwFoIxv_rtW1KV4.mp4', 4),
(8, 'RRR', 'A fearless warrior on a perilous mission comes face to face with a steely cop serving British forces in this epic saga set in pre-independent India.', 'S.S. Rajamouli', 'N.T. Rama Rao Jr. , Ram Charan ,Ajay Devgn', '7.8', '3h 7m', '2022', 'images/rrr.jpg', 'movies/pushpa_2_LwFoIxv_qVAI8LT.mp4', 4),
(10, 'K.G.F: Chapter 2', 'In the blood-soaked Kolar Gold Fields, Rocky\'s name strikes fear into his foes, while the government sees him as a threat to law and order. Rocky must battle threats from all sides for unchallenged supremacy.', 'Prashanth Neel', 'Yash , Sanjay Dutt  , Raveena Tandon', '8.2', '2h 46m', '2022', 'images/kgf.jpg', 'movies/pushpa_2_LwFoIxv_ZtNeJCn.mp4', 4),
(11, 'Jawan', 'A prison warden recruits inmates to commit outrageous crimes that shed light on corruption and injustice - and that lead him to an unexpected reunion.', 'Atlee', 'Shah Rukh Khan , Nayanthara , Vijay Sethupathi', '6.9', '2h 49m', '20234', 'images/jawan.jpg', 'movies/pushpa_2_LwFoIxv_1IlgDF7.mp4', 4),
(12, 'Avengers: Endgame', 'After the devastating events of Avengers: Infinity War (2018), the universe is in ruins. With the help of remaining allies, the Avengers assemble once more in order to reverse ..', 'Anthony Russo, Joe Russo', 'Robert Downey Jr. , Chris Evans, Mark Ruffalo', '8.4', '3h 1m', '2019', 'images/avengers_endgame.jpg', 'movies/videoplayback.mp4', 4),
(13, 'sholay', 'After his family is murdered by a notorious and ruthless bandit, a former police officer enlists the services of two outlaws to capture the bandit.', 'Ramesh Sippy', 'Sanjeev Kumar , Dharmendra , Amitabh Bachchan', '8.1', '2h 42m', '1975', 'images/sholay.jpg', 'movies/pushpa_2_LwFoIxv_j51qwxH.mp4', 4);

-- --------------------------------------------------------

--
-- Table structure for table `app_payment`
--

CREATE TABLE `app_payment` (
  `pay_id` int(11) NOT NULL,
  `pay_method` varchar(50) NOT NULL,
  `card_no` varchar(16) DEFAULT NULL,
  `expiry_date` varchar(10) DEFAULT NULL,
  `cvv_code` varchar(4) DEFAULT NULL,
  `card_holder_nm` varchar(100) DEFAULT NULL,
  `sub_price` decimal(10,2) NOT NULL,
  `start_date` date NOT NULL,
  `end_date` date NOT NULL,
  `user_id` bigint(20) NOT NULL,
  `subscription_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;

--
-- Dumping data for table `app_payment`
--

INSERT INTO `app_payment` (`pay_id`, `pay_method`, `card_no`, `expiry_date`, `cvv_code`, `card_holder_nm`, `sub_price`, `start_date`, `end_date`, `user_id`, `subscription_id`) VALUES
(1, 'Credit/Debit Card', '7587', '76/75', NULL, NULL, 1099.00, '2025-03-03', '2026-03-03', 1, 7);

-- --------------------------------------------------------

--
-- Table structure for table `app_subscription`
--

CREATE TABLE `app_subscription` (
  `sub_id` int(11) NOT NULL,
  `sub_name` varchar(100) NOT NULL,
  `sub_price` decimal(10,2) NOT NULL,
  `sub_time_limit` varchar(20) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;

--
-- Dumping data for table `app_subscription`
--

INSERT INTO `app_subscription` (`sub_id`, `sub_name`, `sub_price`, `sub_time_limit`) VALUES
(1, 'BasicPlan', 99.00, '28days'),
(2, 'Standard Plan', 549.00, '6month'),
(7, 'Premium Plan', 1099.00, '1year');

-- --------------------------------------------------------

--
-- Table structure for table `app_user`
--

CREATE TABLE `app_user` (
  `id` bigint(20) NOT NULL,
  `nm` varchar(100) NOT NULL,
  `email` varchar(200) NOT NULL,
  `password` varchar(100) NOT NULL,
  `profile_image` varchar(100) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;

--
-- Dumping data for table `app_user`
--

INSERT INTO `app_user` (`id`, `nm`, `email`, `password`, `profile_image`) VALUES
(1, 'maulik', 'maulik@gmail.com', 'pbkdf2_sha256$600000$9q5jdX86FARdG7Kx19mORo$ZCvFXNiCf5rcLXxsxCthtfBanhIyJ/MYZshakm/9QGU=', 'profile_pics/avengers_endgame.jpg'),
(2, 'priyanshu', 'priyanshu@gmail.com', 'pbkdf2_sha256$600000$SwCWC8CxIA4L2Eo75XnhNo$yAdGUcmiqQv/8kysgAvgfLU/nHzCWvylLS5EAeWwg1A=', 'profile_pics/usericon.png');

-- --------------------------------------------------------

--
-- Table structure for table `auth_group`
--

CREATE TABLE `auth_group` (
  `id` int(11) NOT NULL,
  `name` varchar(150) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;

-- --------------------------------------------------------

--
-- Table structure for table `auth_group_permissions`
--

CREATE TABLE `auth_group_permissions` (
  `id` bigint(20) NOT NULL,
  `group_id` int(11) NOT NULL,
  `permission_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;

-- --------------------------------------------------------

--
-- Table structure for table `auth_permission`
--

CREATE TABLE `auth_permission` (
  `id` int(11) NOT NULL,
  `name` varchar(255) NOT NULL,
  `content_type_id` int(11) NOT NULL,
  `codename` varchar(100) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;

--
-- Dumping data for table `auth_permission`
--

INSERT INTO `auth_permission` (`id`, `name`, `content_type_id`, `codename`) VALUES
(1, 'Can add log entry', 1, 'add_logentry'),
(2, 'Can change log entry', 1, 'change_logentry'),
(3, 'Can delete log entry', 1, 'delete_logentry'),
(4, 'Can view log entry', 1, 'view_logentry'),
(5, 'Can add permission', 2, 'add_permission'),
(6, 'Can change permission', 2, 'change_permission'),
(7, 'Can delete permission', 2, 'delete_permission'),
(8, 'Can view permission', 2, 'view_permission'),
(9, 'Can add group', 3, 'add_group'),
(10, 'Can change group', 3, 'change_group'),
(11, 'Can delete group', 3, 'delete_group'),
(12, 'Can view group', 3, 'view_group'),
(13, 'Can add user', 4, 'add_user'),
(14, 'Can change user', 4, 'change_user'),
(15, 'Can delete user', 4, 'delete_user'),
(16, 'Can view user', 4, 'view_user'),
(17, 'Can add content type', 5, 'add_contenttype'),
(18, 'Can change content type', 5, 'change_contenttype'),
(19, 'Can delete content type', 5, 'delete_contenttype'),
(20, 'Can view content type', 5, 'view_contenttype'),
(21, 'Can add session', 6, 'add_session'),
(22, 'Can change session', 6, 'change_session'),
(23, 'Can delete session', 6, 'delete_session'),
(24, 'Can view session', 6, 'view_session'),
(25, 'Can add user', 7, 'add_user'),
(26, 'Can change user', 7, 'change_user'),
(27, 'Can delete user', 7, 'delete_user'),
(28, 'Can view user', 7, 'view_user'),
(29, 'Can add subscription', 8, 'add_subscription'),
(30, 'Can change subscription', 8, 'change_subscription'),
(31, 'Can delete subscription', 8, 'delete_subscription'),
(32, 'Can view subscription', 8, 'view_subscription'),
(33, 'Can add payment', 9, 'add_payment'),
(34, 'Can change payment', 9, 'change_payment'),
(35, 'Can delete payment', 9, 'delete_payment'),
(36, 'Can view payment', 9, 'view_payment'),
(37, 'Can add categories', 10, 'add_categories'),
(38, 'Can change categories', 10, 'change_categories'),
(39, 'Can delete categories', 10, 'delete_categories'),
(40, 'Can view categories', 10, 'view_categories'),
(41, 'Can add movies', 11, 'add_movies'),
(42, 'Can change movies', 11, 'change_movies'),
(43, 'Can delete movies', 11, 'delete_movies'),
(44, 'Can view movies', 11, 'view_movies');

-- --------------------------------------------------------

--
-- Table structure for table `auth_user`
--

CREATE TABLE `auth_user` (
  `id` int(11) NOT NULL,
  `password` varchar(128) NOT NULL,
  `last_login` datetime(6) DEFAULT NULL,
  `is_superuser` tinyint(1) NOT NULL,
  `username` varchar(150) NOT NULL,
  `first_name` varchar(150) NOT NULL,
  `last_name` varchar(150) NOT NULL,
  `email` varchar(254) NOT NULL,
  `is_staff` tinyint(1) NOT NULL,
  `is_active` tinyint(1) NOT NULL,
  `date_joined` datetime(6) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;

--
-- Dumping data for table `auth_user`
--

INSERT INTO `auth_user` (`id`, `password`, `last_login`, `is_superuser`, `username`, `first_name`, `last_name`, `email`, `is_staff`, `is_active`, `date_joined`) VALUES
(1, 'pbkdf2_sha256$600000$L95JqaolOGmhaVpKQxf1y8$pJ/sq1G5zt+kUPMxsyfIxSax8bG3kI5UyA4o2W8ofpE=', '2025-03-03 11:34:54.573020', 1, 'admin@123', '', '', 'admin@gmail.com', 1, 1, '2025-02-17 13:58:44.248762');

-- --------------------------------------------------------

--
-- Table structure for table `auth_user_groups`
--

CREATE TABLE `auth_user_groups` (
  `id` bigint(20) NOT NULL,
  `user_id` int(11) NOT NULL,
  `group_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;

-- --------------------------------------------------------

--
-- Table structure for table `auth_user_user_permissions`
--

CREATE TABLE `auth_user_user_permissions` (
  `id` bigint(20) NOT NULL,
  `user_id` int(11) NOT NULL,
  `permission_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;

-- --------------------------------------------------------

--
-- Table structure for table `django_admin_log`
--

CREATE TABLE `django_admin_log` (
  `id` int(11) NOT NULL,
  `action_time` datetime(6) NOT NULL,
  `object_id` longtext DEFAULT NULL,
  `object_repr` varchar(200) NOT NULL,
  `action_flag` smallint(5) UNSIGNED NOT NULL CHECK (`action_flag` >= 0),
  `change_message` longtext NOT NULL,
  `content_type_id` int(11) DEFAULT NULL,
  `user_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;

--
-- Dumping data for table `django_admin_log`
--

INSERT INTO `django_admin_log` (`id`, `action_time`, `object_id`, `object_repr`, `action_flag`, `change_message`, `content_type_id`, `user_id`) VALUES
(1, '2025-02-17 14:27:25.000715', '1', 'Standard Plan', 2, '[{\"changed\": {\"fields\": [\"Sub price\"]}}]', 8, 1),
(2, '2025-02-17 14:32:51.449634', '4', 'abc', 1, '[{\"added\": {}}]', 8, 1),
(3, '2025-02-17 14:33:59.220840', '4', 'abc', 3, '', 8, 1),
(4, '2025-02-18 04:39:27.777867', '1', 'Horror', 1, '[{\"added\": {}}]', 10, 1),
(5, '2025-02-18 05:14:21.016878', '1', 'kaka', 1, '[{\"added\": {}}]', 11, 1),
(6, '2025-02-18 05:15:26.272956', '1', 'kaka', 2, '[{\"changed\": {\"fields\": [\"Movie rating\"]}}]', 11, 1),
(7, '2025-02-18 05:50:45.035622', '2', 'Action', 1, '[{\"added\": {}}]', 10, 1),
(8, '2025-02-18 05:57:52.365932', '2', 'Pushpa 2: The Rule', 1, '[{\"added\": {}}]', 11, 1),
(9, '2025-02-18 14:22:47.602314', '3', 'Action', 1, '[{\"added\": {}}]', 10, 1),
(10, '2025-02-18 14:24:21.839833', '1', 'Pushpa 2: The Rule', 1, '[{\"added\": {}}]', 11, 1),
(11, '2025-02-18 14:28:41.091657', '2', 'kaka', 1, '[{\"added\": {}}]', 11, 1),
(12, '2025-02-18 14:30:59.912176', '3', 'Pushpa 2: The Rule', 1, '[{\"added\": {}}]', 11, 1),
(13, '2025-02-18 15:08:48.056714', '3', 'Pushpa 2: The Rule', 2, '[{\"changed\": {\"fields\": [\"Movie image\"]}}]', 11, 1),
(14, '2025-02-18 16:16:44.141848', '2', 'kaka', 2, '[{\"changed\": {\"fields\": [\"Movie image\"]}}]', 11, 1),
(15, '2025-02-19 04:13:07.847775', '2', 'Chhaava', 2, '[{\"changed\": {\"fields\": [\"movie_name\", \"movie_description\", \"movie_star\", \"movie_rating\", \"movie_release_date\", \"movie_image\", \"movie_video\"]}}]', 11, 1),
(16, '2025-02-19 04:19:21.985096', '3', 'Trending', 2, '[{\"changed\": {\"fields\": [\"cat_name\"]}}]', 10, 1),
(17, '2025-02-19 04:19:38.503852', '4', 'Action', 1, '[{\"added\": {}}]', 10, 1),
(18, '2025-02-19 04:26:26.191046', '4', 'Vanvaas', 1, '[{\"added\": {}}]', 11, 1),
(19, '2025-02-19 04:30:00.727785', '5', 'Love hurts', 1, '[{\"added\": {}}]', 11, 1),
(20, '2025-02-19 04:35:08.928882', '3', 'Shiddat', 2, '[{\"changed\": {\"fields\": [\"movie_name\", \"movie_description\", \"movie_director\", \"movie_star\", \"movie_rating\", \"movie_duration\", \"movie_release_date\"]}}]', 11, 1),
(21, '2025-02-19 04:39:44.187282', '6', 'Match Fixing', 1, '[{\"added\": {}}]', 11, 1),
(22, '2025-02-19 04:44:35.059396', '7', 'Bahubali : The Beginning', 1, '[{\"added\": {}}]', 11, 1),
(23, '2025-02-19 04:45:27.290104', '7', 'Bahubali : The Beginning', 2, '[{\"changed\": {\"fields\": [\"movie_video\"]}}]', 11, 1),
(24, '2025-02-19 04:49:25.944132', '8', 'RRR', 1, '[{\"added\": {}}]', 11, 1),
(25, '2025-02-20 03:25:31.267144', '9', 'Sanak', 1, '[{\"added\": {}}]', 11, 1),
(26, '2025-02-20 03:28:47.174865', '9', 'Sanak', 3, '', 11, 1),
(27, '2025-02-20 03:33:46.362911', '10', 'K.G.F: Chapter 2', 1, '[{\"added\": {}}]', 11, 1),
(28, '2025-02-20 03:36:15.619611', '11', 'Jawan', 1, '[{\"added\": {}}]', 11, 1),
(29, '2025-02-20 03:38:48.885782', '12', 'Gadar: Ek Prem Katha', 1, '[{\"added\": {}}]', 11, 1),
(30, '2025-02-20 03:41:32.111433', '13', 'sholay', 1, '[{\"added\": {}}]', 11, 1),
(31, '2025-02-20 13:54:01.277880', '2', 'Chhaava', 2, '[{\"changed\": {\"fields\": [\"Movie image\"]}}]', 11, 1),
(32, '2025-02-20 13:54:54.465119', '4', 'Vanvaas', 2, '[{\"changed\": {\"fields\": [\"Movie image\"]}}]', 11, 1),
(33, '2025-02-20 13:55:06.786947', '5', 'Love hurts', 2, '[{\"changed\": {\"fields\": [\"Movie image\"]}}]', 11, 1),
(34, '2025-02-20 13:55:32.779731', '6', 'Match Fixing', 2, '[{\"changed\": {\"fields\": [\"Movie image\"]}}]', 11, 1),
(35, '2025-02-20 13:56:02.818082', '7', 'Bahubali : The Beginning', 2, '[{\"changed\": {\"fields\": [\"Movie image\"]}}]', 11, 1),
(36, '2025-02-20 13:56:12.292361', '8', 'RRR', 2, '[{\"changed\": {\"fields\": [\"Movie image\"]}}]', 11, 1),
(37, '2025-02-20 13:56:38.268106', '10', 'K.G.F: Chapter 2', 2, '[{\"changed\": {\"fields\": [\"Movie image\"]}}]', 11, 1),
(38, '2025-02-20 13:56:47.787122', '11', 'Jawan', 2, '[{\"changed\": {\"fields\": [\"Movie image\"]}}]', 11, 1),
(39, '2025-02-20 13:57:09.705484', '12', 'Gadar: Ek Prem Katha', 2, '[{\"changed\": {\"fields\": [\"Movie image\"]}}]', 11, 1),
(40, '2025-02-20 13:57:26.805407', '13', 'sholay', 2, '[{\"changed\": {\"fields\": [\"Movie image\"]}}]', 11, 1),
(41, '2025-02-20 13:58:25.234934', '4', 'Vanvaas', 2, '[{\"changed\": {\"fields\": [\"Movie image\"]}}]', 11, 1),
(42, '2025-02-21 11:54:42.493077', '12', 'Avengers: Endgame', 2, '[{\"changed\": {\"fields\": [\"Movie name\", \"Movie description\", \"Movie director\", \"Movie star\", \"Movie rating\", \"Movie duration\", \"Movie release date\", \"Movie image\", \"Movie video\"]}}]', 11, 1),
(43, '2025-02-21 12:42:55.392957', '1', 'Standard Plan', 2, '[{\"changed\": {\"fields\": [\"Sub time limit\"]}}]', 8, 1),
(44, '2025-02-21 13:00:48.920278', '1', 'Standard Plan', 2, '[{\"changed\": {\"fields\": [\"Sub time limit\"]}}]', 8, 1),
(45, '2025-02-21 13:09:53.277728', '3', 'md@gamil.com - Standard Plan - 2025-02-21 to 2025-03-21', 3, '', 9, 1),
(46, '2025-02-21 13:09:59.870423', '2', 'md@gamil.com - Standard Plan - 2025-02-21 to 2025-03-21', 3, '', 9, 1),
(47, '2025-02-21 13:12:26.348525', '5', 'md@gamil.com - Standard Plan - 2025-02-21 to 2025-03-13', 3, '', 9, 1),
(48, '2025-02-21 13:12:59.752266', '4', 'md@gamil.com - Standard Plan - 2025-02-21 to 2025-03-13', 3, '', 9, 1),
(49, '2025-02-21 13:25:29.053364', '2', 'Premium Plan', 2, '[{\"changed\": {\"fields\": [\"Sub time limit\"]}}]', 8, 1),
(50, '2025-02-21 13:25:46.841838', '7', 'md@gamil.com - Premium Plan - 2025-02-21 to 2025-02-21', 3, '', 9, 1),
(51, '2025-02-21 13:25:46.841838', '6', 'md@gamil.com - Premium Plan - 2025-02-21 to 2025-02-21', 3, '', 9, 1),
(52, '2025-02-21 13:29:21.206663', '8', 'md@gamil.com - Premium Plan - 2025-02-21 to 2026-02-21', 3, '', 9, 1),
(53, '2025-02-23 12:45:26.068313', '5', 'pro', 1, '[{\"added\": {}}]', 8, 1),
(54, '2025-02-23 12:46:33.589354', '6', 'advance', 1, '[{\"added\": {}}]', 8, 1),
(55, '2025-02-23 12:47:24.789711', '6', 'advance', 3, '', 8, 1),
(56, '2025-02-23 12:47:24.789711', '5', 'pro', 3, '', 8, 1),
(57, '2025-02-23 12:49:35.971250', '1', 'BasicPlan', 2, '[{\"changed\": {\"fields\": [\"Sub name\", \"Sub price\", \"Sub time limit\"]}}]', 8, 1),
(58, '2025-02-23 12:50:20.578058', '2', 'Standard Plan', 2, '[{\"changed\": {\"fields\": [\"Sub name\", \"Sub price\", \"Sub time limit\"]}}]', 8, 1),
(59, '2025-02-23 12:50:56.789672', '7', 'Premium Plan', 1, '[{\"added\": {}}]', 8, 1),
(60, '2025-02-23 13:45:12.546464', '12', 'Avengers: Endgame', 2, '[{\"changed\": {\"fields\": [\"Movie description\"]}}]', 11, 1);

-- --------------------------------------------------------

--
-- Table structure for table `django_content_type`
--

CREATE TABLE `django_content_type` (
  `id` int(11) NOT NULL,
  `app_label` varchar(100) NOT NULL,
  `model` varchar(100) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;

--
-- Dumping data for table `django_content_type`
--

INSERT INTO `django_content_type` (`id`, `app_label`, `model`) VALUES
(1, 'admin', 'logentry'),
(10, 'app', 'categories'),
(11, 'app', 'movies'),
(9, 'app', 'payment'),
(8, 'app', 'subscription'),
(7, 'app', 'user'),
(3, 'auth', 'group'),
(2, 'auth', 'permission'),
(4, 'auth', 'user'),
(5, 'contenttypes', 'contenttype'),
(6, 'sessions', 'session');

-- --------------------------------------------------------

--
-- Table structure for table `django_migrations`
--

CREATE TABLE `django_migrations` (
  `id` bigint(20) NOT NULL,
  `app` varchar(255) NOT NULL,
  `name` varchar(255) NOT NULL,
  `applied` datetime(6) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;

--
-- Dumping data for table `django_migrations`
--

INSERT INTO `django_migrations` (`id`, `app`, `name`, `applied`) VALUES
(1, 'contenttypes', '0001_initial', '2025-02-12 14:54:41.737954'),
(2, 'auth', '0001_initial', '2025-02-12 14:54:42.298426'),
(3, 'admin', '0001_initial', '2025-02-12 14:54:42.417381'),
(4, 'admin', '0002_logentry_remove_auto_add', '2025-02-12 14:54:42.433003'),
(5, 'admin', '0003_logentry_add_action_flag_choices', '2025-02-12 14:54:42.446171'),
(6, 'contenttypes', '0002_remove_content_type_name', '2025-02-12 14:54:42.550610'),
(7, 'auth', '0002_alter_permission_name_max_length', '2025-02-12 14:54:42.569748'),
(8, 'auth', '0003_alter_user_email_max_length', '2025-02-12 14:54:42.590092'),
(9, 'auth', '0004_alter_user_username_opts', '2025-02-12 14:54:42.603320'),
(10, 'auth', '0005_alter_user_last_login_null', '2025-02-12 14:54:42.671491'),
(11, 'auth', '0006_require_contenttypes_0002', '2025-02-12 14:54:42.671491'),
(12, 'auth', '0007_alter_validators_add_error_messages', '2025-02-12 14:54:42.721159'),
(13, 'auth', '0008_alter_user_username_max_length', '2025-02-12 14:54:42.738312'),
(14, 'auth', '0009_alter_user_last_name_max_length', '2025-02-12 14:54:42.755981'),
(15, 'auth', '0010_alter_group_name_max_length', '2025-02-12 14:54:42.774823'),
(16, 'auth', '0011_update_proxy_permissions', '2025-02-12 14:54:42.784181'),
(17, 'auth', '0012_alter_user_first_name_max_length', '2025-02-12 14:54:42.801420'),
(18, 'sessions', '0001_initial', '2025-02-12 14:54:42.838861'),
(19, 'app', '0001_initial', '2025-02-12 17:07:23.052143'),
(20, 'app', '0002_subscription', '2025-02-16 05:13:49.299221'),
(21, 'app', '0003_alter_subscription_sub_price_payment', '2025-02-16 13:56:32.350677'),
(22, 'app', '0004_rename_id_payment_user_alter_payment_end_date_and_more', '2025-02-16 14:28:00.700783'),
(23, 'app', '0005_categories', '2025-02-18 04:32:22.279728'),
(24, 'app', '0006_movies', '2025-02-18 05:10:46.530182'),
(25, 'app', '0007_alter_payment_sub_price', '2025-02-21 12:58:48.793108'),
(26, 'app', '0008_user_profile_image', '2025-02-21 16:02:43.829833');

-- --------------------------------------------------------

--
-- Table structure for table `django_session`
--

CREATE TABLE `django_session` (
  `session_key` varchar(40) NOT NULL,
  `session_data` longtext NOT NULL,
  `expire_date` datetime(6) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;

--
-- Dumping data for table `django_session`
--

INSERT INTO `django_session` (`session_key`, `session_data`, `expire_date`) VALUES
('oodxg8g0cvx907nxygwyr4gittpkhqz5', 'YmZmODY4Y2FkNjAxMjk0Yjg5NzkzYTIyMzA1NzBhNzk4Mjg1YjQyODp7InVzZXJfaWQiOjgsInVzZXJfbmFtZSI6ImpheSIsInVzZXJfZW1haWwiOiJqYXlAZ21haWwuY29tIiwiaXNfbG9naW4iOnRydWUsInN1Yl9wbGFuIjoiUHJlbWl1bSBQbGFuIn0=', '2025-03-06 04:24:25.182491'),
('vy5qo4kjhjb5t2xbivpqwan4k4dwga7e', '.eJxVjM0OgjAQBt9lz4S0tT_AyXj3GciWLbQKxVA4GOO7C5EYuW2-mZ0XLMlNdSCoRPa9Iw4OKnhM4Ykx-QX23Q0Y-n9w7rYlb8ZhVUKq-7ELEap5WlwGNS6zr39x4HDYLDZ3FzdAN4zduFbiPAWbb0q-05RfR3L9ZXcPAY_Jr98NtdqhVLbgRFoyVZSajGaWLGuElJydnClsS1oxKq1qW2alEMIYxZETwvsDxcFWtw:1tp44U:ucGsxT9XQ_0DOi3U-4zKRu3W8U0CBHJgoY4maFE7Kv0', '2025-03-17 11:34:54.573020');

--
-- Indexes for dumped tables
--

--
-- Indexes for table `app_categories`
--
ALTER TABLE `app_categories`
  ADD PRIMARY KEY (`cat_id`);

--
-- Indexes for table `app_movies`
--
ALTER TABLE `app_movies`
  ADD PRIMARY KEY (`movie_id`),
  ADD KEY `app_movies_category_id_9c120524_fk_app_categories_cat_id` (`category_id`);

--
-- Indexes for table `app_payment`
--
ALTER TABLE `app_payment`
  ADD PRIMARY KEY (`pay_id`),
  ADD KEY `app_payment_subscription_id_f01bc621_fk_app_subscription_sub_id` (`subscription_id`),
  ADD KEY `app_payment_user_id_0f781b98_fk_app_user_id` (`user_id`);

--
-- Indexes for table `app_subscription`
--
ALTER TABLE `app_subscription`
  ADD PRIMARY KEY (`sub_id`);

--
-- Indexes for table `app_user`
--
ALTER TABLE `app_user`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `auth_group`
--
ALTER TABLE `auth_group`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `name` (`name`);

--
-- Indexes for table `auth_group_permissions`
--
ALTER TABLE `auth_group_permissions`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `auth_group_permissions_group_id_permission_id_0cd325b0_uniq` (`group_id`,`permission_id`),
  ADD KEY `auth_group_permissio_permission_id_84c5c92e_fk_auth_perm` (`permission_id`);

--
-- Indexes for table `auth_permission`
--
ALTER TABLE `auth_permission`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `auth_permission_content_type_id_codename_01ab375a_uniq` (`content_type_id`,`codename`);

--
-- Indexes for table `auth_user`
--
ALTER TABLE `auth_user`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `username` (`username`);

--
-- Indexes for table `auth_user_groups`
--
ALTER TABLE `auth_user_groups`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `auth_user_groups_user_id_group_id_94350c0c_uniq` (`user_id`,`group_id`),
  ADD KEY `auth_user_groups_group_id_97559544_fk_auth_group_id` (`group_id`);

--
-- Indexes for table `auth_user_user_permissions`
--
ALTER TABLE `auth_user_user_permissions`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `auth_user_user_permissions_user_id_permission_id_14a6b632_uniq` (`user_id`,`permission_id`),
  ADD KEY `auth_user_user_permi_permission_id_1fbb5f2c_fk_auth_perm` (`permission_id`);

--
-- Indexes for table `django_admin_log`
--
ALTER TABLE `django_admin_log`
  ADD PRIMARY KEY (`id`),
  ADD KEY `django_admin_log_content_type_id_c4bce8eb_fk_django_co` (`content_type_id`),
  ADD KEY `django_admin_log_user_id_c564eba6_fk_auth_user_id` (`user_id`);

--
-- Indexes for table `django_content_type`
--
ALTER TABLE `django_content_type`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `django_content_type_app_label_model_76bd3d3b_uniq` (`app_label`,`model`);

--
-- Indexes for table `django_migrations`
--
ALTER TABLE `django_migrations`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `django_session`
--
ALTER TABLE `django_session`
  ADD PRIMARY KEY (`session_key`),
  ADD KEY `django_session_expire_date_a5c62663` (`expire_date`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `app_categories`
--
ALTER TABLE `app_categories`
  MODIFY `cat_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=5;

--
-- AUTO_INCREMENT for table `app_movies`
--
ALTER TABLE `app_movies`
  MODIFY `movie_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=14;

--
-- AUTO_INCREMENT for table `app_payment`
--
ALTER TABLE `app_payment`
  MODIFY `pay_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- AUTO_INCREMENT for table `app_subscription`
--
ALTER TABLE `app_subscription`
  MODIFY `sub_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=8;

--
-- AUTO_INCREMENT for table `app_user`
--
ALTER TABLE `app_user`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;

--
-- AUTO_INCREMENT for table `auth_group`
--
ALTER TABLE `auth_group`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `auth_group_permissions`
--
ALTER TABLE `auth_group_permissions`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `auth_permission`
--
ALTER TABLE `auth_permission`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=45;

--
-- AUTO_INCREMENT for table `auth_user`
--
ALTER TABLE `auth_user`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- AUTO_INCREMENT for table `auth_user_groups`
--
ALTER TABLE `auth_user_groups`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `auth_user_user_permissions`
--
ALTER TABLE `auth_user_user_permissions`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `django_admin_log`
--
ALTER TABLE `django_admin_log`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=61;

--
-- AUTO_INCREMENT for table `django_content_type`
--
ALTER TABLE `django_content_type`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=12;

--
-- AUTO_INCREMENT for table `django_migrations`
--
ALTER TABLE `django_migrations`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=27;

--
-- Constraints for dumped tables
--

--
-- Constraints for table `app_movies`
--
ALTER TABLE `app_movies`
  ADD CONSTRAINT `app_movies_category_id_9c120524_fk_app_categories_cat_id` FOREIGN KEY (`category_id`) REFERENCES `app_categories` (`cat_id`);

--
-- Constraints for table `app_payment`
--
ALTER TABLE `app_payment`
  ADD CONSTRAINT `app_payment_subscription_id_f01bc621_fk_app_subscription_sub_id` FOREIGN KEY (`subscription_id`) REFERENCES `app_subscription` (`sub_id`),
  ADD CONSTRAINT `app_payment_user_id_0f781b98_fk_app_user_id` FOREIGN KEY (`user_id`) REFERENCES `app_user` (`id`);

--
-- Constraints for table `auth_group_permissions`
--
ALTER TABLE `auth_group_permissions`
  ADD CONSTRAINT `auth_group_permissio_permission_id_84c5c92e_fk_auth_perm` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`),
  ADD CONSTRAINT `auth_group_permissions_group_id_b120cbf9_fk_auth_group_id` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`);

--
-- Constraints for table `auth_permission`
--
ALTER TABLE `auth_permission`
  ADD CONSTRAINT `auth_permission_content_type_id_2f476e4b_fk_django_co` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`);

--
-- Constraints for table `auth_user_groups`
--
ALTER TABLE `auth_user_groups`
  ADD CONSTRAINT `auth_user_groups_group_id_97559544_fk_auth_group_id` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`),
  ADD CONSTRAINT `auth_user_groups_user_id_6a12ed8b_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`);

--
-- Constraints for table `auth_user_user_permissions`
--
ALTER TABLE `auth_user_user_permissions`
  ADD CONSTRAINT `auth_user_user_permi_permission_id_1fbb5f2c_fk_auth_perm` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`),
  ADD CONSTRAINT `auth_user_user_permissions_user_id_a95ead1b_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`);

--
-- Constraints for table `django_admin_log`
--
ALTER TABLE `django_admin_log`
  ADD CONSTRAINT `django_admin_log_content_type_id_c4bce8eb_fk_django_co` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`),
  ADD CONSTRAINT `django_admin_log_user_id_c564eba6_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
