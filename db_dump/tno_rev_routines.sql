CREATE DATABASE  IF NOT EXISTS `tno_rev` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci */ /*!80016 DEFAULT ENCRYPTION='N' */;
USE `tno_rev`;
-- MySQL dump 10.13  Distrib 8.0.29, for Win64 (x86_64)
--
-- Host: 127.0.0.1    Database: tno_rev
-- ------------------------------------------------------
-- Server version	8.0.29

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Temporary view structure for view `rev_check`
--

DROP TABLE IF EXISTS `rev_check`;
/*!50001 DROP VIEW IF EXISTS `rev_check`*/;
SET @saved_cs_client     = @@character_set_client;
/*!50503 SET character_set_client = utf8mb4 */;
/*!50001 CREATE VIEW `rev_check` AS SELECT 
 1 AS `url`,
 1 AS `org_name`,
 1 AS `org_address`,
 1 AS `org_rate`,
 1 AS `org_num_rate`,
 1 AS `org_num_rev`,
 1 AS `cnt`*/;
SET character_set_client = @saved_cs_client;

--
-- Final view structure for view `rev_check`
--

/*!50001 DROP VIEW IF EXISTS `rev_check`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_0900_ai_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`root`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `rev_check` AS select `org`.`url` AS `url`,`org`.`org_name` AS `org_name`,`org`.`org_address` AS `org_address`,`org`.`org_rate` AS `org_rate`,`org`.`org_num_rate` AS `org_num_rate`,`org`.`org_num_rev` AS `org_num_rev`,count(`reviews`.`url`) AS `cnt` from (`org` left join (select `reviews`.`idreviews` AS `idreviews`,`reviews`.`url` AS `url`,`reviews`.`rev_date` AS `rev_date`,`reviews`.`add_date` AS `add_date`,`reviews`.`rating` AS `rating`,`reviews`.`rev_text` AS `rev_text`,`reviews`.`sha256` AS `sha256`,`reviews`.`deleted` AS `deleted` from `reviews` where (`reviews`.`deleted` = 0)) `reviews` on((`org`.`url` = `reviews`.`url`))) where (`org`.`deleted` = '0') group by `org`.`url` */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;

--
-- Dumping events for database 'tno_rev'
--

--
-- Dumping routines for database 'tno_rev'
--
/*!50003 DROP PROCEDURE IF EXISTS `insert_rev` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'STRICT_TRANS_TABLES,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`dima`@`%` PROCEDURE `insert_rev`(f_url VARCHAR(1024), f_rev_date DATE, f_rating INT, rev_text TEXT, f_sha256 CHAR(64))
BEGIN
IF (SELECT count(*) FROM reviews WHERE url=f_url AND rev_date=f_rev_date AND sha256=f_sha256) > 0 THEN 
	UPDATE reviews SET deleted = '0' WHERE (url = f_url AND rev_date = f_rev_date AND sha256=f_sha256);
ELSE 
	INSERT INTO reviews (`url`, `rev_date`, `add_date`, `rating`, `rev_text`, `sha256`, `deleted`) VALUES
    (f_url, f_rev_date, CURDATE(), f_rating, rev_text, f_sha256, '0');
END IF;
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2022-07-11 18:10:39
