-- MySQL dump 10.13  Distrib 5.5.24, for osx10.6 (i386)
--
-- Host: localhost    Database: phylografter
-- ------------------------------------------------------
-- Server version	5.5.24-log

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
-- Table structure for table `apg_taxon`
--

DROP TABLE IF EXISTS `apg_taxon`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `apg_taxon` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `parent` int(11) DEFAULT NULL,
  `next` int(11) DEFAULT NULL,
  `back` int(11) DEFAULT NULL,
  `depth` int(11) DEFAULT NULL,
  `name` varchar(255) NOT NULL,
  `rank` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB AUTO_INCREMENT=29037 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `auth_cas`
--

DROP TABLE IF EXISTS `auth_cas`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `auth_cas` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) DEFAULT NULL,
  `uuid` varchar(255) DEFAULT NULL,
  `url` varchar(255) DEFAULT NULL,
  `created_on` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `user_id__idx` (`user_id`),
  CONSTRAINT `auth_cas_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `auth_event`
--

DROP TABLE IF EXISTS `auth_event`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `auth_event` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `time_stamp` datetime DEFAULT NULL,
  `user_id` int(11) DEFAULT NULL,
  `description` longtext,
  `origin` varchar(255) DEFAULT NULL,
  `client_ip` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `user_id__idx` (`user_id`),
  CONSTRAINT `auth_event_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=679 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `auth_group`
--

DROP TABLE IF EXISTS `auth_group`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `auth_group` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `description` longtext,
  `role` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=24 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `auth_membership`
--

