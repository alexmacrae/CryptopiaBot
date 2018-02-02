<?php
include_once 'header.php';

$ownedcoins_json = json_decode(file_get_contents($_SESSION['dir'] . "json/ownedcoins.json"), true);
$_SESSION['wishlist_json'] = json_decode(file_get_contents($_SESSION['dir'] . "json/wishlist.json"), true);
$_SESSION['blacklist_json'] = json_decode(file_get_contents($_SESSION['dir'] . "json/blacklist.json"), true);
?>

<section id="coin-management">

    <h2>Coin Management</h2>

    <?php
    try {
        sleep($_SESSION['sleep']);
        ?>
        <form id="ownedcoins_form">
            <table class="table table-hover">
                <thead>
                    <tr>
                        <th scope="col">Coin ID</th>
                        <th scope="col">Symbol</th>
                        <th scope="col">Total</th>
                        <th scope="col">Available</th>
                        <th scope="col">Held For Trades</th>
                        <th scope="col">Status</th>
                        <th scope="col">HODL</th>

                    </tr>

                <tbody>

                    <?php
                    $results = $ct->getBalance();

                    $ignore_keys = array('Unconfirmed', 'PendingWithdraw', 'Address', 'StatusMessage', 'BaseAddress');

                    for ($i = 0; $i < count($results); $i++):

                        if ($results[$i]['Total'] > 0 && $results[$i]['Symbol'] != 'BTC'):
                            echo '<tr class="table-secondary coin-row" name="' . $results[$i]['Symbol'] . '">';

                            $hodl = 'false';

                            foreach ($ownedcoins_json as $key => $v):
                                $json_coin = $key;

                                if ($json_coin == $results[$i]['Symbol']):

                                    $hodl = strtolower($v['hodl']);

                                endif;

                            endforeach;


                            foreach ($results[$i] as $key => $value):

                                if (in_array($key, $ignore_keys) != 1):


                                    if (is_numeric($value) && $key != 'CurrencyId'):
                                        $value = number_format($value, 8, '.', '');
                                    endif;

                                    echo '<td class="' . $key . '">' . $value . '</td>';
                                endif;
                            endforeach;

                            $hodl_checked = '';
                            if ($hodl == 'true'):
                                $hodl_checked = ' checked';
                            endif;
                            ?>
                        <td>
                            <input class="coin-name" name="<?php echo $results[$i]['Symbol'] ?>[Symbol]" type="hidden" value="<?php echo $results[$i]['Symbol'] ?>" />
                            <input class="coin-hodl" type="checkbox"<?php echo $hodl_checked ?>/>
                            <input class="coin-hodl-hidden" type="hidden" name="<?php echo $results[$i]['Symbol'] ?>[hodl]" value="<?php echo $hodl ?>" />
                        </td>

                        <?php
                        echo '</tr>';
                    endif;
                    ?>

                    <?php
                endfor;
                ?>
                </tbody>
            </table>
        </form>
        <?php
//    print_r($results);
    } catch (Exception $e) {
        echo '' . $e->getMessage() . PHP_EOL;
    }
    ?>

</section>

<section id="wishlist">
    <h2>Wishlist</h2>

    <form id="wishlist_form">
        <table class="table table-hover narrow">
            <thead>
                <tr>
                    <th scope="col">Coin</th>
                    <th scope="col">Hodl</th>
                    <th scope="col">Remove</th>
                </tr>
            </thead>
            <tbody>
                <?php
                foreach ($_SESSION['wishlist_json'] as $key => $value):

                    $hodl = strtolower($value['hodl']);



                    $hodl_checked = '';
                    if ($hodl == 'true'):
                        $hodl_checked = ' checked';
                    endif;

                    echo '<tr class="table-success coin-row" name="' . $key . '"><td>' . $key . '</td>';
                    echo '<td><input class="coin" type="hidden" name="' . $key . '[Symbol]" value="' . $key . '" />';

                    echo '<input class="coin-hodl" type="checkbox"' . $hodl_checked . ' />';

                    echo '<input class="coin-hodl-hidden" type="hidden" name="' . $key . '[hodl]" value="' . $hodl . '" />
                            
                        </td>';
                    echo '<td><button type="button" class="btn btn-secondary remove" remove-coin="' . $key . '">Remove</button></td></tr>';

                endforeach;
                ?>

                <tr class="table-secondary new-coin">
                    <td>
                        <input class="coin-name" />
                    </td>
                    <td>
                        <input type="checkbox" class="coin-hodl" />
                        <input class="coin-hodl-hidden" type="hidden" />
                    </td>
                    <td><button type="button" class="btn btn-primary add-coin" id="wishlist-button">Add</button></td></tr>
            </tbody>
        </table>

    </form>



</section>

<section id="blacklist">
    <h2>Blacklist</h2>
    <form id="blacklist_form">
        <table class="table table-hover narrow">
            <thead>
                <tr>
                    <th scope="col">Coin</th>
                    <th scope="col">Remove</th>
                </tr>
            </thead>
            <tbody>
                <?php
                foreach ($_SESSION['blacklist_json'] as $key => $value):

                    echo '<tr class="table-danger coin-row" name="' . $key . '"><td>' . $key . '</td>';
                    echo '<td><input class="coin" type="hidden" name="' . $key . '[Symbol]" value="' . $key . '" />';
                    echo '<button type="button" class="btn btn-secondary remove" remove-coin="' . $key . '">Remove</button></td></tr>';

                endforeach;
                ?>
                <tr class="table-secondary new-coin">
                    <td>
                        <input class="coin-name" />
                    </td>
                    <td>
                        <button type="button" class="btn btn-primary add-coin" id="blacklist-button">Add</button>
                    </td>
                </tr>
            </tbody>
        </table>


    </form>



</section>





<?php
include_once 'footer.php';
