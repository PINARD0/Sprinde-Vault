CREATE DATABASE IF NOT EXISTS `MonederoPW`;
CREATE DATABASE IF NOT EXISTS `SprindeUserAuthDatabase`;

-- MySQL dump 10.13  Distrib 8.0.41, for Win64 (x86_64)
--
-- Host: localhost    Database: MonederoPW
-- ------------------------------------------------------
-- Server version	8.0.41

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
-- Table structure for table `emails`
--

USE `MonederoPW`;

DROP TABLE IF EXISTS `emails`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `emails` (
  `id` int NOT NULL AUTO_INCREMENT,
  `email` varchar(255) NOT NULL,
  `grupo` varchar(100) NOT NULL,
  `password_hash` varchar(255) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `email` (`email`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `emails`
--

LOCK TABLES `emails` WRITE;
/*!40000 ALTER TABLE `emails` DISABLE KEYS */;
INSERT INTO `emails` VALUES (1,'prueba@sprinde.com','YouTube','qFJRGc21VtFT4Y61K0DoKa1BdOY6QpLKuaBE9LtFi8Q='),(2,'prueba2@sprinde.com','Facebook','qWECpTaJbyIfCf2+uerac969AL1G9V2Vn8R7FZ8ybnk=');
/*!40000 ALTER TABLE `emails` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `hardware`
--

DROP TABLE IF EXISTS `hardware`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `hardware` (
  `id` int NOT NULL AUTO_INCREMENT,
  `CodeName` varchar(45) NOT NULL,
  `IP` varchar(15) NOT NULL,
  `Nombre` varchar(100) DEFAULT NULL,
  `password_hash` varchar(255) NOT NULL,
  `Hardware_type_Id` int NOT NULL,
  `Localizacion` varchar(100) NOT NULL,
  `is_active` tinyint(1) DEFAULT '1',
  PRIMARY KEY (`id`),
  UNIQUE KEY `CodeName` (`CodeName`),
  UNIQUE KEY `IP` (`IP`),
  KEY `Hardware_type_Id` (`Hardware_type_Id`),
  KEY `fk_location_code` (`Localizacion`),
  CONSTRAINT `hardware_ibfk_1` FOREIGN KEY (`Hardware_type_Id`) REFERENCES `hardwaretypes` (`type_id`)
) ENGINE=InnoDB AUTO_INCREMENT=4567 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `hardware`
--

LOCK TABLES `hardware` WRITE;
/*!40000 ALTER TABLE `hardware` DISABLE KEYS */;
INSERT INTO `hardware` VALUES (1,'A60-1','192.168.0.1','caca','QCHGjg3SwkOeh2/p7wQMWMjzmjmwmi3wr8aXRaZofeU=',2,'Ariel',1),(2,'A60-2','192.168.0.2','pipi','9tH2kudB3IMrGgzR7PeOJd+s7HDqg/22nHTdNMKoxTw=',6,'Ariel',1),(3,'M90-1','192.168.0.135','miro_cable','dubpnXg0oOi/IXnJrBpXIVh/Fn9z3iCLe6KhddE87II=',7,'Miró',1);
/*!40000 ALTER TABLE `hardware` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `hardwaretypes`
--

DROP TABLE IF EXISTS `hardwaretypes`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `hardwaretypes` (
  `type_id` int NOT NULL,
  `type_name` varchar(50) NOT NULL,
  PRIMARY KEY (`type_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `hardwaretypes`
--

LOCK TABLES `hardwaretypes` WRITE;
/*!40000 ALTER TABLE `hardwaretypes` DISABLE KEYS */;
INSERT INTO `hardwaretypes` VALUES (1,'Router'),(2,'Switch'),(3,'Access Point'),(4,'Portatil'),(5,'Teclado'),(6,'PC'),(7,'Cable'),(8,'Placa base');
/*!40000 ALTER TABLE `hardwaretypes` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `location_code`
--

DROP TABLE IF EXISTS `location_code`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `location_code` (
  `id` varchar(45) NOT NULL,
  `name` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `id_UNIQUE` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `location_code`
--

LOCK TABLES `location_code` WRITE;
/*!40000 ALTER TABLE `location_code` DISABLE KEYS */;
INSERT INTO `location_code` VALUES ('A60','Ariel'),('B30','Beso Beach'),('C30','Cactus'),('M30','Miranda'),('M90','Miró'),('O10','Oficina'),('P40','Cala d\'Or'),('R10','Juan'),('Y20','Zafiro Palace');
/*!40000 ALTER TABLE `location_code` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `master_check`
--

DROP TABLE IF EXISTS `master_check`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `master_check` (
  `id` int NOT NULL,
  `ciphertext` text NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `master_check`
--

LOCK TABLES `master_check` WRITE;
/*!40000 ALTER TABLE `master_check` DISABLE KEYS */;
INSERT INTO `master_check` VALUES (1,'QsAEyFo5TDZFg6EVGqlA4StsaaopmSRE+XRkOkGJeSU=');
/*!40000 ALTER TABLE `master_check` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-04-11 13:33:47







-- MySQL dump 10.13  Distrib 8.0.41, for Win64 (x86_64)
--
-- Host: localhost    Database: SprindeUserAuthDatabase
-- ------------------------------------------------------
-- Server version	8.0.41

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
-- Table structure for table `users`
--

USE `SprindeUserAuthDatabase`;

DROP TABLE IF EXISTS `users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `users` (
  `id` int NOT NULL AUTO_INCREMENT,
  `email` varchar(255) NOT NULL,
  `password_hash` varchar(255) NOT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `is_admin` tinyint(1) DEFAULT '0',
  PRIMARY KEY (`id`),
  UNIQUE KEY `email` (`email`)
) ENGINE=InnoDB AUTO_INCREMENT=40 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `users`
--

LOCK TABLES `users` WRITE;
/*!40000 ALTER TABLE `users` DISABLE KEYS */;
INSERT INTO `users` VALUES (1,'LOLA4@gmail.com','$2b$12$z1Tzrd4eHXtD3UsxExfbIuGWp8xKxXS/m/uz36gnzsENEatnc15oe','2025-04-01 06:28:16',0),(2,'aaaaaaa@sprinde.com','$2b$12$3t6kQyijllVtjPE5xDRSSuXny7VHLy/omnBA2RzgRboCc0cQW7hqe','2025-04-01 08:06:14',0),(3,'ola34@gmail.net','$2b$12$kw./KLoC7xYQLTe4DGrmxOcKvG4GaPsyTxGgE1iopBfbPle3fRHSe','2025-04-02 08:41:48',0),(4,'lol2@gmail.net','$2b$12$T8hZyjJ1gC7mZxuxpBE8DuCs5hd2hu83ZDnWFCmmeIROtVc.uzlqO','2025-03-31 12:42:17',0),(5,'user57@example.com','$2b$12$YLzbq3PemBTQHe/IdLcoFOjnLT..Ess5lqt0Ew0/w7Oojo97OM1Ua','2025-04-11 11:20:26',0),(6,'web2@sprinde.com','$2b$12$y/DJN0FrZn1fh75crYSqiObjnSl54CzJYA1pzPJ1PtD3.50ufnnQy','2025-03-21 10:50:41',0),(9,'admin@example.com','$2b$12$fjzuErpGKynWuC2LplqS4.qsGANkQcJsHmpcxK63sVsvedW4NZb.O','2025-03-21 11:07:04',1),(11,'user100@example.com','password_hash_example','2025-03-26 15:38:28',0),(12,'user200@example.com','password_hash_example','2025-03-26 15:38:28',0),(15,'user5@example.com','password_hash_example','2025-03-26 15:38:28',0);
/*!40000 ALTER TABLE `users` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-04-11 13:33:47