DROP TABLE IF EXISTS `auth_membership`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `auth_membership` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) DEFAULT NULL,
  `group_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `user_id__idx` (`user_id`),
  KEY `group_id__idx` (`group_id`),
  CONSTRAINT `auth_membership_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`) ON DELETE CASCADE,
  CONSTRAINT `auth_membership_ibfk_2` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=37 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `auth_permission`
--

DROP TABLE IF EXISTS `auth_permission`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `auth_permission` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `group_id` int(11) DEFAULT NULL,
  `record_id` int(11) DEFAULT NULL,
  `table_name` varchar(255) DEFAULT NULL,
  `name` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `group_id__idx` (`group_id`),
  CONSTRAINT `auth_permission_ibfk_1` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `auth_user`
--

DROP TABLE IF EXISTS `auth_user`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `auth_user` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `reset_password_key` varchar(255) DEFAULT NULL,
  `password` varchar(255) DEFAULT NULL,
  `registration_key` varchar(255) DEFAULT NULL,
  `email` varchar(255) DEFAULT NULL,
  `first_name` varchar(128) DEFAULT NULL,
  `last_name` varchar(128) DEFAULT NULL,
  `registration_id` varchar(512) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=22 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `clipboard`
--

DROP TABLE IF EXISTS `clipboard`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `clipboard` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `nodeId` int(11) DEFAULT NULL,
  `name` varchar(255) DEFAULT NULL,
  `creationDate` datetime DEFAULT NULL,
  `treetype` varchar(255) DEFAULT NULL,
  `user` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `nodeId__idx` (`nodeId`),
  KEY `userIdx` (`user`),
  CONSTRAINT `clipboard_ibfk_1` FOREIGN KEY (`user`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=95 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `gene`
--

DROP TABLE IF EXISTS `gene`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `gene` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  `genome` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `gnode`
--

DROP TABLE IF EXISTS `gnode`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `gnode` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `label` varchar(128) DEFAULT NULL,
  `ntips` int(11) DEFAULT NULL,
  `pruned` char(1) NOT NULL DEFAULT 'F',
  `next` int(11) DEFAULT NULL,
  `back` int(11) DEFAULT NULL,
  `length` double DEFAULT NULL,
  `age` double DEFAULT NULL,
  `age_min` double DEFAULT NULL,
  `age_max` double DEFAULT NULL,
  `tree` int(11) DEFAULT NULL,
  `snode` int(11) DEFAULT NULL,
  `stree` int(11) DEFAULT NULL,
  `mtime` datetime DEFAULT NULL,
  `parent` int(11) DEFAULT NULL,
  `parent__tmp` int(11) DEFAULT NULL,
  `isleaf` char(1) DEFAULT NULL,
  `viewweight` double DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `tree__idx` (`tree`),
  KEY `snode__idx` (`snode`),
  KEY `stree__idx` (`stree`),
  KEY `parent__idx` (`parent`),
  CONSTRAINT `gnode_ibfk_1` FOREIGN KEY (`tree`) REFERENCES `gtree` (`id`) ON DELETE NO ACTION,
  CONSTRAINT `gnode_ibfk_2` FOREIGN KEY (`snode`) REFERENCES `snode` (`id`) ON DELETE NO ACTION,
  CONSTRAINT `gnode_ibfk_3` FOREIGN KEY (`stree`) REFERENCES `stree` (`id`) ON DELETE NO ACTION
) ENGINE=InnoDB AUTO_INCREMENT=148050 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `gtree`
--

DROP TABLE IF EXISTS `gtree`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `gtree` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `contributor` varchar(128) DEFAULT NULL,
  `mtime` datetime DEFAULT NULL,
  `title` varchar(255) DEFAULT NULL,
  `comment` longtext,
  `date` datetime DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=482 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `gtree_edit`
--

DROP TABLE IF EXISTS `gtree_edit`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `gtree_edit` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `gtree` int(11) DEFAULT NULL,
  `action` varchar(255) DEFAULT NULL,
  `target_gnode` int(11) DEFAULT NULL,
  `comment` longtext,
  `mtime` datetime DEFAULT NULL,
  `user` int(11) DEFAULT NULL,
  `affected_node_id` int(11) DEFAULT NULL,
  `affected_clade_id` int(11) DEFAULT NULL,
  `originaltreetype` varchar(255) DEFAULT NULL,
  `clipboard_node__tmp` int(11) DEFAULT NULL,
  `newNodeOriginId` int(11) DEFAULT NULL,
  `newNodeOriginType` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `gtree__idx` (`gtree`),
  KEY `target_gnode__idx` (`target_gnode`),
  KEY `user__idx` (`user`),
  CONSTRAINT `gtree_edit_ibfk_1` FOREIGN KEY (`gtree`) REFERENCES `gtree` (`id`) ON DELETE CASCADE,
  CONSTRAINT `gtree_edit_ibfk_2` FOREIGN KEY (`target_gnode`) REFERENCES `gnode` (`id`) ON DELETE CASCADE,
  CONSTRAINT `gtree_edit_ibfk_4` FOREIGN KEY (`user`) REFERENCES `auth_user` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=704 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `gtree_share`
--

DROP TABLE IF EXISTS `gtree_share`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `gtree_share` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user` int(11) DEFAULT NULL,
  `gtree` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `user__idx` (`user`),
  KEY `gtree__idx` (`gtree`),
  CONSTRAINT `gtree_share_ibfk_1` FOREIGN KEY (`user`) REFERENCES `auth_user` (`id`),
  CONSTRAINT `gtree_share_ibfk_2` FOREIGN KEY (`gtree`) REFERENCES `gtree` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=14 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `ncbi_name`
--

DROP TABLE IF EXISTS `ncbi_name`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ncbi_name` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `taxid` int(11) NOT NULL,
  `name` varchar(255) DEFAULT NULL,
  `unique_name` varchar(255) DEFAULT NULL,
  `name_class` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `unique_name` (`unique_name`),
  KEY `taxid` (`taxid`),
  CONSTRAINT `ncbi_name_ibfk_1` FOREIGN KEY (`taxid`) REFERENCES `ncbi_node` (`taxid`) ON DELETE NO ACTION
) ENGINE=InnoDB AUTO_INCREMENT=234995 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `ncbi_node`
--

DROP TABLE IF EXISTS `ncbi_node`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ncbi_node` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `taxid` int(11) NOT NULL,
  `name` varchar(255) DEFAULT NULL,
  `parent` int(11) DEFAULT NULL,
  `next` int(11) DEFAULT NULL,
  `back` int(11) DEFAULT NULL,
  `depth` int(11) DEFAULT NULL,
  `rank` varchar(255) DEFAULT NULL,
  `hidden` char(1) NOT NULL DEFAULT 'F',
  `comments` longtext,
  PRIMARY KEY (`id`),
  UNIQUE KEY `taxid` (`taxid`),
  KEY `rank` (`rank`)
) ENGINE=InnoDB AUTO_INCREMENT=119054 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `ncbi_taxon`
--

