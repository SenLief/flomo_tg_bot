# @BotFather api token
API_TOKEN = ''

MODE = 'webhook' #polling or webhook
# nginx反代域名，要求必须用https
WEBHOOK_HOST = 'bot.tg.com'

# 端口
WEBHOOK_PORT = 8443  # 443, 80, 88 or 8443 (port need to be 'open')
# 监听
WEBHOOK_LISTEN = '127.0.0.1'  # In some VPS you may need to put here the IP addr

#给管理员发送一些日志
ADMIN_ID = ''
# nginx conf example

# server
# {
#     listen 80;
#     listen 443 ssl http2;
#     server_name xxxxxxxxx;
#     index index.php index.html index.htm default.php default.htm default.html;
#     root /var/www/html;
#
#
#     if ($server_port !~ 443){
#         rewrite ^(/.*)$ https://$host$1 permanent;
#     }
#     #HTTP_TO_HTTPS_END
#     ssl_certificate    /etc/nginx/ssl/529213.xyz.cert.pem;
#     ssl_certificate_key    /etc/nginx/ssl/529213.xyz.key.pem;
#     ssl_protocols TLSv1 TLSv1.1 TLSv1.2;
#     ssl_ciphers ECDHE-RSA-AES128-GCM-SHA256:HIGH:!aNULL:!MD5:!RC4:!DHE;
#     ssl_prefer_server_ciphers on;
#     ssl_session_cache shared:SSL:10m;
#     ssl_session_timeout 10m;
#     error_page 497  https://$host$request_uri;
#
#     #SSL-END
#
#     location / {
#         proxy_set_header   X-Real-IP $remote_addr;
#         proxy_set_header   Host      $http_host;
#         proxy_pass         http://127.0.0.1:8443;
#         proxy_set_header REMOTE-HOST $remote_addr;
#         proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
#         proxy_set_header X-Forwarded-Proto $scheme;
#         client_max_body_size 100m;
#         }
# }
