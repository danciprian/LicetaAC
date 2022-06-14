<?php

    $server   = "danciprian.go.ro";
    $user     = "dcd";
    $password = "58abf97d22A";
    $db_name  = "licenta";
    $port     = 3306;

    // Create connection
    $db_conn = new mysqli($server, $user, $password, $db_name, $port);

    // Check connection
    if($db_conn->connect_error) {
        die("Connection failed: " . $db_conn->connect_error);
    }

?>