DROP TABLE IF EXISTS `ncbi_taxon`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ncbi_taxon` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `taxid` int(11) NOT NULL,
  `parent` int(11) DEFAULT NULL,
  `next` int(11) DEFAULT NULL,
  `back` int(11) DEFAULT NULL,
  `depth` int(11) DEFAULT NULL,
  `name` varchar(255) NOT NULL,
  `rank` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `taxid` (`taxid`)
) ENGINE=InnoDB AUTO_INCREMENT=30493 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `ottol_name`
--

DROP TABLE IF EXISTS `ottol_name`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ottol_name` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `opentree_uid` char(32) NOT NULL,
  `opentree_parent_uid` char(32) DEFAULT NULL,
  `opentree_accepted_uid` char(32) DEFAULT NULL,
  `preottol_taxid` bigint(11) unsigned DEFAULT NULL,
  `preottol_parent_taxid` bigint(11) unsigned DEFAULT NULL,
  `preottol_source` varchar(64) DEFAULT NULL,
  `preottol_source_taxid` varchar(64) DEFAULT NULL,
  `ncbi_taxid` int(11) DEFAULT NULL,
  `treebase_taxid` int(11) DEFAULT NULL,
  `namebank_taxid` int(11) DEFAULT NULL,
  `node` int(11) unsigned DEFAULT NULL,
  `name` varchar(255) NOT NULL,
  `unique_name` varchar(255) DEFAULT NULL,
  `preottol_authority` varchar(255) DEFAULT NULL,
  `preottol_code` varchar(255) DEFAULT NULL,
  `rank` varchar(255) DEFAULT NULL,
  `preottol_date` varchar(255) DEFAULT NULL,
  `comments` varchar(255) DEFAULT NULL,
  `preottol_homonym_flag` char(1) NOT NULL DEFAULT 'F',
  `preottol_pdb_flag` char(1) NOT NULL DEFAULT 'F',
  `mtime` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `opentree_uid` (`opentree_uid`),
  UNIQUE KEY `preottol_taxid` (`preottol_taxid`),
  KEY `node__idx` (`node`),
  KEY `name` (`name`),
  KEY `unique_name` (`unique_name`)
) ENGINE=InnoDB AUTO_INCREMENT=2163979 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `ottol_node`
--

DROP TABLE IF EXISTS `ottol_node`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ottol_node` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `uid` bigint(11) unsigned NOT NULL,
  `parent` int(11) DEFAULT NULL,
  `next` int(11) DEFAULT NULL,
  `back` int(11) DEFAULT NULL,
  `depth` int(11) DEFAULT NULL,
  `name` int(11) NOT NULL,
  `mtime` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uid` (`uid`),
  KEY `name` (`name`),
  KEY `next` (`next`),
  KEY `depth` (`depth`),
  KEY `parent` (`parent`),
  KEY `back` (`back`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `otu`
--

DROP TABLE IF EXISTS `otu`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `otu` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `study` int(11) DEFAULT NULL,
  `label` varchar(255) NOT NULL,
  `taxon` int(11) DEFAULT NULL,
  `ottol_name` int(11) DEFAULT NULL,
  `tb_nexml_id` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `study__idx` (`study`),
  KEY `taxon__idx` (`taxon`),
  KEY `ottol_name` (`ottol_name`),
  CONSTRAINT `otu_ibfk_1` FOREIGN KEY (`study`) REFERENCES `study` (`id`) ON DELETE NO ACTION,
  CONSTRAINT `otu_ibfk_2` FOREIGN KEY (`taxon`) REFERENCES `taxon` (`id`) ON DELETE NO ACTION
) ENGINE=InnoDB AUTO_INCREMENT=69870 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `phylogramNodeMeta`
--

