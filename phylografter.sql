-- phpMyAdmin SQL Dump
-- version 4.0.6
-- http://www.phpmyadmin.net
--
-- Host: localhost
-- Generation Time: Oct 04, 2013 at 03:40 PM
-- Server version: 5.6.13
-- PHP Version: 5.5.4

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;

--
-- Database: `phylografter`
--

-- --------------------------------------------------------

--
-- Table structure for table `apg_taxon`
--

CREATE TABLE IF NOT EXISTS `apg_taxon` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `parent` int(11) DEFAULT NULL,
  `next` int(11) DEFAULT NULL,
  `back` int(11) DEFAULT NULL,
  `depth` int(11) DEFAULT NULL,
  `name` varchar(255) NOT NULL,
  `rank` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB  DEFAULT CHARSET=utf8 AUTO_INCREMENT=29037 ;

-- --------------------------------------------------------

--
-- Table structure for table `auth_cas`
--

CREATE TABLE IF NOT EXISTS `auth_cas` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) DEFAULT NULL,
  `uuid` varchar(255) DEFAULT NULL,
  `url` varchar(255) DEFAULT NULL,
  `created_on` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `user_id__idx` (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 AUTO_INCREMENT=1 ;

-- --------------------------------------------------------

--
-- Table structure for table `auth_event`
--

CREATE TABLE IF NOT EXISTS `auth_event` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `time_stamp` datetime DEFAULT NULL,
  `user_id` int(11) DEFAULT NULL,
  `description` longtext,
  `origin` varchar(255) DEFAULT NULL,
  `client_ip` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `user_id__idx` (`user_id`)
) ENGINE=InnoDB  DEFAULT CHARSET=utf8 AUTO_INCREMENT=2279 ;

-- --------------------------------------------------------

--
-- Table structure for table `auth_group`
--

CREATE TABLE IF NOT EXISTS `auth_group` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `description` longtext,
  `role` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB  DEFAULT CHARSET=utf8 AUTO_INCREMENT=59 ;

-- --------------------------------------------------------

--
-- Table structure for table `auth_membership`
--

CREATE TABLE IF NOT EXISTS `auth_membership` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) DEFAULT NULL,
  `group_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `user_id__idx` (`user_id`),
  KEY `group_id__idx` (`group_id`)
) ENGINE=InnoDB  DEFAULT CHARSET=utf8 AUTO_INCREMENT=90 ;

-- --------------------------------------------------------

--
-- Table structure for table `auth_permission`
--

CREATE TABLE IF NOT EXISTS `auth_permission` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `group_id` int(11) DEFAULT NULL,
  `record_id` int(11) DEFAULT NULL,
  `table_name` varchar(255) DEFAULT NULL,
  `name` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `group_id__idx` (`group_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 AUTO_INCREMENT=1 ;

-- --------------------------------------------------------

--
-- Table structure for table `auth_user`
--

CREATE TABLE IF NOT EXISTS `auth_user` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `reset_password_key` varchar(255) DEFAULT NULL,
  `password` varchar(255) DEFAULT NULL,
  `registration_key` varchar(255) DEFAULT NULL,
  `email` varchar(255) DEFAULT NULL,
  `first_name` varchar(128) DEFAULT NULL,
  `last_name` varchar(128) DEFAULT NULL,
  `registration_id` varchar(512) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB  DEFAULT CHARSET=utf8 AUTO_INCREMENT=57 ;

-- --------------------------------------------------------

--
-- Table structure for table `clipboard`
--

CREATE TABLE IF NOT EXISTS `clipboard` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `nodeId` int(11) DEFAULT NULL,
  `name` varchar(255) DEFAULT NULL,
  `creationDate` datetime DEFAULT NULL,
  `treetype` varchar(255) DEFAULT NULL,
  `user` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `nodeId__idx` (`nodeId`)
) ENGINE=InnoDB  DEFAULT CHARSET=utf8 AUTO_INCREMENT=77 ;

