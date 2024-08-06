CREATE or ALTER PROCEDURE [dbo].[MA_calculator]
	@date char(10),
	@company varchar(10)
AS
BEGIN
	-- SET NOCOUNT ON added to prevent extra result sets from
	-- interfering with SELECT statements.
	SET NOCOUNT ON

	DECLARE @MA5 real
    -- Insert statements for procedure here

	--MA5
	SELECT @MA5 = AVG([c])
	FROM stock_data
	WHERE date in (SELECT date FROM find_date(@date, 5, 1, 1)) AND stock_code = @company

	UPDATE stock_data
	SET MA5 = @MA5
	WHERE date = @date AND stock_code = @company
END
