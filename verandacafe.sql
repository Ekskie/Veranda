-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Dec 31, 2024 at 02:08 AM
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
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `cart_items`
--

INSERT INTO `cart_items` (`id`, `name`, `price`, `image_url`, `quantity`, `created_at`) VALUES
(1, 'Chicksilog', 89.00, '/static/upload/Chicksilog.webp', 2, '2024-12-30 18:07:12'),
(2, 'Longsilog Garlic', 59.00, '/static/upload/Longsilog_Garlic.webp', 1, '2024-12-30 18:07:43'),
(3, 'Coke', 85.00, '/static/upload/Rectangle_4.png', 1, '2024-12-30 18:16:44');

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
(3, 'Beverage', 'Refreshing drinks'),
(18, 'Daily Offers', 'With Discount');

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
(5, 'Chicken Inasal', 159.00, 0, 32, 1, '/static/upload/Inasal.png', 0, 0, 0),
(22, 'Chicken Inasal', 129.00, 0, 15, 18, '/static/upload/Inasal.png', 0, 0, 0),
(24, 'Chicksilog', 129.00, 0, 15, 1, '/static/upload/Chicksilogunli.webp', 0, 0, 0),
(25, 'Pork Marinated', 139.00, 0, 20, 1, '/static/upload/Pork_Marinated.webp', 0, 0, 0),
(26, 'Liemsilog', 119.00, 0, 15, 1, '/static/upload/liemsilog_unli.webp', 0, 0, 0),
(27, 'Embusilog', 129.00, 0, 20, 1, '/static/upload/liemsilog_unli.webp', 0, 0, 0),
(28, 'Longsilog Marilaw', 159.00, 0, 20, 1, '/static/upload/Longsilog_Marilaw.webp', 0, 0, 0),
(29, 'Chicksilog', 89.00, 0, 15, 2, '/static/upload/Chicksilog.webp', 0, 0, 0),
(30, 'Embusilog', 79.00, 0, 15, 2, '/static/upload/Embusilog.webp', 0, 0, 0),
(31, 'Liemsilog', 69.00, 0, 20, 2, '/static/upload/Liemsilog.webp', 0, 0, 0),
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
(42, 'Sprite', 85.00, 0, 1, 3, '/static/upload/sprite.png', 0, 0, 0);

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
  `order_date` datetime DEFAULT current_timestamp(),
  `status` enum('Pending','Preparing','Completed','Cancelled') DEFAULT 'Pending'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

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
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=4;

--
-- AUTO_INCREMENT for table `menucategories`
--
ALTER TABLE `menucategories`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=20;

--
-- AUTO_INCREMENT for table `menuitems`
--
ALTER TABLE `menuitems`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=43;

--
-- AUTO_INCREMENT for table `orderdetails`
--
ALTER TABLE `orderdetails`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `orders`
--
ALTER TABLE `orders`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

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
