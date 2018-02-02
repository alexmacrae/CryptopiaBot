<?php
include_once 'includes.php';
session_start();
?>
<!DOCTYPE html>

<html>
    <head>
        <title>CryptopiaBot</title>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">

        <link rel="stylesheet" type="text/css" href="css/flatly/bootstrap.min.css" />


        <style>
            #main{
                padding:20px;
            }
            #settings{

                width: 500px;
            }
            #footer{
                margin-bottom: 0;

            }
            section{
                margin-top:20px;
            }
            .navbar p{
                font-size: 12px;
                color:#fff;
            }

            .navbar-collapse.collapse.in {
                display: block!important; /* Bug fix: stops hamburger menu from closing as soon as it opens */
            }
        </style>

        <style>
            #ajax_message{

                position:fixed;
                top:0;
                width: 100%;
                right:0;
                margin-left:-50%;
                display: flex;
                flex-direction: row;
                flex-wrap: wrap;
                justify-content: center;
                align-items: center;
            }
            #ajax_message.success{
                background: #CCF5CC;
            }
            #ajax_message.error{
                background: #F3A6A6;
            }
            .ajax_response {
                padding: 10px 20px;
                border: 0;
                display: inline-block;
                cursor: pointer;
            }

            .narrow{
                max-width:45%;
                width:45%;
            }

        </style>

    </head>

    <?php
    $timezone = new DateTimeZone('GMT-12'); # The time we're pulling in is already in AUS time. I think php ini is messing with things.
    $dateformat = "h:iA d/m/Y";

    $_SESSION['sleep'] = 1; # Cryptopia needs 1s pause between API calls

    if ($_SERVER['SERVER_ADDR'] == '192.168.1.61'):

        $_SESSION['dir'] = "/root/CryptopiaBot/";
    else:
        $_SESSION['dir'] = "../";
    endif;

    $settings_path = $_SESSION['dir'] . "json/settings.json";

    $json = json_decode(file_get_contents($settings_path), true);

    $settings = $json['settings'];
    $secrets = $json['secrets'];

    $API_KEY = $secrets['cryptopia']['key'];
    $API_SECRET = $secrets['cryptopia']['secret'];

    try {

        $_SESSION['ct'] = New Cryptopia($API_SECRET, $API_KEY);
        $ct = $_SESSION['ct'];
        sleep($_SESSION['sleep']);
    } catch (Exception $e) {
        echo '' . $e->getMessage() . PHP_EOL;
    }
    ?>

    <body>

        <nav class="navbar navbar-expand-lg navbar-dark bg-primary">
            <a class="navbar-brand" href="#">CryptopiaBot</a>
            <button class="navbar-toggler" type="button" data-toggle="collapse" data-target="#navbarColor01" aria-controls="navbarColor01" aria-expanded="false" aria-label="Toggle navigation" style="">
                <span class="navbar-toggler-icon"></span>
            </button>

            <div class="collapse navbar-collapse" id="navbarColor01">
                <ul class="navbar-nav mr-auto">
                    <li class="nav-item active">
                        <a class="nav-link" href="index.php">Settings</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="open-orders.php">Open Orders</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="order-history.php">Order History</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="coin-management.php">Coin Management</a>
                    </li>
                </ul>

                <form class="form-inline my-2 my-lg-0">
                    <p style="text-align: right">
                        BTC total: <?php
                        echo number_format($ct->GetCurrencyBalance("BTC")['Total'], 8);
                        sleep($_SESSION['sleep']);
                        ?><br/>
                        BTC available: <?php echo number_format($ct->GetCurrencyBalance("BTC")['Available'], 8) ?>
                    </p>
                </form>

            </div>

        </nav>


        <div id="main">


            <div id="ajax_message">
                <span class="ajax_response"></span>
            </div>
