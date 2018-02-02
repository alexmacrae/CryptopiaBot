<?php
include_once 'header.php';


try {

    sleep($_SESSION['sleep']);
    
    ?>

    <h2>Order History</h2>

    <table class="table table-hover">
        <thead>
            <tr>
                <th scope="col">Trade ID</th>
                <th scope="col">Market</th>
                <th scope="col">Type</th>
                <th scope="col">Price</th>
                <th scope="col">Amount</th>
                <th scope="col">Total</th>
                <th scope="col">Fee</th>
                <th scope="col">Timestamp</th>

            </tr>

        <tbody>

            <?php
            $results = $ct->tradeHistory();

            for ($i = 0; $i < count($results); $i++):

                if ($i % 2 == 0):
                    echo '<tr class="table-primary">';
                else:
                    echo '<tr class="table-secondary">';
                endif;
                ?>

                <?php
                foreach ($results[$i] as $key => $value):

                    if (is_numeric($value) && $key != 'id'):
                        $value = number_format($value, 8, '.', '');
                    elseif ($key == 'timestamp'):
                        
                        $date = new DateTime($value);
                        $date->setTimezone($timezone);
                        $value = $date->format($dateformat);
                    endif;

                    echo '<td>' . $value . '</td>';
                endforeach;
                ?>
                </tr>
                <?php
            endfor;
            ?>
        </tbody>
    </table>
    <?php
//    print_r($results);
} catch (Exception $e) {
    echo '' . $e->getMessage() . PHP_EOL;
}



include_once 'footer.php';
