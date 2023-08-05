from ajenti.api import *
from ajenti.plugins.webserver_common.api import WebserverPlugin
from ajenti.util import platform_select


@plugin
class Nginx (WebserverPlugin):
    service_name = 'nginx'
    service_buttons = [
        {
            'command': 'force-reload',
            'text': _('Reload'),
            'icon': 'step-forward',
        }
    ]
    hosts_available_dir = platform_select(
        debian='/etc/nginx/sites-available',
        centos='/etc/nginx/conf.d',
        freebsd='/usr/local/etc/nginx/conf.d',
    )
    hosts_enabled_dir = '/etc/nginx/sites-enabled'
    supports_host_activation = platform_select(
        debian=True,
        default=False,
    )

    template = """server {
    server_name name;
    access_log /var/log/nginx/name.access.log;
    error_log  /var/log/nginx/name.error.log;

    listen 80;

    location / {
        root /var/www/name;
    }

    location ~ \.lang$ {
        include fastcgi_params;
        fastcgi_pass 127.0.0.1:port;
        fastcgi_split_path_info ^()(.*)$;
    }
}
"""

    def init(self):
        self.title = 'NGINX'
        self.category = _('Software')
        self.icon = 'globe'
