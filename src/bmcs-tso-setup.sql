USE [tso]
GO

/****** Object:  Table [dbo].[LOG_PROCESS_DETAIL]    Script Date: 8/1/2019 6:20:50 PM ******/
DROP TABLE [dbo].[LOG_PROCESS_DETAIL]
GO

/****** Object:  Table [dbo].[LOG_PROCESS_DETAIL]    Script Date: 8/1/2019 6:20:50 PM ******/
SET ANSI_NULLS ON
GO

SET QUOTED_IDENTIFIER ON
GO

CREATE TABLE [dbo].[LOG_PROCESS_DETAIL](
	[ID] [numeric](19, 0) IDENTITY(1,1) NOT NULL,
	[REPORT_TIMESTAMP] [datetime] NULL,
	[REPORT_EPOCH] [int] NULL,
	[REPORT_DATE] [date] NULL,
	[REPORT_TIME] [time](7) NULL,
	[REPORT_WINDOW] [time](7) NULL,
	[SFDC] [varchar](255) NULL,
	[CUSTOMER] [varchar](255) NULL,
	[GRID] [varchar](255) NULL,
	[PEER] [varchar](255) NULL,
	[ROOT_JOB] [varchar](255) NULL,
	[MODULE] [varchar](255) NULL,
	[WORKFLOW] [varchar](255) NULL,
	[PROCESS_ID] [varchar](255) NULL,
	[PROCESS_STATUS] [varchar](255) NULL,
	[PROCESS_START] [datetime] NULL,
	[PROCESS_END] [datetime] NULL,
	[PROCESS_DURATION] [int] NULL,
	[PROCESS_PATH] [varchar](4096) NULL,
	[LOG_FILE_NAME] [varchar](4096) NULL,
PRIMARY KEY CLUSTERED 
(
	[ID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY]
GO

USE [tso]
GO

/****** Object:  Table [dbo].[LOG_GRID]    Script Date: 8/1/2019 6:20:30 PM ******/
DROP TABLE [dbo].[LOG_GRID]
GO

/****** Object:  Table [dbo].[LOG_GRID]    Script Date: 8/1/2019 6:20:30 PM ******/
SET ANSI_NULLS ON
GO

SET QUOTED_IDENTIFIER ON
GO

CREATE TABLE [dbo].[LOG_GRID](
	[ID] [numeric](19, 0) IDENTITY(1,1) NOT NULL,
	[REPORT_TIMESTAMP] [datetime] NULL,
	[REPORT_EPOCH] [int] NULL,
	[REPORT_DATE] [date] NULL,
	[REPORT_TIME] [time](7) NULL,
	[REPORT_WINDOW] [time](7) NULL,
	[SFDC] [varchar](255) NULL,
	[CUSTOMER] [varchar](255) NULL,
	[GRID] [varchar](255) NULL,
	[PEER] [varchar](255) NULL,
	[THREAD_TYPE] [varchar](255) NULL,
	[STATUS] [varchar](255) NULL,
	[ADAPTER] [varchar](255) NULL,
	[PROCESS_ID] [varchar](255) NULL,
	[SUMMARY] [varchar](4096) NULL,
	[INFO] [varchar](4096) NULL,
	[LOG_FILE_NAME] [varchar](4096) NULL,
PRIMARY KEY CLUSTERED 
(
	[ID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY]
GO

USE [tso]
GO

/****** Object:  Table [dbo].[LOG_HEALTH]    Script Date: 8/1/2019 6:20:35 PM ******/
DROP TABLE [dbo].[LOG_HEALTH]
GO

/****** Object:  Table [dbo].[LOG_HEALTH]    Script Date: 8/1/2019 6:20:35 PM ******/
SET ANSI_NULLS ON
GO

SET QUOTED_IDENTIFIER ON
GO

CREATE TABLE [dbo].[LOG_HEALTH](
	[ID] [numeric](19, 0) IDENTITY(1,1) NOT NULL,
	[REPORT_TIMESTAMP] [datetime] NULL,
	[REPORT_EPOCH] [int] NULL,
	[REPORT_DATE] [date] NULL,
	[REPORT_TIME] [time](7) NULL,
	[REPORT_WINDOW] [time](7) NULL,
	[SFDC] [varchar](255) NULL,
	[CUSTOMER] [varchar](255) NULL,
	[GRID] [varchar](255) NULL,
	[PEER] [varchar](255) NULL,
	[CATEGORY] [varchar](255) NULL,
	[DESCRIPTION] [varchar](255) NULL,
	[STATUS] [varchar](255) NULL,
	[METRIC_INSTANCE] [varchar](255) NULL,
	[METRIC_NAME] [varchar](255) NULL,
	[METRIC_VALUE] [int] NULL,
	[LOG_FILE_NAME] [varchar](4096) NULL,
PRIMARY KEY CLUSTERED 
(
	[ID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY]
GO

USE [tso]
GO

/****** Object:  Table [dbo].[LOG_PLATFORM]    Script Date: 8/1/2019 6:20:40 PM ******/
DROP TABLE [dbo].[LOG_PLATFORM]
GO

/****** Object:  Table [dbo].[LOG_PLATFORM]    Script Date: 8/1/2019 6:20:40 PM ******/
SET ANSI_NULLS ON
GO

SET QUOTED_IDENTIFIER ON
GO

CREATE TABLE [dbo].[LOG_PLATFORM](
	[ID] [numeric](19, 0) IDENTITY(1,1) NOT NULL,
	[REPORT_TIMESTAMP] [datetime] NULL,
	[REPORT_EPOCH] [int] NULL,
	[REPORT_DATE] [date] NULL,
	[REPORT_TIME] [time](7) NULL,
	[REPORT_WINDOW] [time](7) NULL,
	[SFDC] [varchar](255) NULL,
	[CUSTOMER] [varchar](255) NULL,
	[GRID] [varchar](255) NULL,
	[PEER] [varchar](255) NULL,
	[MODULE] [varchar](255) NULL,
	[WORKFLOW] [varchar](255) NULL,
	[PROCESS_ID] [varchar](255) NULL,
	[PROCESS_PATH] [varchar](4096) NULL,
	[LEVEL] [varchar](255) NULL,
	[TYPE] [varchar](255) NULL,
	[JAVA_CLASS] [varchar](255) NULL,
	[JAVA_OPERATION] [varchar](255) NULL,
	[SUMMARY] [varchar](4096) NULL,
	[LOG_FILE_NAME] [varchar](4096) NULL,
PRIMARY KEY CLUSTERED 
(
	[ID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY]
GO


USE [tso]
GO

/****** Object:  Table [dbo].[LOG_PROCESS]    Script Date: 8/1/2019 6:20:46 PM ******/
DROP TABLE [dbo].[LOG_PROCESS]
GO

/****** Object:  Table [dbo].[LOG_PROCESS]    Script Date: 8/1/2019 6:20:46 PM ******/
SET ANSI_NULLS ON
GO

SET QUOTED_IDENTIFIER ON
GO

CREATE TABLE [dbo].[LOG_PROCESS](
	[ID] [numeric](19, 0) IDENTITY(1,1) NOT NULL,
	[REPORT_TIMESTAMP] [datetime] NULL,
	[REPORT_EPOCH] [int] NULL,
	[REPORT_DATE] [date] NULL,
	[REPORT_TIME] [time](7) NULL,
	[REPORT_WINDOW] [time](7) NULL,
	[SFDC] [varchar](255) NULL,
	[CUSTOMER] [varchar](255) NULL,
	[GRID] [varchar](255) NULL,
	[PEER] [varchar](255) NULL,
	[ROOT_JOB] [varchar](255) NULL,
	[MODULE] [varchar](255) NULL,
	[WORKFLOW] [varchar](255) NULL,
	[PROCESS_ID] [varchar](255) NULL,
	[PROCESS_STATUS] [varchar](255) NULL,
	[PROCESS_START] [datetime] NULL,
	[PROCESS_END] [datetime] NULL,
	[PROCESS_DURATION] [int] NULL,
	[PROCESS_PATH] [varchar](4096) NULL,
	[LOG_FILE_NAME] [varchar](4096) NULL,
PRIMARY KEY CLUSTERED 
(
	[ID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY]
GO
