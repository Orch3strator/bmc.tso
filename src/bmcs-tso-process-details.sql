USE [tso]
GO

/****** Object:  Table [dbo].[LOG_PROCESS_DETAIL]    Script Date: 4/12/2019 4:10:02 PM ******/
DROP TABLE [dbo].[LOG_PROCESS_DETAIL]
GO

/****** Object:  Table [dbo].[LOG_PROCESS_DETAIL]    Script Date: 4/12/2019 4:10:02 PM ******/
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
PRIMARY KEY CLUSTERED 
(
	[ID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY]
GO


