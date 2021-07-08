USE [tso]
GO

/****** Object:  Table [dbo].[LOG_PLATFORM]    Script Date: 4/12/2019 4:09:51 PM ******/
DROP TABLE [dbo].[LOG_PLATFORM]
GO

/****** Object:  Table [dbo].[LOG_PLATFORM]    Script Date: 4/12/2019 4:09:51 PM ******/
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
PRIMARY KEY CLUSTERED 
(
	[ID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY]
GO


