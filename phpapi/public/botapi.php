<?php
declare(strict_types = 1);
require_once dirname(__FILE__, 2)."/pass/discordbotpass.php";
try{
    $pdo = new PDO("mysql:host=".getHost()."; dbname=".getDBName()."; charset=utf8mb4", getUser(), getPassword());
    $pdo->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
    $pdo->setAttribute(PDO::ATTR_EMULATE_PREPARES, false);
}catch(PDOException $e){
    echo "error";
    exit();
}
if($_SERVER["REQUEST_METHOD"] == "POST"){
    //パスワードチェック
    $passwordStatement = $pdo->prepare("select * from user where id = 1");
    $passwordStatement->execute();
    $dbpassword = $passwordStatement->fetch(PDO::FETCH_ASSOC);
    if (!password_verify($_POST["password"], $dbpassword["password"])) {
        echo "password error";
        exit();
    }
    
    $statement = $pdo->prepare("insert into record (id, date, record) values (NULL, CURRENT_TIMESTAMP, :input)");
    $statement->bindValue(":input", $_POST["input"], PDO::PARAM_STR);
    $statement->execute();
    //成功したらsuccessと返す
    echo "success";
}

if($_SERVER["REQUEST_METHOD"] == "GET"){
    $statement = $pdo->prepare("select record from record where record like '%運動%'");
    $statement->execute();
    $count = 0;
    while($rec = $statement ->fetch(PDO::FETCH_ASSOC)){
        //空白削除
        $rec = str_replace(" ", "", $rec);
        $isMatch1 = preg_match("/[0-9]*分/", $rec["record"], $matchWithMintue);
        if($isMatch1 == 1){
            $isMatch2 = preg_match("/[0-9]*/", $matchWithMintue[0], $match);
            if($isMatch2 == 1){
                $count = $count + $match[0];
            }
        }
        
        
    }
    echo $count;
}