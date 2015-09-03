name := "SparkStreaming"
version := "0.1"
scalaVersion := "2.10.4"

libraryDependencies += "org.apache.spark" %% "spark-core" % "1.3.0"
libraryDependencies += "org.apache.spark" %% "spark-streaming" % "1.3.0"
libraryDependencies += "org.apache.spark" %% "spark-streaming-kafka" % "1.3.0"

javaOptions += "-Xmx2G"
scalaHome := Some(file("/opt/apache/scala-2.10.4/"))

skip in update := true