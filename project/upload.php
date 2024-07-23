<?php
// Flask 서버의 URL 설정
$flask_url = 'http://127.0.0.1:5000/'; // Flask 서버의 주소 (변경 필요)

// 업로드 폴더 설정
$uploadDir = 'uploads/';
if (!is_dir($uploadDir)) {
    mkdir($uploadDir, 0777, true);
}

if ($_SERVER['REQUEST_METHOD'] == 'POST' && isset($_FILES['voice_file'])) {
    $fileName = basename($_FILES['voice_file']['name']);
    $uploadFilePath = $uploadDir . $fileName;

    // 파일을 업로드 폴더에 저장
    if (move_uploaded_file($_FILES['voice_file']['tmp_name'], $uploadFilePath)) {
        // Flask 서버로 파일 업로드 요청
        $params = [
            'voice_file' => new CURLFile($uploadFilePath)
        ];

        $ch = curl_init();
        curl_setopt($ch, CURLOPT_URL, $flask_url);
        curl_setopt($ch, CURLOPT_POST, true);
        curl_setopt($ch, CURLOPT_POSTFIELDS, $params);
        curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
        $response = curl_exec($ch);
        curl_close($ch);

        if ($response !== false) {
            // JSON 응답을 PHP 배열로 변환
            $responseJson = json_decode($response, true);
            $txtFilename = $responseJson['txt_filename'];

            echo '<h1>변환된 텍스트</h1>';
            foreach ($responseJson['speaker_segments'] as $segment) {
                echo '<div class="segment">';
                echo '<div class="speaker-name">화자 ' . htmlspecialchars($segment['speaker']) . ':</div>';
                echo '<div class="text"><p>' . htmlspecialchars($segment['text']) . '</p></div>';
                echo '</div>';
            }
            echo '<a href="' . $flask_url . 'download/' . urlencode($txtFilename) . '" class="download-link">TXT 파일 다운로드</a>';
            echo '<br><br><a href="/">다시 시도</a>';
        } else {
            echo 'Flask 서버에서 응답을 받지 못했습니다.';
        }
    } else {
        echo '파일 업로드에 실패했습니다.';
    }
} else {
    echo '잘못된 요청입니다.';
}
?>
