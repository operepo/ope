<?php
# OPE-Rachel - set admin password to current docker IT password

$pw = getenv("IT_PW");
$pw = md5($pw);
$db = new SQLite3("/var/www/html/modules/admin.sqlite");
$db->exec("DELETE FROM users WHERE username='admin'"); 
$db->exec("INSERT INTO users (username, password) VALUES ('admin', '$pw')");
$db->exec("COMMIT");
$db->close();
?>