DROP TABLE IF EXISTS `phylogramNodeMeta`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `phylogramNodeMeta` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `tree` int(11) DEFAULT NULL,
  `treeType` varchar(255) DEFAULT NULL,
  `text` varchar(255) DEFAULT NULL,
  `weight` double DEFAULT NULL,
  `nodeid` int(11) DEFAULT NULL,
  `longesttraversal` double DEFAULT NULL,
  `descendanttipcount` int(11) DEFAULT NULL,
  `closestdescendantlabel` varchar(255) DEFAULT NULL,
  `next` int(11) unsigned NOT NULL,
  `back` int(11) unsigned NOT NULL,
  `descendantlabelcount` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `autoCollapseIdx` (`tree`,`treeType`,`next`,`back`,`weight`),
  KEY `descendantLabelIdx` (`tree`,`treeType`,`next`,`back`,`text`)
) ENGINE=InnoDB AUTO_INCREMENT=859982 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `plantlist`
--

DROP TABLE IF EXISTS `plantlist`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `plantlist` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `major_group` varchar(255) DEFAULT NULL,
  `family` varchar(255) DEFAULT NULL,
  `genus_hybrid_marker` varchar(255) DEFAULT NULL,
  `genus` varchar(255) DEFAULT NULL,
  `species_hybrid_marker` varchar(255) DEFAULT NULL,
  `species` varchar(255) DEFAULT NULL,
  `infra_rank` varchar(255) DEFAULT NULL,
  `infra_epithet` varchar(255) DEFAULT NULL,
  `author` varchar(255) DEFAULT NULL,
  `TPL_status` varchar(255) DEFAULT NULL,
  `original_status` varchar(255) DEFAULT NULL,
  `source` varchar(255) DEFAULT NULL,
  `source_id` varchar(255) DEFAULT NULL,
  `IPNI_id` varchar(255) DEFAULT NULL,
  `publication` varchar(255) DEFAULT NULL,
  `pub_collation` varchar(255) DEFAULT NULL,
  `pub_page` varchar(255) DEFAULT NULL,
  `pub_date` varchar(255) DEFAULT NULL,
  `confidence__tmp` varchar(512) DEFAULT NULL,
  `confidence` varchar(512) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=597067 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `plugin_wiki_attachment`
--

DROP TABLE IF EXISTS `plugin_wiki_attachment`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `plugin_wiki_attachment` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `tablename` varchar(255) DEFAULT NULL,
  `record_id` int(11) DEFAULT NULL,
  `name` varchar(255) DEFAULT NULL,
  `file` varchar(255) DEFAULT NULL,
  `created_by` int(11) DEFAULT NULL,
  `created_on` datetime DEFAULT NULL,
  `modified_by` int(11) DEFAULT NULL,
  `modified_on` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `created_by__idx` (`created_by`),
  KEY `modified_by__idx` (`modified_by`),
  CONSTRAINT `plugin_wiki_attachment_ibfk_1` FOREIGN KEY (`created_by`) REFERENCES `auth_user` (`id`) ON DELETE CASCADE,
  CONSTRAINT `plugin_wiki_attachment_ibfk_2` FOREIGN KEY (`modified_by`) REFERENCES `auth_user` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `plugin_wiki_comment`
--

DROP TABLE IF EXISTS `plugin_wiki_comment`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `plugin_wiki_comment` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `tablename` varchar(255) DEFAULT NULL,
  `record_id` int(11) DEFAULT NULL,
  `body` varchar(255) DEFAULT NULL,
  `created_by` int(11) DEFAULT NULL,
  `created_on` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `created_by__idx` (`created_by`),
  CONSTRAINT `plugin_wiki_comment_ibfk_1` FOREIGN KEY (`created_by`) REFERENCES `auth_user` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `plugin_wiki_link`
