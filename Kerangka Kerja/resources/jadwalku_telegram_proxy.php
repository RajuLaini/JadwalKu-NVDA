<?php
/**
 * JadwalKu Telegram Webhook & Feedback API Proxy
 * v1.6.2 (Serverless/PHP Forwarder)
 * 
 * Unggah file ini ke server/hosting Anda (misal: https://rajulaini.com/api/jadwalku/feedback.php atau index.php)
 * dan sesuaikan TELEGRAM_BOT_TOKEN serta TELEGRAM_CHAT_ID di bawah ini dengan kredensial bot Anda (Aileen Bot).
 */

header('Content-Type: application/json; charset=utf-8');
header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Methods: POST, GET, OPTIONS');
header('Access-Control-Allow-Headers: Content-Type, User-Agent');

if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') {
    http_response_code(200);
    exit;
}

// =================== KONFIGURASI BOT TELEGRAM ===================
// Ganti dengan Token Bot Telegram Anda (Aileen Bot)
define('TELEGRAM_BOT_TOKEN', 'GANTI_DENGAN_TOKEN_BOT_TELEGRAM_ANDA');

// Ganti dengan Chat ID / User ID / Group ID tujuan penerimaan laporan
define('TELEGRAM_CHAT_ID', 'GANTI_DENGAN_CHAT_ID_TELEGRAM_ANDA');

// Batas maksimal total laporan harian dari SELURUH pengguna
define('DAILY_MAX_REPORTS', 10);
// ===============================================================

$today = date('Y-m-d');
$logFile = __DIR__ . '/daily_reports_counter.json';

// Baca atau inisialisasi file penghitung laporan harian
$counterData = ['date' => $today, 'count' => 0, 'ips' => []];
if (file_exists($logFile)) {
    $content = file_get_contents($logFile);
    $decoded = json_decode($content, true);
    if ($decoded && isset($decoded['date']) && $decoded['date'] === $today) {
        $counterData = $decoded;
    }
}

$userIp = $_SERVER['REMOTE_ADDR'] ?? 'Unknown IP';

// 1. Tangani Pengecekan Kuota Harian (GET ?action=check_limit)
if ($_SERVER['REQUEST_METHOD'] === 'GET') {
    if (isset($_GET['action']) && $_GET['action'] === 'check_limit') {
        if ($counterData['count'] >= DAILY_MAX_REPORTS) {
            echo json_encode([
                'allowed' => false,
                'reason' => 'daily_limit_reached',
                'message' => 'Kuota harian laporan (maksimal ' . DAILY_MAX_REPORTS . ' laporan) telah penuh.'
            ]);
        } elseif (in_array($userIp, $counterData['ips'])) {
            echo json_encode([
                'allowed' => false,
                'reason' => 'user_already_sent',
                'message' => 'Anda sudah mengirimkan laporan hari ini.'
            ]);
        } else {
            echo json_encode([
                'allowed' => true,
                'current_count' => $counterData['count'],
                'max_limit' => DAILY_MAX_REPORTS
            ]);
        }
        exit;
    }
}

