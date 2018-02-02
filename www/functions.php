<?php

include_once 'includes.php';
session_start();

if (isset($_GET['orderid'])):
    $ct = $_SESSION['ct'];
    $ct->cancelOrder($_GET['orderid']);
    echo 'Order #' . $_GET['orderid'] . ' has been cancelled';

endif;

if (isset($_GET['reboot'])):

   echo 'REBOOT: doesn\'t seem to work at the moment';
    exec('reboot');
//    echo exec('/usr/bin/reboot');


endif;
    