-- --------------------------------------------------------

--
-- Table structure for table `gene`
--

CREATE TABLE IF NOT EXISTS `gene` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  `genome` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 AUTO_INCREMENT=1 ;

-- --------------------------------------------------------

--
-- Table structure for table `gnode`
--

CREATE TABLE IF NOT EXISTS `gnode` (
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
  KEY `parent__idx` (`parent`)
) ENGINE=InnoDB  DEFAULT CHARSET=utf8 AUTO_INCREMENT=118615 ;

-- --------------------------------------------------------

--
-- Table structure for table `gtree`
--

CREATE TABLE IF NOT EXISTS `gtree` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `contributor` varchar(128) DEFAULT NULL,
  `mtime` datetime DEFAULT NULL,
  `title` varchar(255) DEFAULT NULL,
  `comment` longtext,
  `date` datetime DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB  DEFAULT CHARSET=utf8 AUTO_INCREMENT=366 ;

-- --------------------------------------------------------

--
-- Table structure for table `gtree_edit`
--

CREATE TABLE IF NOT EXISTS `gtree_edit` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `gtree` int(11) DEFAULT NULL,
  `action` varchar(255) DEFAULT NULL,
  `target_gnode` int(11) DEFAULT NULL,
  `source_node` int(11) DEFAULT NULL,
  `comment` longtext,
  `mtime` datetime DEFAULT NULL,
  `user` int(11) DEFAULT NULL,
  `affected_node_id` int(11) DEFAULT NULL,
  `affected_clade_id` int(11) DEFAULT NULL,
  `clipboard_node` int(11) DEFAULT NULL,
  `originaltreetype` varchar(255) DEFAULT NULL,
  `clipboard_node__tmp` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `gtree__idx` (`gtree`),
  KEY `target_gnode__idx` (`target_gnode`),
  KEY `source_node__idx` (`source_node`),
  KEY `user__idx` (`user`),
  KEY `clipboard_node__idx` (`clipboard_node`)
) ENGINE=InnoDB  DEFAULT CHARSET=utf8 AUTO_INCREMENT=437 ;

-- --------------------------------------------------------

--
-- Table structure for table `gtree_share`
--

