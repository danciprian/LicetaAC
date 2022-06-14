<?php
require_once("functions.php");

$duid = trim($_POST['duid']);

if(delete_device($duid)){
    echo "ok";
} else {
    echo "nok";
}

?>