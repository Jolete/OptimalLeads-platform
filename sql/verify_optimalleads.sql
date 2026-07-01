SELECT TOP (1000)
    [event_id],
    [aggregate_id],
    [event_name],
    [event_kind],
    [correlation_id],
    [causation_id],
    [occurred_at],
    [payload],
    [created_at]
FROM [optimalleads_chat].[dbo].[chat_outbox];

SELECT TOP (1000)
    [conversation_id],
    [title],
    [messages],
    [created_at]
FROM [optimalleads_chat].[dbo].[chat_conversations];

SELECT TOP (1000)
    [id],
    [name],
    [email],
    [stage]
FROM [optimalleads_leads].[dbo].[leads];

SELECT TOP (1000)
    [id],
    [name],
    [category]
FROM [optimalleads_analytics].[dbo].[projections];