CREATE TABLE IF NOT EXISTS `gtree_share` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user` int(11) DEFAULT NULL,
  `gtree` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `user__idx` (`user`),
  KEY `gtree__idx` (`gtree`)
) ENGINE=InnoDB  DEFAULT CHARSET=utf8 AUTO_INCREMENT=11 ;

-- --------------------------------------------------------

--
-- Table structure for table `ncbi_name`
--

CREATE TABLE IF NOT EXISTS `ncbi_name` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `taxid` int(11) NOT NULL,
  `name` varchar(255) DEFAULT NULL,
  `unique_name` varchar(255) DEFAULT NULL,
  `name_class` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `unique_name` (`unique_name`),
  KEY `taxid` (`taxid`)
) ENGINE=InnoDB  DEFAULT CHARSET=utf8 AUTO_INCREMENT=234995 ;

-- --------------------------------------------------------

--
-- Table structure for table `ncbi_node`
--

CREATE TABLE IF NOT EXISTS `ncbi_node` (
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
) ENGINE=InnoDB  DEFAULT CHARSET=utf8 AUTO_INCREMENT=119054 ;

-- --------------------------------------------------------

--
-- Table structure for table `ncbi_taxon`
--

CREATE TABLE IF NOT EXISTS `ncbi_taxon` (
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
) ENGINE=InnoDB  DEFAULT CHARSET=utf8 AUTO_INCREMENT=30493 ;

-- --------------------------------------------------------

--
-- Table structure for table `ottol_name`
--

CREATE TABLE IF NOT EXISTS `ottol_name` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `uid` int(10) unsigned DEFAULT NULL,
  `parent_uid` int(10) unsigned DEFAULT NULL,
  `accepted_uid` int(10) unsigned DEFAULT NULL,
  `next` int(10) unsigned DEFAULT NULL,
  `back` int(10) unsigned DEFAULT NULL,
  `preottol_taxid` bigint(11) unsigned DEFAULT NULL,
  `preottol_parent_taxid` bigint(11) unsigned DEFAULT NULL,
  `preottol_source` varchar(64) DEFAULT NULL,
  `preottol_source_taxid` varchar(64) DEFAULT NULL,
  `ncbi_taxid` int(11) unsigned DEFAULT NULL,
  `gbif_taxid` int(10) unsigned DEFAULT NULL,
  `treebase_taxid` int(11) DEFAULT NULL,
  `namebank_taxid` int(11) DEFAULT NULL,
  `name` varchar(255) NOT NULL,
  `unique_name` varchar(255) DEFAULT NULL,
  `rank` varchar(255) DEFAULT NULL,
  `comments` varchar(255) DEFAULT NULL,
  `mtime` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `preottol_taxid` (`preottol_taxid`),
  KEY `name` (`name`),
  KEY `unique_name` (`unique_name`),
  KEY `gbif_taxid` (`gbif_taxid`),
  KEY `uid` (`uid`),
  KEY `accepted_uid` (`accepted_uid`),
  KEY `parent_uid` (`parent_uid`),
  KEY `nextback` (`next`,`back`)
) ENGINE=InnoDB  DEFAULT CHARSET=utf8 AUTO_INCREMENT=7066018 ;

-- --------------------------------------------------------

--
-- Table structure for table `ottol_node`
--

CREATE TABLE IF NOT EXISTS `ottol_node` (
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
) ENGINE=InnoDB DEFAULT CHARSET=utf8 AUTO_INCREMENT=1 ;

-- --------------------------------------------------------

--
-- Table structure for table `otu`
--

CREATE TABLE IF NOT EXISTS `otu` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `study` int(11) DEFAULT NULL,
  `label` varchar(255) NOT NULL,
  `taxon` int(11) DEFAULT NULL,
  `ottol_name` int(11) unsigned DEFAULT NULL,
  `tb_nexml_id` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `study__idx` (`study`),
  KEY `taxon__idx` (`taxon`),
  KEY `ottol_name` (`ottol_name`)
) ENGINE=InnoDB  DEFAULT CHARSET=utf8 AUTO_INCREMENT=394780 ;

-- --------------------------------------------------------

--
-- Table structure for table `phylogramNodeMeta`
--

CREATE TABLE IF NOT EXISTS `phylogramNodeMeta` (
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
) ENGINE=InnoDB  DEFAULT CHARSET=utf8 AUTO_INCREMENT=859982 ;

-- --------------------------------------------------------

--
-- Table structure for table `plantlist`
--

CREATE TABLE IF NOT EXISTS `plantlist` (
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
) ENGINE=InnoDB  DEFAULT CHARSET=utf8 AUTO_INCREMENT=597067 ;

-- --------------------------------------------------------

--
-- Table structure for table `plugin_wiki_attachment`
--

CREATE TABLE IF NOT EXISTS `plugin_wiki_attachment` (
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
  KEY `modified_by__idx` (`modified_by`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 AUTO_INCREMENT=1 ;

-- --------------------------------------------------------

--
-- Table structure for table `plugin_wiki_comment`
--

CREATE TABLE IF NOT EXISTS `plugin_wiki_comment` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `tablename` varchar(255) DEFAULT NULL,
  `record_id` int(11) DEFAULT NULL,
  `body` varchar(255) DEFAULT NULL,
  `created_by` int(11) DEFAULT NULL,
  `created_on` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `created_by__idx` (`created_by`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 AUTO_INCREMENT=1 ;

-- --------------------------------------------------------

--
-- Table structure for table `plugin_wiki_link`
--

CREATE TABLE IF NOT EXISTS `plugin_wiki_link` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `tag` int(11) DEFAULT NULL,
  `table_name` varchar(255) DEFAULT NULL,
  `record_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `tag__idx` (`tag`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 AUTO_INCREMENT=1 ;

-- --------------------------------------------------------

--
-- Table structure for table `plugin_wiki_page`
--

CREATE TABLE IF NOT EXISTS `plugin_wiki_page` (
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
  KEY `modified_by__idx` (`modified_by`)
) ENGINE=InnoDB  DEFAULT CHARSET=utf8 AUTO_INCREMENT=2 ;

-- --------------------------------------------------------

--
-- Table structure for table `plugin_wiki_page_archive`
--

CREATE TABLE IF NOT EXISTS `plugin_wiki_page_archive` (
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
  KEY `modified_by__idx` (`modified_by`)
) ENGINE=InnoDB  DEFAULT CHARSET=utf8 AUTO_INCREMENT=2 ;

-- --------------------------------------------------------

--
-- Table structure for table `plugin_wiki_tag`
--

CREATE TABLE IF NOT EXISTS `plugin_wiki_tag` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(255) DEFAULT NULL,
  `links` int(11) DEFAULT NULL,
  `created_by` int(11) DEFAULT NULL,
  `created_on` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `created_by__idx` (`created_by`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 AUTO_INCREMENT=1 ;

-- --------------------------------------------------------

--
-- Table structure for table `prune_detail`
--

CREATE TABLE IF NOT EXISTS `prune_detail` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `pruned_gnode` int(11) DEFAULT NULL,
  `gtree_edit` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `pruned_gnode__idx` (`pruned_gnode`),
  KEY `gtree_edit__idx` (`gtree_edit`)
) ENGINE=InnoDB  DEFAULT CHARSET=utf8 AUTO_INCREMENT=67 ;

-- --------------------------------------------------------

--
-- Table structure for table `sequence`
--

CREATE TABLE IF NOT EXISTS `sequence` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `otu` int(11) DEFAULT NULL,
  `gene` int(11) DEFAULT NULL,
  `data` longtext,
  `ac` varchar(255) DEFAULT NULL,
  `gi` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `otu__idx` (`otu`),
  KEY `gene__idx` (`gene`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 AUTO_INCREMENT=1 ;

-- --------------------------------------------------------

--
-- Table structure for table `snode`
--

CREATE TABLE IF NOT EXISTS `snode` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `label` varchar(128) DEFAULT NULL,
  `otu` int(11) DEFAULT NULL,
  `ottol_name` int(11) unsigned DEFAULT NULL,
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
  KEY `parent__idx` (`parent`),
  KEY `tree__idx` (`tree`),
  KEY `treeNodeLengths` (`tree`,`length`),
  KEY `treeNext` (`tree`,`next`),
  KEY `ottol_name` (`ottol_name`)
) ENGINE=InnoDB  DEFAULT CHARSET=utf8 AUTO_INCREMENT=1054856 ;

-- --------------------------------------------------------

--
-- Table structure for table `stree`
--

CREATE TABLE IF NOT EXISTS `stree` (
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
  `last_modified` timestamp NULL DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `study__idx` (`study`),
  KEY `last_modified` (`last_modified`)
) ENGINE=InnoDB  DEFAULT CHARSET=utf8 AUTO_INCREMENT=6176 ;

-- --------------------------------------------------------

--
-- Table structure for table `stree_tag`
--

CREATE TABLE IF NOT EXISTS `stree_tag` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `tag` varchar(255) NOT NULL,
  `name` varchar(255) DEFAULT NULL,
  `value` varchar(255) DEFAULT NULL,
  `stree` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `stree__idx` (`stree`)
) ENGINE=InnoDB  DEFAULT CHARSET=utf8 AUTO_INCREMENT=4463 ;

