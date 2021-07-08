USE [tso]
GO

/****** Object:  Table [dbo].[LOG_HEALTH]    Script Date: 4/12/2019 4:09:45 PM ******/
DROP TABLE [dbo].[LOG_HEALTH]
GO

/****** Object:  Table [dbo].[LOG_HEALTH]    Script Date: 4/12/2019 4:09:45 PM ******/
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
PRIMARY KEY CLUSTERED 
(
	[ID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY]
GO


