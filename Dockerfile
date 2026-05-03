FROM php:8.1-apache

# Install dependencies
RUN apt-get update && apt-get install -y \
    libfftw3-dev \
    libsndfile1-dev \
    libsoapysdr-dev \
    libxml2-dev \
    cmake \
    build-essential \
    git \
    sqlite3 \
    redis-tools \
    && rm -rf /var/lib/apt/lists/*

# Build and install sigutils
RUN git clone --recursive https://github.com/BatchDrake/sigutils.git /tmp/sigutils \
    && cd /tmp/sigutils \
    && mkdir build && cd build \
    && cmake .. \
    && make -j$(nproc) \
    && make install \
    && ldconfig

# Build and install suscan
RUN git clone --recursive https://github.com/BatchDrake/suscan.git /tmp/suscan \
    && cd /tmp/suscan \
    && mkdir build && cd build \
    && cmake .. \
    && make -j$(nproc) \
    && make install \
    && ldconfig

# Enable Apache modules
RUN a2enmod rewrite headers

# Copy application files
COPY . /var/www/html/

# Set permissions
RUN chown -R www-data:www-data /var/www/html \
    && chmod -R 755 /var/www/html

# Create data directory
RUN mkdir -p /var/lib/nwo-spectrum \
    && chown www-data:www-data /var/lib/nwo-spectrum

# Expose port
EXPOSE 80

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost/api/v1/health || exit 1

# Start Apache
CMD ["apache2-foreground"]
