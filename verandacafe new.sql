-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Jan 05, 2025 at 03:00 PM
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
-- Database: `verandacafe`
--

-- --------------------------------------------------------

--
-- Table structure for table `cart_items`
--

CREATE TABLE `cart_items` (
  `id` int(11) NOT NULL,
  `name` varchar(255) NOT NULL,
  `price` decimal(10,2) NOT NULL,
  `image_url` varchar(255) NOT NULL,
  `quantity` int(11) DEFAULT 1,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `temporary_user_id` varchar(255) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `menucategories`
--

CREATE TABLE `menucategories` (
  `id` int(11) NOT NULL,
  `name` varchar(100) NOT NULL,
  `description` text DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `menucategories`
--

INSERT INTO `menucategories` (`id`, `name`, `description`) VALUES
(1, 'Unli Rice', 'Unli sa sarap'),
(2, 'Tapsilog', 'Filipino breakfast favorites'),
(3, 'Beverage', 'Refreshing drinks');

-- --------------------------------------------------------

--
-- Table structure for table `menuitems`
--

CREATE TABLE `menuitems` (
  `id` int(11) NOT NULL,
  `name` varchar(100) NOT NULL,
  `price` decimal(10,2) NOT NULL,
  `discounted_price` int(11) NOT NULL,
  `preparation_time` int(11) NOT NULL,
  `category_id` int(11) DEFAULT NULL,
  `image_url` varchar(255) DEFAULT NULL,
  `is_active` tinyint(1) NOT NULL,
  `is_bestSeller` tinyint(1) NOT NULL,
  `sales_count` int(11) DEFAULT 0
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `menuitems`
--

INSERT INTO `menuitems` (`id`, `name`, `price`, `discounted_price`, `preparation_time`, `category_id`, `image_url`, `is_active`, `is_bestSeller`, `sales_count`) VALUES
(5, 'Chicken Inasal', 159.00, 129, 32, 1, '/static/upload/Inasal.png', 1, 0, 1),
(24, 'Chicksilog', 129.00, 119, 15, 1, '/static/upload/Chicksilogunli.webp', 1, 1, 5),
(25, 'Pork Marinated', 139.00, 120, 20, 1, '/static/upload/Pork_Marinated.webp', 1, 0, 1),
(26, 'Liemsilog', 119.00, 0, 15, 1, '/static/upload/liemsilog_unli.webp', 0, 0, 1),
(27, 'Embusilog', 129.00, 0, 20, 1, '/static/upload/liemsilog_unli.webp', 0, 0, 0),
(28, 'Longsilog Marilaw', 159.00, 0, 20, 1, '/static/upload/Longsilog_Marilaw.webp', 0, 0, 0),
(29, 'Chicksilog', 89.00, 0, 15, 2, '/static/upload/Chicksilog.webp', 0, 1, 5),
(30, 'Embusilog', 79.00, 0, 15, 2, '/static/upload/Embusilog.webp', 0, 0, 0),
(31, 'Liemsilog', 69.00, 0, 20, 2, '/static/upload/Liemsilog.webp', 0, 0, 1),
(32, 'Tosilog', 59.00, 0, 15, 2, '/static/upload/Tosilog.webp', 0, 0, 0),
(33, 'Shanghaisilog', 79.00, 0, 15, 2, '/static/upload/Shanghai_Silog.webp', 0, 0, 0),
(34, 'Longsilog Garlic', 59.00, 0, 20, 2, '/static/upload/Longsilog_Garlic.webp', 0, 0, 0),
(35, 'Adobosilog ', 69.00, 0, 20, 2, '/static/upload/Adobosilog.webp', 0, 0, 0),
(36, 'Fish Fillet Silog', 89.00, 0, 20, 2, '/static/upload/5.webp', 0, 0, 0),
(37, 'Danggit Silog', 59.00, 0, 15, 2, '/static/upload/Danggit_Silog.webp', 0, 0, 0),
(38, 'Porksilog ', 89.00, 0, 20, 2, '/static/upload/Porksilog.webp', 0, 0, 0),
(39, 'Longsilog Hamonado', 79.00, 0, 20, 2, '/static/upload/Longsilog_Hamonado.webp', 0, 0, 0),
(40, 'Coke', 85.00, 0, 1, 3, '/static/upload/Rectangle_4.png', 0, 0, 0),
(41, 'Ice Tea Pitcher', 59.00, 0, 1, 3, '/static/upload/pitcher.png', 0, 0, 0),
(42, 'Sprite', 85.00, 0, 1, 3, '/static/upload/sprite.png', 0, 1, 2);

-- --------------------------------------------------------

--
-- Table structure for table `orderdetails`
--

CREATE TABLE `orderdetails` (
  `id` int(11) NOT NULL,
  `order_id` int(11) DEFAULT NULL,
  `menu_item_id` int(11) DEFAULT NULL,
  `quantity` int(11) NOT NULL DEFAULT 1
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `orders`
--

CREATE TABLE `orders` (
  `id` int(11) NOT NULL,
  `user_id` varchar(255) NOT NULL,
  `product_name` varchar(255) NOT NULL,
  `price` decimal(10,2) NOT NULL,
  `quantity` int(11) NOT NULL,
  `order_status` enum('Pending','Completed','Cancelled','OnGoing') DEFAULT 'Pending',
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `updated_at` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  `dine_in_takeout` enum('Dine In','Take Out') NOT NULL DEFAULT 'Dine In',
  `customer_name` varchar(255) DEFAULT NULL,
  `special_requests` text DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `orders`
--

INSERT INTO `orders` (`id`, `user_id`, `product_name`, `price`, `quantity`, `order_status`, `created_at`, `updated_at`, `dine_in_takeout`, `customer_name`, `special_requests`) VALUES
(1, '87bad895-6806-4de7-b1da-226a6b41fe11', 'Chicksilog', 129.00, 1, 'Cancelled', '2025-01-02 07:00:36', '2025-01-02 07:07:08', 'Dine In', 'denn', ''),
(2, 'b0586302-5ee3-48da-925c-5d0246d33496', 'Chicksilog', 129.00, 1, 'Completed', '2025-01-02 07:02:03', '2025-01-02 11:19:26', '', 'de', 'd'),
(3, '3dacb039-dd3f-42e9-99c6-70be94d9e509', 'Chicken Inasal', 159.00, 1, 'Completed', '2025-01-02 07:03:04', '2025-01-02 11:20:51', 'Dine In', 'gg', ''),
(4, '4eb06f73-e2ff-4c1d-b7fd-b82434ff2291', 'Chicken Inasal', 159.00, 1, 'Cancelled', '2025-01-02 07:03:36', '2025-01-02 10:09:52', 'Dine In', 'asd', ''),
(5, 'b0b9daab-042b-46cd-ac8b-a28bae98c0b1', 'Chicken Inasal', 159.00, 1, 'Completed', '2025-01-02 07:05:02', '2025-01-02 11:21:46', '', 'gg', ''),
(6, 'ba5ede81-7450-4376-a601-af08da8273e2', 'Chicken Inasal', 159.00, 1, 'Completed', '2025-01-02 07:05:16', '2025-01-02 11:32:34', '', 'asd', ''),
(7, '2508e16e-3603-40c7-9f54-05ad37eee5f8', 'Chicksilog', 129.00, 1, 'Completed', '2025-01-02 07:06:44', '2025-01-02 11:21:26', 'Take Out', 'renz', ''),
(8, 'da3b0d60-516d-46da-8f6b-ebce8455d82c', 'Chicken Inasal', 159.00, 1, 'Completed', '2025-01-02 10:06:58', '2025-01-02 11:14:59', 'Take Out', 'red', 'toyo'),
(9, 'da3b0d60-516d-46da-8f6b-ebce8455d82c', 'Liemsilog', 69.00, 1, 'Completed', '2025-01-02 10:06:58', '2025-01-02 11:14:59', 'Take Out', 'red', 'toyo'),
(10, 'c665abd8-0916-4532-ab4d-d079f7f9b8e9', 'Chicken Inasal', 159.00, 1, 'Completed', '2025-01-02 10:07:45', '2025-01-02 11:08:54', 'Dine In', 'josh', 'extrang sabaw'),
(11, 'c665abd8-0916-4532-ab4d-d079f7f9b8e9', 'Longsilog Marilaw', 159.00, 1, 'Completed', '2025-01-02 10:07:45', '2025-01-02 11:08:54', 'Dine In', 'josh', 'extrang sabaw'),
(12, 'c665abd8-0916-4532-ab4d-d079f7f9b8e9', 'Chicksilog', 129.00, 1, 'Completed', '2025-01-02 10:07:45', '2025-01-02 11:08:54', 'Dine In', 'josh', 'extrang sabaw'),
(13, 'c665abd8-0916-4532-ab4d-d079f7f9b8e9', 'Pork Marinated', 139.00, 1, 'Completed', '2025-01-02 10:07:45', '2025-01-02 11:08:54', 'Dine In', 'josh', 'extrang sabaw'),
(14, 'c665abd8-0916-4532-ab4d-d079f7f9b8e9', 'Liemsilog', 119.00, 1, 'Completed', '2025-01-02 10:07:45', '2025-01-02 11:08:54', 'Dine In', 'josh', 'extrang sabaw'),
(15, 'fc1391d7-901a-4222-a87b-7782afb3e7ad', 'Chicken Inasal', 159.00, 1, 'Completed', '2025-01-02 10:29:23', '2025-01-02 11:16:42', 'Dine In', 'vince', ''),
(16, 'fc1391d7-901a-4222-a87b-7782afb3e7ad', 'Pork Marinated', 139.00, 1, 'Completed', '2025-01-02 10:29:23', '2025-01-02 11:16:42', 'Dine In', 'vince', ''),
(17, '2d2aa5b1-b071-4e01-b191-e31b7e13917f', 'Chicksilog', 129.00, 1, 'Completed', '2025-01-02 11:22:50', '2025-01-02 11:23:45', 'Dine In', 'denn', ''),
(18, '2d2aa5b1-b071-4e01-b191-e31b7e13917f', 'Longsilog Marilaw', 159.00, 1, 'Completed', '2025-01-02 11:22:50', '2025-01-02 11:23:45', 'Dine In', 'denn', ''),
(19, '13bf9308-02cf-4f53-bba7-02bd7eb9f460', 'Longsilog Marilaw', 159.00, 1, 'Completed', '2025-01-02 11:24:12', '2025-01-02 11:24:46', 'Dine In', 'barth', ''),
(20, '13bf9308-02cf-4f53-bba7-02bd7eb9f460', 'Coke', 85.00, 1, 'Completed', '2025-01-02 11:24:12', '2025-01-02 11:24:46', 'Dine In', 'barth', ''),
(21, '9bbe3306-6002-4f97-b67e-aef2a7bc73e5', 'Embusilog', 79.00, 1, 'Completed', '2025-01-02 11:26:16', '2025-01-02 11:26:23', 'Take Out', 'vince', 'toyo'),
(22, '9992dcf3-264f-4a6c-b2f2-1efa5be9d5a0', 'Pork Marinated', 139.00, 1, 'Completed', '2025-01-02 11:27:22', '2025-01-02 11:27:39', 'Dine In', 'denn', 'denn'),
(23, 'c9ec8aeb-2473-4745-b1e1-93c1418c01f4', 'Ice Tea Pitcher', 59.00, 1, 'Completed', '2025-01-02 11:35:52', '2025-01-02 11:36:09', 'Dine In', 'vince', ''),
(24, '5ee05e67-f74c-47f6-8062-01e6e6c7ea72', 'Sprite', 85.00, 1, 'Completed', '2025-01-02 11:37:27', '2025-01-02 11:37:33', 'Dine In', 'red', 'denn'),
(25, '7a2eb298-4d9f-446e-b40b-654cea6b04f2', 'Sprite', 85.00, 1, 'Completed', '2025-01-02 11:38:02', '2025-01-02 11:38:13', 'Take Out', 'gg', ''),
(26, '47f7628c-c66d-4c50-8101-3aa565c69265', 'Sprite', 85.00, 1, 'Completed', '2025-01-02 11:42:44', '2025-01-02 11:42:51', 'Dine In', 'red', ''),
(27, '248df980-b440-4197-8412-b84f227d103a', 'Chicksilog', 89.00, 1, 'Completed', '2025-01-02 12:37:09', '2025-01-02 12:37:17', 'Dine In', 'Yuri', ''),
(28, 'e2fe102f-205a-4f97-b81d-5636e606ec29', 'Sprite', 85.00, 1, 'Completed', '2025-01-02 13:15:33', '2025-01-02 13:15:43', 'Dine In', 'gg', '');

--
-- Indexes for dumped tables
--

--
-- Indexes for table `cart_items`
--
ALTER TABLE `cart_items`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `menucategories`
--
ALTER TABLE `menucategories`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `menuitems`
--
ALTER TABLE `menuitems`
  ADD PRIMARY KEY (`id`),
  ADD KEY `category_id` (`category_id`);

--
-- Indexes for table `orderdetails`
--
ALTER TABLE `orderdetails`
  ADD PRIMARY KEY (`id`),
  ADD KEY `order_id` (`order_id`),
  ADD KEY `menu_item_id` (`menu_item_id`);

--
-- Indexes for table `orders`
--
ALTER TABLE `orders`
  ADD PRIMARY KEY (`id`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `cart_items`
--
ALTER TABLE `cart_items`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=205;

--
-- AUTO_INCREMENT for table `menucategories`
--
ALTER TABLE `menucategories`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=21;

--
-- AUTO_INCREMENT for table `menuitems`
--
ALTER TABLE `menuitems`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=44;

--
-- AUTO_INCREMENT for table `orderdetails`
--
ALTER TABLE `orderdetails`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `orders`
--
ALTER TABLE `orders`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=29;

--
-- Constraints for dumped tables
--

--
-- Constraints for table `menuitems`
--
ALTER TABLE `menuitems`
  ADD CONSTRAINT `menuitems_ibfk_1` FOREIGN KEY (`category_id`) REFERENCES `menucategories` (`id`);

--
-- Constraints for table `orderdetails`
--
ALTER TABLE `orderdetails`
  ADD CONSTRAINT `orderdetails_ibfk_1` FOREIGN KEY (`order_id`) REFERENCES `orders` (`id`),
  ADD CONSTRAINT `orderdetails_ibfk_2` FOREIGN KEY (`menu_item_id`) REFERENCES `menuitems` (`id`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
