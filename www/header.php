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
    $_SESSION['ownedcoins_json'] = json_decode(file_get_contents($_SESSION['dir'] . "json/ownedcoins.json"), true);

    $settings = $json['settings'];
    $secrets = $json['secrets'];

    $API_KEY = $secrets['cryptopia']['key'];
    $API_SECRET = $secrets['cryptopia']['secret'];

    $API_SUCCESS = False;

    if ($API_KEY && $API_SECRET):

        while ($API_SUCCESS === False):

            try {
                $_SESSION['ct'] = New Cryptopia($API_SECRET, $API_KEY);
                $ct = $_SESSION['ct'];
                sleep($_SESSION['sleep']);
                $API_SUCCESS = True;
                break;
            } catch (Exception $e) {
                echo '<span class="php-error" style="display: none;">' . $e->getMessage() . PHP_EOL . '</span>';
                sleep($_SESSION['sleep']);
            }

        endwhile;

    else:

        echo 'ERROR: API key and secret not entered into settings: ' . $settings_path;

    endif;
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

            </div>
            <?php
            // Get total BTC values

            $currency = 'AUD';

            $marketdata = $ct->getMarketData();

            sleep($_SESSION['sleep']);

            $results = $ct->getBalance();

            sleep($_SESSION['sleep']);

            $btc_balance = 0;

            $btc_total_value = 0;

            for ($i = 0; $i < count($results); $i++):

                if ($results[$i]['Symbol'] == 'BTC'):
                    $btc_balance = $results[$i]['Total'];
                    continue;
                endif;

                if ($results[$i]['Total'] > 0):

                    foreach ($marketdata as $item):

                        $symbol = explode('/', $item['Label'])[0];
                        $market = explode('/', $item['Label'])[1];

                        if ($market != 'BTC'):
                            continue;
                        endif;

                        if ($symbol == $results[$i]['Symbol']):
                            $btc_total_value += $results[$i]['Total'] * $item['LastPrice'];
                            break;
                        endif;

                    endforeach;
                endif;
            endfor;
            ?>
            <form class="form-inline my-2 my-lg-0">
                <p style="text-align: right">
                    BTC available and in trades: <?php echo number_format($btc_total_value, 8) ?><br/>
                    Total BTC value: <?php echo number_format($btc_total_value + $btc_balance, 8); ?><br/>
                    Total AUD value: $<?php echo number_format(($btc_total_value + $btc_balance) / file_get_contents("https://blockchain.info/tobtc?currency=$currency&value=1"), 2); ?>
                </p>
            </form>

        </nav>

        <div id="main">


            <div id="ajax_message">
                <span class="ajax_response"></span>
            </div>
