# Pull base image.
FROM nginx

# File Author / Maintainer
LABEL MAINTAINER="Contact@thomas-illiet.fr"

# Copy a configuration file from the current directory
ADD site /usr/share/nginx/html