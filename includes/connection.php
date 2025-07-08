<?php
$db_host = getenv('DB_HOST') ?: 'localhost';
$db_user = getenv('DB_USER') ?: 'root';
$db_pass = getenv('DB_PASSWORD') ?: '';
$db_name = getenv('DB_NAME') ?: 'scms';

$db = mysqli_connect($db_host, $db_user, $db_pass) or
        die ('Unable to connect. Check your connection parameters.');
mysqli_select_db($db, $db_name) or die(mysqli_error($db));
?>