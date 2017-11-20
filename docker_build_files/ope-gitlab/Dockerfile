FROM gitlab/gitlab-ce:release

ENV VIRTUAL_HOST=gitlab.ed

COPY start.sh /start.sh
RUN chmod +x /start.sh

VOLUME ["/etc/gitlab", "/var/log/gitlab", "/var/opt/gitlab"]

CMD /start.sh