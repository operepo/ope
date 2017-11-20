FROM gitlab/gitlab-ce:latest

ENV VIRTUAL_HOST=git.ed

COPY start.sh /start.sh
RUN chmod +x /start.sh

VOLUME ["/etc/gitlab", "/var/log/gitlab", "/var/opt/gitlab"]

#CMD /start.sh