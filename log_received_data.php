<?php
require_once("functions.php");

$duid = trim($_POST['duid']);
$temp = trim($_POST['temp']);
$press = trim($_POST['press']);
$hum = trim($_POST['hum']);

if(log_received_data($duid, $temp, $press, $hum)){
    echo "ok";
} else {
    echo "nok";
}

?>