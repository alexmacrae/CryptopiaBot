<?php
include_once 'header.php';

function get_settings() {

    global $settings;

    echo '<div class="settings">';

    echo '<h2>Settings</h2>';

    echo '<table class="table table-hover">';
    foreach ($settings as $key => $value):
        ?>
        <tr>
            <td>

                <label for="<?php echo $key ?>"><?php echo $key ?></label>
            </td>
            <td>
                <?php if ($key == "MINIMUM_PURCHASE_CRYPTOPIA"): ?>

                    <input disabled class="form-control" id="<?php echo $key ?>" type="" value="<?php echo $value ?>" name="settings[<?php echo $key ?>]" />

                <?php else: ?>

                    <input class="form-control" id="<?php echo $key ?>" type="" value="<?php echo $value ?>" name="settings[<?php echo $key ?>]" />

                <?php endif; ?>

            </td>
        </tr>
        <?php
    endforeach;
    echo '</table>';
    echo '</div>';
}

function get_secrets() {

    global $secrets;

    echo '<div class="secrets">';

    foreach ($secrets as $key => $v):

        echo '<h2>' . $key . '</h2><br>';
        echo '<table class="table table-hover">';
        foreach ($secrets[$key] as $subkey => $value):
            ?>
            <tr>
                <td>
                    <label for="<?php echo $key ?>-<?php echo $subkey ?>"><?php echo $subkey ?></label>
                </td>
                <td>
                    <input class="form-control" id="<?php echo $key ?>-<?php echo $subkey ?>" value="<?php echo $value ?>" name="secrets[<?php echo $key ?>][<?php echo $subkey ?>]" />
                </td>
            </tr>
            <?php
        endforeach;
        echo '</table>';
    endforeach;

    echo '</div>';
}
?>



<form id="settings">

    <div class="form-group"></div>
    <?php
    get_settings();
    ?>

    <div class="form-group">
        <?php
        get_secrets();
        ?>
    </div>
</form>

<button type="button" class="btn btn-primary" id="update">Save Settings</button><button type="button" class="btn btn-secondary" id="reboot">Reboot Raspberry Pi</button>



<?php
include_once 'footer.php';
