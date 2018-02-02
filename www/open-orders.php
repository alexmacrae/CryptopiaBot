<?php
include_once 'header.php';


try {

    sleep($_SESSION['sleep']);
    ?>

    <h2>Open Orders</h2>

    <table class="table table-hover">
        <thead>
            <tr>
                <th scope="col">Order ID</th>
                <th scope="col">Market</th>
                <th scope="col">Type</th>
                <th scope="col">Price</th>
                <th scope="col">Amount</th>
                <th scope="col">Total</th>
                <th scope="col">Remaining</th>
                <th scope="col">Time / Date</th>
                <th scope="col">Cancel order</th>

            </tr>

        <tbody>

            <?php
            $results = $ct->activeOrders();



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
                
                echo '<td><button type="button" class="cancel" orderid="'.$results[$i]['id'].'">Cancel</button></td>';    
                
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
