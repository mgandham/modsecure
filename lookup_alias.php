<html>
<body>
<?php
$t = /* set to boolean indicating if alias is claimed */ 0;
//Welcome test3 <?php echo $_GET["alias"]; ?><br>
if ($t == true){ // alias is claimed
    header("Location: profile.php"); die();
} else { // alias is unclaimed, display signup form
}
?>
<form action="sign_up.php">
    Choose password: <input type="password" name="psw"><br>
    <input type="submit">
</form>

  
</body>
</html>
