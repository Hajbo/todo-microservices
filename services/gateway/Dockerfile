FROM nginx:1.19
RUN rm -r /etc/nginx/conf.d/
VOLUME ["/var/cache/nginx", "/var/run/"]
COPY . /etc/nginx/