-- --------------------------------------------------------

--
-- Table structure for table `study`
--

CREATE TABLE IF NOT EXISTS `study` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `focal_clade` int(11) DEFAULT NULL,
  `focal_clade_ottol` int(11) unsigned DEFAULT NULL,
  `citation` varchar(1024) NOT NULL,
  `label` varchar(255) DEFAULT NULL,
  `year_published` int(11) DEFAULT NULL,
  `contributor` varchar(128) NOT NULL,
  `comment` longtext,
  `uploaded` datetime NOT NULL DEFAULT '2011-02-19 11:44:46',
  `treebase_id` int(11) DEFAULT NULL,
  `doi` varchar(255) DEFAULT NULL,
  `last_modified` timestamp NULL DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `focal_clade__idx` (`focal_clade`),
  KEY `citation` (`citation`(255)),
  KEY `focal_clade_ottol` (`focal_clade_ottol`),
  KEY `last_modified` (`last_modified`)
) ENGINE=InnoDB  DEFAULT CHARSET=utf8 AUTO_INCREMENT=2651 ;

-- --------------------------------------------------------

--
-- Table structure for table `study_file`
--

CREATE TABLE IF NOT EXISTS `study_file` (
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
  KEY `study__idx` (`study`)
) ENGINE=InnoDB  DEFAULT CHARSET=utf8 AUTO_INCREMENT=1689 ;

