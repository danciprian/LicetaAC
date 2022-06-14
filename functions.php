<?php 
    require_once('dbconnection.php');
    
    function AppendJsonRow($row){

        return(["dname"=>$row['device_name'],
                "dlocation"=>$row['location'],
                "duid"=>$row['duid'],
                "owner"=>$row['owner']]);
    }

    function AppendJsonDataHistRow($row){
        return(["dname"=>$row['device_name'],
                "time_stamp"=>$row['time_stamp'],
                "temp"=>$row['temperature'],
                "press"=>$row['pressure'],
                "hum"=>$row['humidity']]);
    }

    function add_new_device($d_name, $d_location, $d_uid, $owner) {

        global $db_conn;
        
        if(check_if_device_exists($d_uid)) {
            echo "This device already exists.";
            return;
        }

        $sql = "INSERT INTO devices (`device_name`, `owner`, `duid`, `location`) 
        VALUES ('$d_name', '$owner', '$d_uid', '$d_location')";

        if($db_conn->query($sql) === TRUE) {
            return TRUE;
        } else {
            return FALSE;
        }
    }


    function check_if_device_exists($duid) {
        global $db_conn;
        $sql = "SELECT `duid` from `devices`
                WHERE `duid`='$duid'
                LIMIT 1";

        $result = mysqli_query($db_conn, $sql);
        if(mysqli_num_rows($result) > 0) {
            return TRUE;
        } else {
            return FALSE;
        }
    }

    function get_all_devices() {

        global $db_conn;
        $devices = [];
        $sql = "";

        $sql = "SELECT * from `devices`";

        $result = $db_conn->query($sql);

        while($row = $result->fetch_assoc()) {
            array_push($devices, AppendJsonRow($row));
        }

        return $devices;
    }

    function get_devices_log() {

        global $db_conn;
        $devices = [];
        $sql = "";

        $sql = "SELECT * from `devices_data`
                ORDER BY `time_stamp` DESC";

        $result = $db_conn->query($sql);

        while($row = $result->fetch_assoc()) {
            array_push($devices, AppendJsonDataHistRow($row));
        }

        return $devices;
    }

    function delete_device($device_uniquie_id) {
        global $db_conn;
        $sql = "DELETE FROM `devices`
                WHERE `duid`='$device_uniquie_id'";


        if($db_conn->query($sql) === TRUE) {
            return true;
        } else {
            return false;
        }
    }


    function log_received_data($d_name, $temp, $press, $hum) {
        global $db_conn;
        $sql = "INSERT INTO devices_data (`device_name`, `temperature`, `pressure`, `humidity`) 
        VALUES ('$d_name', '$temp', '$press', '$hum')";

        if($db_conn->query($sql) === TRUE) {
            return TRUE;
        } else {
            return FALSE;
        }
    }


?>