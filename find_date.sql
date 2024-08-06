CREATE or ALTER FUNCTION [dbo].[find_date](@start_date DATE, @days INT, @hasToday BIT, @isBackward BIT)
RETURNS TABLE
AS
RETURN
(
	SELECT TOP (@days) date, day_of_stock
	FROM calendar
	WHERE 
		(@hasToday = 1 AND @isBackward = 1 AND date <= @start_date		-- 包含今天，往前找
		OR @hasToday = 0 AND @isBackward = 1 AND date < @start_date		-- 不包含今天，往前找
		OR @hasToday = 1 AND @isBackward = 0 AND date >= @start_date	-- 包含今天，往後找
		OR @hasToday = 0 AND @isBackward = 0 AND date > @start_date)	-- 不包含今天，往後找
		AND day_of_stock != -1											-- 扣除休市日
	ORDER BY 
		CASE WHEN @isBackward = 1 THEN date END DESC,					-- 往前找就降序排列
		CASE WHEN @isBackward = 0 THEN date END ASC						-- 往後找就升序排列
)