--

DROP TABLE IF EXISTS `plugin_wiki_link`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `plugin_wiki_link` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `tag` int(11) DEFAULT NULL,
  `table_name` varchar(255) DEFAULT NULL,
  `record_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `tag__idx` (`tag`),
  CONSTRAINT `plugin_wiki_link_ibfk_1` FOREIGN KEY (`tag`) REFERENCES `plugin_wiki_tag` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `plugin_wiki_page`
--

DROP TABLE IF EXISTS `plugin_wiki_page`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `plugin_wiki_page` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `slug` varchar(255) DEFAULT NULL,
  `title` varchar(255) DEFAULT NULL,
  `active` char(1) DEFAULT NULL,
  `public` char(1) DEFAULT NULL,
  `body` longtext,
  `role` int(11) DEFAULT NULL,
  `changelog` varchar(255) DEFAULT NULL,
  `created_by` int(11) DEFAULT NULL,
  `created_on` datetime DEFAULT NULL,
  `modified_by` int(11) DEFAULT NULL,
  `modified_on` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `role__idx` (`role`),
  KEY `created_by__idx` (`created_by`),
  KEY `modified_by__idx` (`modified_by`),
  CONSTRAINT `plugin_wiki_page_ibfk_1` FOREIGN KEY (`role`) REFERENCES `auth_group` (`id`) ON DELETE CASCADE,
  CONSTRAINT `plugin_wiki_page_ibfk_2` FOREIGN KEY (`created_by`) REFERENCES `auth_user` (`id`) ON DELETE CASCADE,
  CONSTRAINT `plugin_wiki_page_ibfk_3` FOREIGN KEY (`modified_by`) REFERENCES `auth_user` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `plugin_wiki_page_archive`
--

DROP TABLE IF EXISTS `plugin_wiki_page_archive`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `plugin_wiki_page_archive` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `current_record` int(11) DEFAULT NULL,
  `slug` varchar(255) DEFAULT NULL,
  `title` varchar(255) DEFAULT NULL,
  `active` char(1) DEFAULT NULL,
  `public` char(1) DEFAULT NULL,
  `body` longtext,
  `role` int(11) DEFAULT NULL,
  `changelog` varchar(255) DEFAULT NULL,
  `created_by` int(11) DEFAULT NULL,
  `created_on` datetime DEFAULT NULL,
  `modified_by` int(11) DEFAULT NULL,
  `modified_on` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `current_record__idx` (`current_record`),
  KEY `role__idx` (`role`),
  KEY `created_by__idx` (`created_by`),
  KEY `modified_by__idx` (`modified_by`),
  CONSTRAINT `plugin_wiki_page_archive_ibfk_1` FOREIGN KEY (`current_record`) REFERENCES `plugin_wiki_page` (`id`) ON DELETE CASCADE,
  CONSTRAINT `plugin_wiki_page_archive_ibfk_2` FOREIGN KEY (`role`) REFERENCES `auth_group` (`id`) ON DELETE CASCADE,
  CONSTRAINT `plugin_wiki_page_archive_ibfk_3` FOREIGN KEY (`created_by`) REFERENCES `auth_user` (`id`) ON DELETE CASCADE,
  CONSTRAINT `plugin_wiki_page_archive_ibfk_4` FOREIGN KEY (`modified_by`) REFERENCES `auth_user` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `plugin_wiki_tag`
--

DROP TABLE IF EXISTS `plugin_wiki_tag`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `plugin_wiki_tag` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(255) DEFAULT NULL,
  `links` int(11) DEFAULT NULL,
  `created_by` int(11) DEFAULT NULL,
  `created_on` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `created_by__idx` (`created_by`),
  CONSTRAINT `plugin_wiki_tag_ibfk_1` FOREIGN KEY (`created_by`) REFERENCES `auth_user` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `prune_detail`
--

DROP TABLE IF EXISTS `prune_detail`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `prune_detail` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `pruned_gnode` int(11) DEFAULT NULL,
  `gtree_edit` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `pruned_gnode__idx` (`pruned_gnode`),
  KEY `gtree_edit__idx` (`gtree_edit`),
  CONSTRAINT `prune_detail_ibfk_1` FOREIGN KEY (`pruned_gnode`) REFERENCES `gnode` (`id`) ON DELETE CASCADE,
  CONSTRAINT `prune_detail_ibfk_2` FOREIGN KEY (`gtree_edit`) REFERENCES `gtree_edit` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=6524 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `sequence`
--

DROP TABLE IF EXISTS `sequence`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `sequence` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `otu` int(11) DEFAULT NULL,
  `gene` int(11) DEFAULT NULL,
  `data` longtext,
  `ac` varchar(255) DEFAULT NULL,
  `gi` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `otu__idx` (`otu`),
  KEY `gene__idx` (`gene`),
  CONSTRAINT `sequence_ibfk_1` FOREIGN KEY (`otu`) REFERENCES `otu` (`id`) ON DELETE NO ACTION,
  CONSTRAINT `sequence_ibfk_2` FOREIGN KEY (`gene`) REFERENCES `gene` (`id`) ON DELETE NO ACTION
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `snode`
--

DROP TABLE IF EXISTS `snode`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `snode` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `label` varchar(128) DEFAULT NULL,
  `otu` int(11) DEFAULT NULL,
  `taxon` int(11) DEFAULT NULL,
  `ottol_name` int(11) DEFAULT NULL,
  `ingroup` char(1) NOT NULL DEFAULT 'F',
  `isleaf` char(1) NOT NULL DEFAULT 'F',
  `parent` int(11) DEFAULT NULL,
  `next` int(11) DEFAULT NULL,
  `back` int(11) DEFAULT NULL,
  `depth` int(11) DEFAULT NULL,
  `length` double DEFAULT NULL,
  `age` double DEFAULT NULL,
  `age_min` double DEFAULT NULL,
  `age_max` double DEFAULT NULL,
  `bootstrap_support` double DEFAULT NULL,
  `posterior_support` double DEFAULT NULL,
  `other_support` double DEFAULT NULL,
  `other_support_type` varchar(255) DEFAULT NULL,
  `tree` int(11) DEFAULT NULL,
  `pruned` char(1) NOT NULL DEFAULT 'F',
  `mtime` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `otu__idx` (`otu`),
  KEY `taxon__idx` (`taxon`),
  KEY `parent__idx` (`parent`),
  KEY `tree__idx` (`tree`),
  KEY `treeNodeLengths` (`tree`,`length`),
  KEY `treeNext` (`tree`,`next`),
  KEY `ottolIndex` (`ottol_name`),
  CONSTRAINT `snode_ibfk_5` FOREIGN KEY (`otu`) REFERENCES `otu` (`id`) ON DELETE SET NULL,
  CONSTRAINT `snode_ibfk_6` FOREIGN KEY (`taxon`) REFERENCES `taxon` (`id`) ON DELETE SET NULL,
  CONSTRAINT `snode_ibfk_7` FOREIGN KEY (`parent`) REFERENCES `snode` (`id`) ON DELETE SET NULL,
  CONSTRAINT `snode_ibfk_8` FOREIGN KEY (`tree`) REFERENCES `stree` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB AUTO_INCREMENT=178233 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `stree`
--

DROP TABLE IF EXISTS `stree`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `stree` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `study` int(11) DEFAULT NULL,
  `uploaded` datetime NOT NULL DEFAULT '2011-02-20 14:19:49',
  `newick` longtext,
  `clade_labels_represent` varchar(255) DEFAULT NULL,
  `clade_labels_comment` longtext,
  `branch_lengths_represent` varchar(255) DEFAULT NULL,
  `branch_lengths_comment` longtext,
  `newick_idstr` longtext,
  `type` varchar(128) NOT NULL,
  `comment` longtext,
  `contributor` varchar(128) NOT NULL,
  `author_contributed` char(1) DEFAULT NULL,
  `tb_tree_id` varchar(128) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `study__idx` (`study`),
  CONSTRAINT `stree_ibfk_1` FOREIGN KEY (`study`) REFERENCES `study` (`id`) ON DELETE NO ACTION
) ENGINE=InnoDB AUTO_INCREMENT=205 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `stree_tag`
--

DROP TABLE IF EXISTS `stree_tag`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `stree_tag` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `tag` varchar(255) NOT NULL,
  `name` varchar(255) DEFAULT NULL,
  `value` varchar(255) DEFAULT NULL,
  `stree` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `stree__idx` (`stree`),
  CONSTRAINT `stree_tag_ibfk_2` FOREIGN KEY (`stree`) REFERENCES `stree` (`id`) ON DELETE NO ACTION
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `study`
--

DROP TABLE IF EXISTS `study`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `study` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `focal_clade` int(11) DEFAULT NULL,
  `focal_clade_ottol` int(11) DEFAULT NULL,
  `citation` varchar(1024) NOT NULL,
  `label` varchar(255) DEFAULT NULL,
  `year_published` int(11) DEFAULT NULL,
  `contributor` varchar(128) NOT NULL,
  `comment` longtext,
  `uploaded` datetime NOT NULL DEFAULT '2011-02-19 11:44:46',
  `treebase_id` int(11) DEFAULT NULL,
  `doi` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `focal_clade__idx` (`focal_clade`),
  KEY `citation` (`citation`(255)),
  KEY `focal_clade_ottol` (`focal_clade_ottol`),
  CONSTRAINT `study_ibfk_1` FOREIGN KEY (`focal_clade`) REFERENCES `taxon` (`id`) ON DELETE NO ACTION
) ENGINE=InnoDB AUTO_INCREMENT=297 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `study_file`
--

DROP TABLE IF EXISTS `study_file`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `study_file` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `study` int(11) DEFAULT NULL,
  `file` varchar(255) DEFAULT NULL,
  `data` longblob,
  `uploaded` datetime NOT NULL DEFAULT '2011-02-21 00:15:28',
  `description` varchar(255) DEFAULT NULL,
  `source` varchar(255) DEFAULT NULL,
  `filename` varchar(255) DEFAULT NULL,
  `contributor` varchar(128) NOT NULL,
  `comment` longtext,
  PRIMARY KEY (`id`),
  KEY `study__idx` (`study`),
  CONSTRAINT `study_file_ibfk_1` FOREIGN KEY (`study`) REFERENCES `study` (`id`) ON DELETE NO ACTION
) ENGINE=InnoDB AUTO_INCREMENT=358 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `study_tag`
--

DROP TABLE IF EXISTS `study_tag`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `study_tag` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `tag` varchar(255) NOT NULL,
  `name` varchar(255) DEFAULT NULL,
  `value` varchar(255) DEFAULT NULL,
  `study` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `study__idx` (`study`),
  CONSTRAINT `study_tag_ibfk_2` FOREIGN KEY (`study`) REFERENCES `study` (`id`) ON DELETE NO ACTION
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `taxon`
--

DROP TABLE IF EXISTS `taxon`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `taxon` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `apg_taxon` int(11) DEFAULT NULL,
  `name` varchar(255) NOT NULL,
  `rank` varchar(255) DEFAULT NULL,
  `ncbi_taxid` int(11) DEFAULT NULL,
  `namebank_id` int(11) DEFAULT NULL,
  `tb_taxid` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `apg_taxon__idx` (`apg_taxon`),
  KEY `ncbi_taxid` (`ncbi_taxid`),
  KEY `name` (`name`),
  CONSTRAINT `taxon_ibfk_2` FOREIGN KEY (`apg_taxon`) REFERENCES `apg_taxon` (`id`) ON DELETE NO ACTION,
  CONSTRAINT `taxon_ibfk_3` FOREIGN KEY (`ncbi_taxid`) REFERENCES `ncbi_node` (`taxid`) ON DELETE NO ACTION
) ENGINE=InnoDB AUTO_INCREMENT=137239 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `taxon_copy`
--

DROP TABLE IF EXISTS `taxon_copy`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `taxon_copy` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `parent` int(11) DEFAULT NULL,
  `ncbi_taxon` int(11) DEFAULT NULL,
  `apg_taxon` int(11) DEFAULT NULL,
  `name` varchar(255) NOT NULL,
  `rank` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `ncbi_taxon__idx` (`ncbi_taxon`),
  KEY `apg_taxon__idx` (`apg_taxon`)
) ENGINE=InnoDB AUTO_INCREMENT=33452 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `treeMeta`
--

DROP TABLE IF EXISTS `treeMeta`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `treeMeta` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `tree` int(11) DEFAULT NULL,
  `treeType` varchar(255) DEFAULT NULL,
  `depth` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=191 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `treeMetaDepthDetail`
--

DROP TABLE IF EXISTS `treeMetaDepthDetail`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `treeMetaDepthDetail` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `treeMeta` int(11) DEFAULT NULL,
  `depth` int(11) DEFAULT NULL,
  `nodeCount` double DEFAULT NULL,
  `tipCount` double DEFAULT NULL,
  `longestlabel` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `treeMeta__idx` (`treeMeta`),
  CONSTRAINT `treeMetaDepthDetail_ibfk_1` FOREIGN KEY (`treeMeta`) REFERENCES `treeMeta` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=5995 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `treebase_matrix`
--

DROP TABLE IF EXISTS `treebase_matrix`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `treebase_matrix` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `study` int(11) DEFAULT NULL,
  `label` varchar(255) DEFAULT NULL,
  `type` varchar(255) DEFAULT NULL,
  `nchar` int(11) DEFAULT NULL,
  `ntax` int(11) DEFAULT NULL,
  `tb_matrix_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `tb_matrix_id` (`tb_matrix_id`),
  KEY `study__idx` (`study`),
  CONSTRAINT `treebase_matrix_ibfk_1` FOREIGN KEY (`study`) REFERENCES `study` (`id`) ON DELETE NO ACTION
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `treebase_matrix_row`
--