-- --------------------------------------------------------

--
-- Table structure for table `study_tag`
--

CREATE TABLE IF NOT EXISTS `study_tag` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `tag` varchar(255) NOT NULL,
  `name` varchar(255) DEFAULT NULL,
  `value` varchar(255) DEFAULT NULL,
  `study` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `study__idx` (`study`)
) ENGINE=InnoDB  DEFAULT CHARSET=utf8 AUTO_INCREMENT=4343 ;

-- --------------------------------------------------------

--
-- Table structure for table `taxon`
--

CREATE TABLE IF NOT EXISTS `taxon` (
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
  KEY `name` (`name`)
) ENGINE=InnoDB  DEFAULT CHARSET=utf8 AUTO_INCREMENT=137239 ;

-- --------------------------------------------------------

--
-- Table structure for table `taxon_copy`
--

CREATE TABLE IF NOT EXISTS `taxon_copy` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `parent` int(11) DEFAULT NULL,
  `ncbi_taxon` int(11) DEFAULT NULL,
  `apg_taxon` int(11) DEFAULT NULL,
  `name` varchar(255) NOT NULL,
  `rank` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `ncbi_taxon__idx` (`ncbi_taxon`),
  KEY `apg_taxon__idx` (`apg_taxon`)
) ENGINE=InnoDB  DEFAULT CHARSET=utf8 AUTO_INCREMENT=33452 ;

-- --------------------------------------------------------

--
-- Table structure for table `treebase_matrix`
--

