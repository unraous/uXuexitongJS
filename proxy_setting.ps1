# 设置 HTTP 和 HTTPS 代理为本地 7897 端口

$proxy = "http://127.0.0.1:7897"
$env:http_proxy = $proxy
$env:https_proxy = $proxy

Write-Host "Proxy setting successful: $proxy"