DROP TABLE IF EXISTS `treebase_matrix_row`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `treebase_matrix_row` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `otu` int(11) DEFAULT NULL,
  `data` longtext NOT NULL,
  PRIMARY KEY (`id`),
  KEY `otu__idx` (`otu`),
  CONSTRAINT `treebase_matrix_row_ibfk_1` FOREIGN KEY (`otu`) REFERENCES `otu` (`id`) ON DELETE NO ACTION
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `unique_user`
--

DROP TABLE IF EXISTS `unique_user`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `unique_user` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `first_name` varchar(255) DEFAULT NULL,
  `last_name` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=34 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `userEdit`
--

DROP TABLE IF EXISTS `userEdit`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `userEdit` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `username` varchar(200) DEFAULT NULL,
  `timestamp` datetime DEFAULT NULL,
  `tableName` varchar(100) DEFAULT NULL,
  `rowId` int(11) DEFAULT NULL,
  `fieldName` varchar(100) DEFAULT NULL,
  `previousValue` longtext,
  `updatedValue` longtext,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=60 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `user_map`
--

DROP TABLE IF EXISTS `user_map`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `user_map` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `auth_user_id` int(11) DEFAULT NULL,
  `unique_user_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `auth_user_id__idx` (`auth_user_id`),
  KEY `unique_user_id__idx` (`unique_user_id`),
  CONSTRAINT `user_map_ibfk_1` FOREIGN KEY (`auth_user_id`) REFERENCES `auth_user` (`id`) ON DELETE CASCADE,
  CONSTRAINT `user_map_ibfk_2` FOREIGN KEY (`unique_user_id`) REFERENCES `unique_user` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=45 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2013-01-31 11:44:10