CREATE TABLE IF NOT EXISTS `treebase_matrix` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `study` int(11) DEFAULT NULL,
  `label` varchar(255) DEFAULT NULL,
  `type` varchar(255) DEFAULT NULL,
  `nchar` int(11) DEFAULT NULL,
  `ntax` int(11) DEFAULT NULL,
  `tb_matrix_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `tb_matrix_id` (`tb_matrix_id`),
  KEY `study__idx` (`study`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 AUTO_INCREMENT=1 ;

-- --------------------------------------------------------

--
-- Table structure for table `treebase_matrix_row`
--

CREATE TABLE IF NOT EXISTS `treebase_matrix_row` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `otu` int(11) DEFAULT NULL,
  `data` longtext NOT NULL,
  PRIMARY KEY (`id`),
  KEY `otu__idx` (`otu`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 AUTO_INCREMENT=1 ;

-- --------------------------------------------------------

--
-- Table structure for table `treeMeta`
--

CREATE TABLE IF NOT EXISTS `treeMeta` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `tree` int(11) DEFAULT NULL,
  `treeType` varchar(255) DEFAULT NULL,
  `depth` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB  DEFAULT CHARSET=utf8 AUTO_INCREMENT=191 ;

-- --------------------------------------------------------

--
-- Table structure for table `treeMetaDepthDetail`
--

CREATE TABLE IF NOT EXISTS `treeMetaDepthDetail` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `treeMeta` int(11) DEFAULT NULL,
  `depth` int(11) DEFAULT NULL,
  `nodeCount` double DEFAULT NULL,
  `tipCount` double DEFAULT NULL,
  `longestlabel` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `treeMeta__idx` (`treeMeta`)
) ENGINE=InnoDB  DEFAULT CHARSET=utf8 AUTO_INCREMENT=5995 ;

-- --------------------------------------------------------

--
-- Table structure for table `unique_user`
--

CREATE TABLE IF NOT EXISTS `unique_user` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `first_name` varchar(255) DEFAULT NULL,
  `last_name` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB  DEFAULT CHARSET=utf8 AUTO_INCREMENT=34 ;

-- --------------------------------------------------------

--
-- Table structure for table `userEdit`
--

CREATE TABLE IF NOT EXISTS `userEdit` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `username` varchar(200) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `timestamp` datetime DEFAULT NULL,
  `tableName` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `rowId` int(11) DEFAULT NULL,
  `fieldName` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `previousValue` longtext COLLATE utf8mb4_unicode_ci,
  `updatedValue` longtext COLLATE utf8mb4_unicode_ci,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB  DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci AUTO_INCREMENT=15566 ;

-- --------------------------------------------------------

--
-- Table structure for table `user_map`
--

CREATE TABLE IF NOT EXISTS `user_map` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `auth_user_id` int(11) DEFAULT NULL,
  `unique_user_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `auth_user_id__idx` (`auth_user_id`),
  KEY `unique_user_id__idx` (`unique_user_id`)
) ENGINE=InnoDB  DEFAULT CHARSET=utf8 AUTO_INCREMENT=45 ;

--
-- Constraints for dumped tables
--

--
-- Constraints for table `auth_cas`
--
ALTER TABLE `auth_cas`
  ADD CONSTRAINT `auth_cas_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`) ON DELETE CASCADE;

--
-- Constraints for table `auth_event`
--
ALTER TABLE `auth_event`
  ADD CONSTRAINT `auth_event_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`) ON DELETE CASCADE;

--
-- Constraints for table `auth_membership`
--
ALTER TABLE `auth_membership`
  ADD CONSTRAINT `auth_membership_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `auth_membership_ibfk_2` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`) ON DELETE CASCADE;

