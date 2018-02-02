<?php

include_once 'includes.php';
session_start();

if (isset($_GET['json'])):

    if (isset($_GET['json_file'])):

        if ($_GET['json_file'] == 'wishlist_form'):
            $file = $_SESSION['dir'] . "json/wishlist.json";
        elseif ($_GET['json_file'] == 'blacklist_form'):
            $file = $_SESSION['dir'] . "json/blacklist.json";
        elseif ($_GET['json_file'] == 'ownedcoins_form'):
            $file = $_SESSION['dir'] . "json/ownedcoins.json";
        endif;

    else:
        $file = $_SESSION['dir'] . "json/settings.json";
    endif;

    $json = json_decode($_GET['json']);

    file_put_contents($file, json_encode($json, JSON_PRETTY_PRINT));

    var_dump($json);

elseif (isset($_GET['blackwish_remove']) && isset($_GET['blackwish_json']) && isset($_GET['blackwish_form'])):

    $filename = explode('_', $_GET['blackwish_form'])[0];

    $file = $_SESSION['dir'] . "json/" . $filename . ".json";
    $_SESSION[$filename . '_json'] = json_decode($_GET['blackwish_json']);

    file_put_contents($file, json_encode($_SESSION[$filename . '_json'], JSON_PRETTY_PRINT));

    echo $_GET['blackwish_remove'] . ' has been removed from the ' . $filename;
//    var_dump($_SESSION[$filename.'_json']);

elseif (isset($_GET['blackwish_add']) && isset($_GET['blackwish_json']) && isset($_GET['blackwish_form'])):

    $filename = explode('_', $_GET['blackwish_form'])[0];

    $file = $_SESSION['dir'] . "json/" . $filename . ".json";
    $_SESSION[$filename . '_json'] = json_decode($_GET['blackwish_json']);

    file_put_contents($file, json_encode($_SESSION[$filename . '_json'], JSON_PRETTY_PRINT));

    echo $_GET['blackwish_add'] . ' has been added to the ' . $filename;
//    var_dump($_SESSION[$filename.'_json']);

endif;

