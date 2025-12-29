@echo off
echo Testing webhook endpoint with order 35456...
curl "http://localhost:5000/test-odoo?order_id=35456"
echo.
echo.
pause

