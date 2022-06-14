<?php

require_once("functions.php");

$dname = trim($_POST['dname']);
$dlocation = trim($_POST['dlocation']);
$duid = trim($_POST['duid']);
$owner = trim($_POST['owner']);

if(add_new_device($dname, $dlocation, $duid, $owner)){
    echo "ok";
} else {
    echo " Device not created.";
}

?>