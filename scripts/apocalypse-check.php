#!/usr/bin/env php
<?php
/**
 * NWO Signal Spectrum - Apocalypse Indicator Cron Job
 * 
 * Run this every 5-15 minutes to check for apocalyptic signals
 * Add to crontab:
 * */15 * * * * /usr/bin/php /path/to/apocalypse-check.php >> /var/log/nwo-apocalypse.log 2>&1
 */

// Autoload
require_once __DIR__ . '/../vendor/autoload.php';

use NWOSignalSpectrum\ApocalypseIndicators;

// Database connection
$dbHost = getenv('DB_HOST') ?: 'localhost';
$dbName = getenv('DB_NAME') ?: 'nwocapital';
$dbUser = getenv('DB_USER') ?: 'root';
$dbPass = getenv('DB_PASS') ?: '';

try {
    $db = new PDO(
        "mysql:host={$dbHost};dbname={$dbName};charset=utf8mb4",
        $dbUser,
        $dbPass,
        [
            PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION,
            PDO::ATTR_DEFAULT_FETCH_MODE => PDO::FETCH_ASSOC,
            PDO::ATTR_EMULATE_PREPARES => false,
        ]
    );
} catch (PDOException $e) {
    error_log("[" . date('Y-m-d H:i:s') . "] Database connection failed: " . $e->getMessage());
    exit(1);
}

$indicators = new ApocalypseIndicators($db);

echo "[" . date('Y-m-d H:i:s') . "] Starting apocalypse checks...\n";

// Run all detection checks
$alerts = [];

try {
    // 1. Aviation Anomaly Check
    echo "Checking aviation anomalies...\n";
    $aviation = $indicators->detectAviationAnomaly();
    if ($aviation) {
        $alerts[] = $aviation;
        echo "  ⚠️  AVIATION ALERT: {$aviation['description']}\n";
    } else {
        echo "  ✓ No aviation anomalies\n";
    }
    
    // 2. Seismic Activity Check
    echo "Checking seismic activity...\n";
    $seismic = $indicators->detectSeismicAnomaly(24);
    if ($seismic) {
        $alerts[] = $seismic;
        echo "  ⚠️  SEISMIC ALERT: {$seismic['description']}\n";
    } else {
        echo "  ✓ No significant seismic activity\n";
    }
    
    // 3. Solar Activity Check
    echo "Checking solar activity...\n";
    $solar = $indicators->detectSolarAnomaly();
    if ($solar) {
        if (is_array($solar) && isset($solar[0])) {
            foreach ($solar as $event) {
                $alerts[] = $event;
                echo "  ⚠️  SOLAR ALERT: {$event['description']}\n";
            }
        } else {
            $alerts[] = $solar;
            echo "  ⚠️  SOLAR ALERT: {$solar['description']}\n";
        }
    } else {
        echo "  ✓ No significant solar activity\n";
    }
    
    // 4. Radiation Check
    echo "Checking radiation levels...\n";
    $radiation = $indicators->detectRadiationAnomaly();
    if ($radiation) {
        $alerts[] = $radiation;
        echo "  ⚠️  RADIATION ALERT: {$radiation['description']}\n";
    } else {
        echo "  ✓ No radiation spikes\n";
    }
    
    // 5. Asteroid Check
    echo "Checking asteroid approaches...\n";
    $asteroid = $indicators->detectAsteroidThreat(7);
    if ($asteroid) {
        $alerts[] = $asteroid;
        echo "  ⚠️  ASTEROID ALERT: {$asteroid['description']}\n";
    } else {
        echo "  ✓ No threatening asteroids\n";
    }
    
} catch (Exception $e) {
    error_log("[" . date('Y-m-d H:i:s') . "] Error during checks: " . $e->getMessage());
    echo "  ✗ Error: {$e->getMessage()}\n";
}

// Summary
echo "\n[" . date('Y-m-d H:i:s') . "] Check complete. Found " . count($alerts) . " alert(s)\n";

