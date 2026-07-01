USE [master];
GO

IF DB_ID(N'optimalleads_chat') IS NULL
BEGIN
    CREATE DATABASE [optimalleads_chat];
END
GO

IF DB_ID(N'optimalleads_leads') IS NULL
BEGIN
    CREATE DATABASE [optimalleads_leads];
END
GO

IF DB_ID(N'optimalleads_analytics') IS NULL
BEGIN
    CREATE DATABASE [optimalleads_analytics];
END
GO

DECLARE @db sysname;
DECLARE db_cursor CURSOR LOCAL FAST_FORWARD FOR
    SELECT name
    FROM sys.databases
    WHERE name IN (N'optimalleads_chat', N'optimalleads_leads', N'optimalleads_analytics');

OPEN db_cursor;
FETCH NEXT FROM db_cursor INTO @db;

WHILE @@FETCH_STATUS = 0
BEGIN
    DECLARE @sql nvarchar(max);
    SET @sql = N'
    USE ' + QUOTENAME(@db) + N';

    IF NOT EXISTS (SELECT 1 FROM sys.database_principals WHERE name = N''optimalleads_app'')
    BEGIN
        CREATE USER [optimalleads_app] FOR LOGIN [optimalleads_app];
    END;

    ALTER ROLE [db_owner] ADD MEMBER [optimalleads_app];
    ';

    EXEC sys.sp_executesql @sql;
    FETCH NEXT FROM db_cursor INTO @db;
END

CLOSE db_cursor;
DEALLOCATE db_cursor;
GO
