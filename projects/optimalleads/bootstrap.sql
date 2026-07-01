USE [master];
GO

IF NOT EXISTS (SELECT 1 FROM sys.sql_logins WHERE name = N'optimalleads_app')
BEGIN
    CREATE LOGIN [optimalleads_app] WITH PASSWORD = N'OptimalLeads1234!', CHECK_POLICY = OFF, CHECK_EXPIRATION = OFF;
END
GO

