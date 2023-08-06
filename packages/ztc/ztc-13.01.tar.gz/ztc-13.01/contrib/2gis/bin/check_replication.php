
#!/usr/bin/env php
<?php
$dbmaster = new PDO('pgsql:host=$MASTERHOST;port=$DBPORT;dbname=$DBNAME;',$DBUSER,$DBPASS);
$master = $dbmaster->query('SELECT pg_current_xlog_location()')->fetchColumn();

$dbslave = new PDO('pgsql:host=$SLAVEHOST;port=$DBPORT;dbname=$DBNAME;',$DBUSER,$DBPASS');
$slave = $dbslave->query('SELECT pg_last_xlog_replay_location()')->fetchColumn();


if($slave) {
    echo ((text_to_lsn($master) - text_to_lsn($slave))/1000)."\n";
} else {
    echo "0\n";
}

function text_to_lsn($text) {
    list($logid, $xrecoff) = explode('/', $text);
    $lsn = hexdec($logid) * 16 * 1024 * 1024 * 255 + hexdec($xrecoff);
    return $lsn;
}

// try to connect to master and fetch current xlog location
// then slave xlog location
// $lsn = delta xlog --> lag seconds 

