-- MySQL dump 10.13  Distrib 8.0.29, for Linux (x86_64)
--
-- Host: vallah.mysql.pythonanywhere-services.com    Database: vallah$dbFlask
-- ------------------------------------------------------
-- Server version	8.0.33

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `pump_buddy`
--
-- Table structure for table `pump_buddy`
DROP TABLE IF EXISTS `pump_buddy`;
CREATE TABLE `pump_buddy` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(80) NOT NULL,
  `instance_name` varchar(80) NOT NULL,  -- Added column
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb3;

-- Dumping data for table `pump_buddy`
LOCK TABLES `pump_buddy` WRITE;
INSERT INTO `pump_buddy` VALUES 
(4,'Frae', 'default'),  -- Added default instance_name
(1,'Josef', 'default'),
(2,'Valle', 'default');
UNLOCK TABLES;

--
-- Table structure for table `workout`
--

DROP TABLE IF EXISTS `workout`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `workout` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(80) NOT NULL,
  `inkrement` int NOT NULL,
  `kind_of_workout` int NOT NULL,
  `instance_name` varchar(80) NOT NULL,  -- Added columna
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=
34 DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;


--
-- Dumping data for table `workout`
--


LOCK TABLES `workout` WRITE;
/*!40000 ALTER TABLE `workout` DISABLE KEYS */;
INSERT INTO `workout` VALUES 
(1,'BenchPress',5,0,"default"),
(2,'Squats',5,0,"default"),
(3,'Deadlift',5,0,"default"),
(19,'Sweatme bench lift',5,0,"default"),
(20,'Low bar',5,0,"default"),
(21,'wide lat pulldown',5,0,"default"),
(22,'rvrs btrfly retro machine',5,0,"default"),
(23,'bicep hammerstrength',1,0,"default"),
(24,'Flachbank kurzhantelen drücken',1,1,"default"),
(25,'schrägbank kurzhanteln drücken',1,1,"default"),
(26,'arnolds seated',1,0,"default"),
(27,'Ass',5,0,"default"),
(28,'beinbizip pink',5,0,"default"),
(29,'Bein biceps red',5,0,"default"),
(30,'21hs legpress',5,0,"default"),
(31,'good girl',5,0,"default"),
(32,'Bad Girl',5,0,"default"),
(33,'wade',5,0,"default"),
/*!40000 ALTER TABLE `workout` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2024-01-13 23:54:03
