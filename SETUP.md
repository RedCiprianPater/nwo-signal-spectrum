## Setup Instructions

### 1. Install Dependencies
composer install

### 2. Configure Environment
cp .env.example .env
# Edit .env with your settings

### 3. Set Up Cron (Optional)
crontab -e
*/15 * * * * /usr/bin/php scripts/apocalypse-check.php

### 4. Run
php scripts/apocalypse-check.php