// 2. Tangani Pengiriman Laporan (POST JSON)
if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    // Periksa apakah kuota harian sudah penuh
    if ($counterData['count'] >= DAILY_MAX_REPORTS) {
        http_response_code(429);
        echo json_encode([
            'success' => false,
            'allowed' => false,
            'reason' => 'daily_limit_reached',
            'message' => 'Mohon maaf, kuota penerimaan laporan JadwalKu untuk hari ini (maksimal 10 laporan/hari) telah penuh. Silakan coba kembali besok pagi!'
        ]);
        exit;
    }

    // Periksa apakah IP/mesin ini sudah mengirim laporan hari ini
    if (in_array($userIp, $counterData['ips'])) {
        http_response_code(429);
        echo json_encode([
            'success' => false,
            'allowed' => false,
            'reason' => 'user_already_sent',
            'message' => 'Anda sudah mengirimkan satu laporan hari ini. Terima kasih atas partisipasi Anda!'
        ]);
        exit;
    }

    $rawInput = file_get_contents('php://input');
    $data = json_decode($rawInput, true);

    if (!$data || empty($data['description'])) {
        http_response_code(400);
        echo json_encode(['success' => false, 'message' => 'Deskripsi laporan tidak boleh kosong.']);
        exit;
    }

    $username = htmlspecialchars($data['username'] ?? 'Unknown');
    $machineName = htmlspecialchars($data['machine_name'] ?? 'Unknown PC');
    $nvdaVersion = htmlspecialchars($data['nvda_version'] ?? 'NVDA');
    $osVersion = htmlspecialchars($data['os_version'] ?? 'Windows');
    $category = htmlspecialchars($data['category'] ?? 'General');
    $subFeature = htmlspecialchars($data['sub_feature'] ?? '-');
    $title = htmlspecialchars($data['title'] ?? 'Laporan JadwalKu');
    $description = htmlspecialchars($data['description'] ?? '');
    $logs = htmlspecialchars($data['logs'] ?? '');

    // Format pesan Telegram bergaya Markdown / HTML yang rapi
    $telegramMessage = "🚨 *LAPORAN / SARAN JADWALKU (v1.6.2)* 🚨\n\n"
        . "📌 *Kategori:* {$category}\n"
        . "🧩 *Sub-Fitur:* {$subFeature}\n"
        . "🏷️ *Judul:* {$title}\n\n"
        . "👤 *Pengguna:* `{$username}` (`{$machineName}`)\n"
        . "🌐 *IP Address:* `{$userIp}`\n"
        . "💻 *Sistem:* `{$nvdaVersion}` | `{$osVersion}`\n"
        . "🕒 *Waktu:* `{$data['client_time']}`\n\n"
        . "💬 *Deskripsi Laporan:*\n{$description}\n";

    if (!empty($logs)) {
        // Potong log jika terlalu panjang agar tidak melebihi batas pesan Telegram (4096 karakter)
        $shortLogs = substr($logs, 0, 1500);
        $telegramMessage .= "\n📋 *Log Diagnostik NVDA:*\n```text\n{$shortLogs}\n```";
    }

    // Kirim ke Telegram via cURL
    if (TELEGRAM_BOT_TOKEN !== 'GANTI_DENGAN_TOKEN_BOT_TELEGRAM_ANDA' && TELEGRAM_CHAT_ID !== 'GANTI_DENGAN_CHAT_ID_TELEGRAM_ANDA') {
        $telegramUrl = "https://api.telegram.org/bot" . TELEGRAM_BOT_TOKEN . "/sendMessage";
        $ch = curl_init();
        curl_setopt($ch, CURLOPT_URL, $telegramUrl);
        curl_setopt($ch, CURLOPT_POST, true);
        curl_setopt($ch, CURLOPT_POSTFIELDS, [
            'chat_id' => TELEGRAM_CHAT_ID,
            'text' => $telegramMessage,
            'parse_mode' => 'Markdown'
        ]);
        curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
        curl_setopt($ch, CURLOPT_TIMEOUT, 10);
        $result = curl_exec($ch);
        $httpCode = curl_getinfo($ch, CURLINFO_HTTP_CODE);
        curl_close($ch);

        if ($httpCode != 200) {
            // Jika gagal kirim ke telegram, tetap sukses di client atau log error
            error_log("JadwalKu Telegram Proxy Error: " . $result);
        }
    }

    // Perbarui counter & daftarkan IP
    $counterData['count'] += 1;
    $counterData['ips'][] = $userIp;
    file_put_contents($logFile, json_encode($counterData, JSON_PRETTY_PRINT));

    echo json_encode([
        'success' => true,
        'message' => 'Laporan berhasil dikirim ke server Telegram.',
        'remaining_quota' => DAILY_MAX_REPORTS - $counterData['count']
    ]);
    exit;
}

http_response_code(405);
echo json_encode(['success' => false, 'message' => 'Method Not Allowed']);
