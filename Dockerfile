FROM python:2.7

#
# Environment variables for configuration
#
# The url of the forum search results '%(q)s' will be subsituted with the url-encoded user query
ENV SEARCH_URL http://www.teambeachbody.com/connect/message-boards/-/message_boards/search?_19_keywords=%(q)s
# comment out for production!
# ENV FLASK_DEBUG true
# what port to start the app on -- make sure it matches the EXPOSE line below
ENV FLAST_PORT 5000
# cache max_age
ENV CACHE_MAX_AGE 300

ADD . /usr/src/app
WORKDIR /usr/src/app
RUN pip install -r requirements.txt
EXPOSE 5000
