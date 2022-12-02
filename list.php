<?php

$host="159.223.207.111",
$user="sql_dev_mavmedia",
$password="acDf7XtRxeibxyJw",
$database="sql_dev_mavmedia"

// Create connection
$conn = new mysqli($host, $user, $password, $database);

// Check connection
if ($conn->connect_error) {
  die("Connection failed: " . $conn->connect_error);
}
echo "Connected successfully";
?>
<!DOCTYPE html>
<html lang="en">
<head>
	<meta charset="UTF-8">
	<meta name="viewport" content="width=device-width, initial-scale=1.0">
	<title>List of links</title>
</head>
<body>
	<ul>
		<?php
		$sql = "select distinct(video) from transcript";
		$run = mysqli_query($conn, $sql);
		while($row = mysqli_fetch_array($run)){
			$video = $row["video"];
		?>
		<li><a href="list.php?id=<?php echo $video;?>"><?php echo $video;?></a></li>
	<?php } ?>
	</ul>

	<?php if(isset($_GET["id"])){
		$video = $_GET["id"];
		$sql1 = "select * from transcript where video = '".$video."'";
		$run1 = mysqli_query($conn, $sql1);
		while($row = mysqli_fetch_array($run1)){
			$speaker = $row["speaker"];
			$message = $row["message"];
			$time = $row["time"];
		?>
		<p><?php echo $time; echo "[".$speaker."] "; echo $message;?></p>
		<?php
	}}
		?>
</body>
</html>