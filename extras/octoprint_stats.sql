------------- SQLite3 Dump File -------------

-- ------------------------------------------
-- Dump of "connected"
-- ------------------------------------------

CREATE TABLE "connected"(
	"event_time" DateTime PRIMARY KEY,
	"port" Text,
	"baudrate" Text );


-- ------------------------------------------
-- Dump of "disconnected"
-- ------------------------------------------

CREATE TABLE "disconnected"(
	"event_time" DateTime PRIMARY KEY );


-- ------------------------------------------
-- Dump of "upload"
-- ------------------------------------------

CREATE TABLE "upload"(
	"event_time" DateTime PRIMARY KEY,
	"file" Text,
	"target" Text );


-- ------------------------------------------
-- Dump of "print_started"
-- ------------------------------------------

CREATE TABLE "print_started"(
	"event_time" DateTime PRIMARY KEY,
	"file" Text,
	"origin" Text );


-- ------------------------------------------
-- Dump of "print_done"
-- ------------------------------------------

CREATE TABLE "print_done"(
	"event_time" DateTime PRIMARY KEY,
	"file" Text,
	"ptime" Integer,
	"origin" Text );


-- ------------------------------------------
-- Dump of "print_failed"
-- ------------------------------------------

CREATE TABLE "print_failed"(
	"event_time" DateTime PRIMARY KEY,
	"file" Text,
	"origin" Text );


-- ------------------------------------------
-- Dump of "print_cancelled"
-- ------------------------------------------

CREATE TABLE "print_cancelled"(
	"event_time" DateTime PRIMARY KEY,
	"file" Text,
	"origin" Text );


-- ------------------------------------------
-- Dump of "print_paused"
-- ------------------------------------------

CREATE TABLE "print_paused"(
	"event_time" DateTime PRIMARY KEY,
	"file" Text,
	"origin" Text );


-- ------------------------------------------
-- Dump of "print_resumed"
-- ------------------------------------------

CREATE TABLE "print_resumed"(
	"event_time" DateTime PRIMARY KEY,
	"file" Text,
	"origin" Text );


-- ------------------------------------------
-- Dump of "error"
-- ------------------------------------------

CREATE TABLE "error"(
	"event_time" DateTime PRIMARY KEY,
	"perror" Text );