--
-- Constraints for table `auth_permission`
--
ALTER TABLE `auth_permission`
  ADD CONSTRAINT `auth_permission_ibfk_1` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`) ON DELETE CASCADE;

--
-- Constraints for table `gnode`
--
ALTER TABLE `gnode`
  ADD CONSTRAINT `gnode_ibfk_4` FOREIGN KEY (`parent`) REFERENCES `gnode` (`id`) ON DELETE NO ACTION,
  ADD CONSTRAINT `gnode_ibfk_5` FOREIGN KEY (`parent`) REFERENCES `gnode` (`id`) ON DELETE NO ACTION;

--
-- Constraints for table `gtree_edit`
--
ALTER TABLE `gtree_edit`
  ADD CONSTRAINT `gtree_edit_ibfk_1` FOREIGN KEY (`gtree`) REFERENCES `gtree` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `gtree_edit_ibfk_2` FOREIGN KEY (`target_gnode`) REFERENCES `gnode` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `gtree_edit_ibfk_3` FOREIGN KEY (`source_node`) REFERENCES `snode` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `gtree_edit_ibfk_4` FOREIGN KEY (`user`) REFERENCES `auth_user` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `gtree_edit_ibfk_5` FOREIGN KEY (`clipboard_node`) REFERENCES `snode` (`id`) ON DELETE CASCADE;

--
-- Constraints for table `gtree_share`
--
ALTER TABLE `gtree_share`
  ADD CONSTRAINT `gtree_share_ibfk_1` FOREIGN KEY (`user`) REFERENCES `unique_user` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `gtree_share_ibfk_2` FOREIGN KEY (`gtree`) REFERENCES `gtree` (`id`) ON DELETE CASCADE;

--
-- Constraints for table `ncbi_name`
--
ALTER TABLE `ncbi_name`
  ADD CONSTRAINT `ncbi_name_ibfk_1` FOREIGN KEY (`taxid`) REFERENCES `ncbi_node` (`taxid`) ON DELETE NO ACTION;

--
-- Constraints for table `otu`
--
ALTER TABLE `otu`
  ADD CONSTRAINT `otu_ibfk_1` FOREIGN KEY (`study`) REFERENCES `study` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `otu_ibfk_2` FOREIGN KEY (`ottol_name`) REFERENCES `ottol_name` (`id`) ON DELETE SET NULL;

--
-- Constraints for table `plugin_wiki_attachment`
--
ALTER TABLE `plugin_wiki_attachment`
  ADD CONSTRAINT `plugin_wiki_attachment_ibfk_1` FOREIGN KEY (`created_by`) REFERENCES `auth_user` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `plugin_wiki_attachment_ibfk_2` FOREIGN KEY (`modified_by`) REFERENCES `auth_user` (`id`) ON DELETE CASCADE;

--
-- Constraints for table `plugin_wiki_comment`
--
ALTER TABLE `plugin_wiki_comment`
  ADD CONSTRAINT `plugin_wiki_comment_ibfk_1` FOREIGN KEY (`created_by`) REFERENCES `auth_user` (`id`) ON DELETE CASCADE;

--
-- Constraints for table `plugin_wiki_link`
--
ALTER TABLE `plugin_wiki_link`
  ADD CONSTRAINT `plugin_wiki_link_ibfk_1` FOREIGN KEY (`tag`) REFERENCES `plugin_wiki_tag` (`id`) ON DELETE CASCADE;

--
-- Constraints for table `plugin_wiki_page`
--
ALTER TABLE `plugin_wiki_page`
  ADD CONSTRAINT `plugin_wiki_page_ibfk_1` FOREIGN KEY (`role`) REFERENCES `auth_group` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `plugin_wiki_page_ibfk_2` FOREIGN KEY (`created_by`) REFERENCES `auth_user` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `plugin_wiki_page_ibfk_3` FOREIGN KEY (`modified_by`) REFERENCES `auth_user` (`id`) ON DELETE CASCADE;

--
-- Constraints for table `plugin_wiki_page_archive`
--
ALTER TABLE `plugin_wiki_page_archive`
  ADD CONSTRAINT `plugin_wiki_page_archive_ibfk_1` FOREIGN KEY (`current_record`) REFERENCES `plugin_wiki_page` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `plugin_wiki_page_archive_ibfk_2` FOREIGN KEY (`role`) REFERENCES `auth_group` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `plugin_wiki_page_archive_ibfk_3` FOREIGN KEY (`created_by`) REFERENCES `auth_user` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `plugin_wiki_page_archive_ibfk_4` FOREIGN KEY (`modified_by`) REFERENCES `auth_user` (`id`) ON DELETE CASCADE;

--
-- Constraints for table `plugin_wiki_tag`
--
ALTER TABLE `plugin_wiki_tag`
  ADD CONSTRAINT `plugin_wiki_tag_ibfk_1` FOREIGN KEY (`created_by`) REFERENCES `auth_user` (`id`) ON DELETE CASCADE;

--
-- Constraints for table `prune_detail`
--
ALTER TABLE `prune_detail`
  ADD CONSTRAINT `prune_detail_ibfk_1` FOREIGN KEY (`pruned_gnode`) REFERENCES `gnode` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `prune_detail_ibfk_2` FOREIGN KEY (`gtree_edit`) REFERENCES `gtree_edit` (`id`) ON DELETE CASCADE;

--
-- Constraints for table `sequence`
--
ALTER TABLE `sequence`
  ADD CONSTRAINT `sequence_ibfk_1` FOREIGN KEY (`otu`) REFERENCES `otu` (`id`) ON DELETE NO ACTION,
  ADD CONSTRAINT `sequence_ibfk_2` FOREIGN KEY (`gene`) REFERENCES `gene` (`id`) ON DELETE NO ACTION;

--
-- Constraints for table `snode`
--
ALTER TABLE `snode`
  ADD CONSTRAINT `snode_ibfk_5` FOREIGN KEY (`otu`) REFERENCES `otu` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `snode_ibfk_7` FOREIGN KEY (`parent`) REFERENCES `snode` (`id`) ON DELETE SET NULL,
  ADD CONSTRAINT `snode_ibfk_8` FOREIGN KEY (`tree`) REFERENCES `stree` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `snode_ibfk_9` FOREIGN KEY (`ottol_name`) REFERENCES `ottol_name` (`id`) ON DELETE SET NULL;

--
-- Constraints for table `stree`
--
ALTER TABLE `stree`
  ADD CONSTRAINT `stree_ibfk_1` FOREIGN KEY (`study`) REFERENCES `study` (`id`) ON DELETE CASCADE;

--
-- Constraints for table `stree_tag`
--
ALTER TABLE `stree_tag`
  ADD CONSTRAINT `stree_tag_ibfk_2` FOREIGN KEY (`stree`) REFERENCES `stree` (`id`) ON DELETE CASCADE;

--
-- Constraints for table `study`
--
ALTER TABLE `study`
  ADD CONSTRAINT `study_ibfk_1` FOREIGN KEY (`focal_clade_ottol`) REFERENCES `ottol_name` (`id`) ON DELETE SET NULL;

--
-- Constraints for table `study_file`
--
ALTER TABLE `study_file`
  ADD CONSTRAINT `study_file_ibfk_1` FOREIGN KEY (`study`) REFERENCES `study` (`id`) ON DELETE CASCADE;

--
-- Constraints for table `study_tag`
--
ALTER TABLE `study_tag`
  ADD CONSTRAINT `study_tag_ibfk_2` FOREIGN KEY (`study`) REFERENCES `study` (`id`) ON DELETE CASCADE;

--
-- Constraints for table `treebase_matrix`
--
ALTER TABLE `treebase_matrix`
  ADD CONSTRAINT `treebase_matrix_ibfk_1` FOREIGN KEY (`study`) REFERENCES `study` (`id`) ON DELETE NO ACTION;

--
-- Constraints for table `treebase_matrix_row`
--
ALTER TABLE `treebase_matrix_row`
  ADD CONSTRAINT `treebase_matrix_row_ibfk_1` FOREIGN KEY (`otu`) REFERENCES `otu` (`id`) ON DELETE NO ACTION;

--
-- Constraints for table `treeMetaDepthDetail`
--
ALTER TABLE `treeMetaDepthDetail`
  ADD CONSTRAINT `treeMetaDepthDetail_ibfk_1` FOREIGN KEY (`treeMeta`) REFERENCES `treeMeta` (`id`) ON DELETE CASCADE;

--
-- Constraints for table `user_map`
--
ALTER TABLE `user_map`
  ADD CONSTRAINT `user_map_ibfk_1` FOREIGN KEY (`auth_user_id`) REFERENCES `auth_user` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `user_map_ibfk_2` FOREIGN KEY (`unique_user_id`) REFERENCES `unique_user` (`id`) ON DELETE CASCADE;