// Calculate and store apocalypse level
try {
    $level = $indicators->calculateApocalypseLevel();
    echo "Current Apocalypse Level: {$level['level']}/5 - {$level['description']}\n";
    
    // Store level in history
    $stmt = $db->prepare("
        INSERT INTO apocalypse_level_history (level, description, active_signals)
        VALUES (?, ?, ?)
    ");
    $stmt->execute([$level['level'], $level['description'], $level['active_signals']]);
    
    // Send notification if level is elevated
    if ($level['level'] >= 3) {
        sendLevelAlert($level);
    }
    
} catch (Exception $e) {
    error_log("[" . date('Y-m-d H:i:s') . "] Error calculating level: " . $e->getMessage());
}

// Send notifications for critical alerts
foreach ($alerts as $alert) {
    if (in_array($alert['severity'], ['critical', 'extreme'])) {
        sendNotification($alert);
    }
}

echo "[" . date('Y-m-d H:i:s') . "] Done.\n";
echo str_repeat("=", 60) . "\n\n";

// Notification functions
function sendNotification($alert) {
    $telegramToken = getenv('TELEGRAM_BOT_TOKEN');
    $chatId = getenv('TELEGRAM_CHAT_ID');
    $discordWebhook = getenv('DISCORD_WEBHOOK_URL');
    
    $emoji = ['low' => '⚪', 'medium' => '🟡', 'high' => '🟠', 'critical' => '🔴', 'extreme' => '☠️'][$alert['severity']] ?? '⚪';
    
    $message = sprintf(
        "%s *APOCALYPSE ALERT - %s*%s\n\n" .
        "Type: %s\n" .
        "Severity: %s\n" .
        "Description: %s\n" .
        "Time: %s\n\n" .
        "Monitor: https://nwo.capital/spectrum",
        $emoji,
        strtoupper($alert['type']),
        $alert['severity'] === 'extreme' ? ' 🚨' : '',
        $alert['type'],
        strtoupper($alert['severity']),
        $alert['description'],
        date('Y-m-d H:i:s', $alert['timestamp'])
    );
    
    // Telegram notification
    if ($telegramToken && $chatId) {
        $url = "https://api.telegram.org/bot{$telegramToken}/sendMessage";
        $data = [
            'chat_id' => $chatId,
            'text' => $message,
            'parse_mode' => 'Markdown',
            'disable_notification' => $alert['severity'] === 'low'
        ];
        
        $ch = curl_init($url);
        curl_setopt($ch, CURLOPT_POST, true);
        curl_setopt($ch, CURLOPT_POSTFIELDS, http_build_query($data));
        curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
        curl_setopt($ch, CURLOPT_TIMEOUT, 10);
        $result = curl_exec($ch);
        $httpCode = curl_getinfo($ch, CURLINFO_HTTP_CODE);
        curl_close($ch);
        
        if ($httpCode === 200) {
            echo "  📱 Telegram notification sent\n";
        } else {
            error_log("Failed to send Telegram notification: HTTP {$httpCode}");
        }
    }
    
    // Discord notification
    if ($discordWebhook) {
        $color = [
            'low' => 0x808080,
            'medium' => 0xFFFF00,
            'high' => 0xFFA500,
            'critical' => 0xFF0000,
            'extreme' => 0x000000
        ][$alert['severity']] ?? 0x808080;
        
        $embed = [
            'title' => "🚨 Apocalypse Alert - " . ucfirst($alert['type']),
            'description' => $alert['description'],
            'color' => $color,
            'fields' => [
                ['name' => 'Severity', 'value' => strtoupper($alert['severity']), 'inline' => true],
                ['name' => 'Time', 'value' => date('Y-m-d H:i:s', $alert['timestamp']), 'inline' => true]
            ],
            'footer' => ['text' => 'NWO Signal Spectrum'],
            'timestamp' => date('c', $alert['timestamp'])
        ];
        
        $payload = json_encode(['embeds' => [$embed]]);
        
        $ch = curl_init($discordWebhook);
        curl_setopt($ch, CURLOPT_POST, true);
        curl_setopt($ch, CURLOPT_POSTFIELDS, $payload);
        curl_setopt($ch, CURLOPT_HTTPHEADER, ['Content-Type: application/json']);
        curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
        curl_setopt($ch, CURLOPT_TIMEOUT, 10);
        curl_exec($ch);
        curl_close($ch);
        
        echo "  💬 Discord notification sent\n";
    }
    
    // Webhook to NWO agent network
    $webhookUrl = getenv('NWO_SPECTRUM_WEBHOOK');
    if ($webhookUrl) {
        $payload = json_encode([
            'event' => 'apocalypse_alert',
            'data' => $alert,
            'timestamp' => time()
        ]);
        
        $ch = curl_init($webhookUrl);
        curl_setopt($ch, CURLOPT_POST, true);
        curl_setopt($ch, CURLOPT_POSTFIELDS, $payload);
        curl_setopt($ch, CURLOPT_HTTPHEADER, ['Content-Type: application/json']);
        curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
        curl_setopt($ch, CURLOPT_TIMEOUT, 10);
        curl_exec($ch);
        curl_close($ch);
        
        echo "  🌐 Webhook sent to agent network\n";
    }
}

function sendLevelAlert($level) {
    $telegramToken = getenv('TELEGRAM_BOT_TOKEN');
    $chatId = getenv('TELEGRAM_CHAT_ID');
    
    if (!$telegramToken || !$chatId) return;
    
    $emoji = ['', '⚪', '🟢', '🟡', '🟠', '🔴'][$level['level']] ?? '⚪';
    
    $message = sprintf(
        "%s *APOCALYPSE LEVEL UPDATE*%s\n\n" .
        "Current Level: %d/5\n" .
        "%s\n\n" .
        "Active Signals: %d\n" .
        "Monitor: https://nwo.capital/spectrum",
        $emoji,
        $level['level'] >= 4 ? ' 🚨' : '',
        $level['level'],
        $level['description'],
        $level['active_signals']
    );
    
    $url = "https://api.telegram.org/bot{$telegramToken}/sendMessage";
    $data = [
        'chat_id' => $chatId,
        'text' => $message,
        'parse_mode' => 'Markdown'
    ];
    
    $ch = curl_init($url);
    curl_setopt($ch, CURLOPT_POST, true);
    curl_setopt($ch, CURLOPT_POSTFIELDS, http_build_query($data));
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
    curl_setopt($ch, CURLOPT_TIMEOUT, 10);
    curl_exec($ch);
    curl_close($ch);
    
    echo "  📱 Level alert sent to Telegram\n";
}
