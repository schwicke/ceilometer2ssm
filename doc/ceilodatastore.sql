-- MySQL dump 10.13  Distrib 5.1.73, for redhat-linux-gnu (x86_64)
--
-- Host: localhost    Database: ceilodatastore
-- ------------------------------------------------------
-- Server version	5.1.73

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `current_record`
--

DROP TABLE IF EXISTS `current_record`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `current_record` (
  `user_id` varchar(255) DEFAULT NULL,
  `project_id` varchar(255) DEFAULT NULL,
  `resource_id` varchar(255) NOT NULL,
  `created_at` datetime DEFAULT NULL,
  `launched_at` datetime DEFAULT NULL,
  `deleted_at` datetime DEFAULT NULL,
  `terminated_at` datetime DEFAULT NULL,
  `hep_spec` varchar(255) DEFAULT NULL,
  `tenant_id` varchar(255) DEFAULT NULL,
  `tenant_name` varchar(255) DEFAULT NULL,
  `vmuuid` varchar(255) DEFAULT NULL,
  `node` varchar(255) DEFAULT NULL,
  `image_ref_url` varchar(255) DEFAULT NULL,
  `state` varchar(16) DEFAULT NULL,
  `memory_mb` int(11) DEFAULT NULL,
  `disk_gb` int(11) DEFAULT NULL,
  `vcpus` int(11) DEFAULT NULL,
  `host_name` varchar(255) DEFAULT NULL,
  `counter_name` varchar(32) DEFAULT NULL,
  `deleted` tinyint(4) DEFAULT '0',
  `cpu_counter_volume` varchar(64) DEFAULT NULL,
  `instance_counter_volume` varchar(64) DEFAULT NULL,
  `net_in_counter_volume` varchar(64) DEFAULT NULL,
  `net_out_counter_volume` varchar(64) DEFAULT NULL,
  `net_out_counter_unit` varchar(32) DEFAULT NULL,
  `net_in_counter_unit` varchar(32) DEFAULT NULL,
  `cpu_counter_unit` varchar(32) DEFAULT NULL,
  `instance_counter_unit` varchar(32) DEFAULT NULL,
  `group_name` varchar(64) DEFAULT NULL,
  `cpu_counter_sample_time` datetime DEFAULT NULL,
  `instance_counter_sample_time` datetime DEFAULT NULL,
  `net_in_counter_sample_time` datetime DEFAULT NULL,
  `net_out_counter_sample_time` datetime DEFAULT NULL,
  `cpu_counter_source` varchar(64) DEFAULT NULL,
  `instance_counter_source` varchar(64) DEFAULT NULL,
  `net_in_counter_source` varchar(64) DEFAULT NULL,
  `net_out_counter_source` varchar(64) DEFAULT NULL,
  `cpu_counter_type` varchar(32) DEFAULT NULL,
  `instance_counter_type` varchar(32) DEFAULT NULL,
  `net_in_counter_type` varchar(32) DEFAULT NULL,
  `net_out_counter_type` varchar(32) DEFAULT NULL,
  PRIMARY KEY (`resource_id`),
  UNIQUE KEY `uniq_resources0user_id0project_id0resource_id` (`user_id`,`project_id`,`resource_id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `metric_data`
--

DROP TABLE IF EXISTS `metric_data`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `metric_data` (
  `id` varchar(255) DEFAULT NULL,
  `r_id` varchar(255) DEFAULT NULL,
  `counter_name` varchar(32) DEFAULT NULL,
  `source` varchar(64) DEFAULT NULL,
  `counter_unit` varchar(32) DEFAULT NULL,
  `counter_volume` varchar(64) DEFAULT NULL,
  `counter_type` varchar(32) DEFAULT NULL,
  `start_time` datetime DEFAULT NULL,
  `end_time` datetime DEFAULT NULL,
  `sample_time` datetime DEFAULT NULL,
  UNIQUE KEY `uniq_metric_data0r_id0counter_name0sample_time` (`r_id`,`counter_name`,`sample_time`),
  CONSTRAINT `metric_data_ibfk_1` FOREIGN KEY (`r_id`) REFERENCES `resources` (`resource_id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `resources`
--

DROP TABLE IF EXISTS `resources`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `resources` (
  `user_id` varchar(255) DEFAULT NULL,
  `project_id` varchar(255) DEFAULT NULL,
  `resource_id` varchar(255) NOT NULL,
  `created_at` datetime DEFAULT NULL,
  `launched_at` datetime DEFAULT NULL,
  `deleted_at` datetime DEFAULT NULL,
  `terminated_at` datetime DEFAULT NULL,
  `deleted` tinyint(1) DEFAULT '0',
  `hep_spec` varchar(255) DEFAULT NULL,
  `tenant_id` varchar(255) DEFAULT NULL,
  `tenant_name` varchar(255) DEFAULT NULL,
  `vmuuid` varchar(255) DEFAULT NULL,
  `node` varchar(255) DEFAULT NULL,
  `image_ref_url` varchar(255) DEFAULT NULL,
  `state` varchar(16) DEFAULT NULL,
  `memory_mb` int(11) DEFAULT NULL,
  `disk_gb` int(11) DEFAULT NULL,
  `vcpus` int(11) DEFAULT NULL,
  `host_name` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`resource_id`),
  KEY `resources_deleted_idx` (`deleted`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2014-06-05 17:32:27
