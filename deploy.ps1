git add -A
git commit -m $args[0]
git push
python -c "import requests; requests.post('https://api.vercel.com/v1/integrations/deploy/prj_CAYgv8zlg8P3n4tLIA7yf4hPsxEP/eBOcjAn0yz')"
Write-Host "Deployed!"
