
import kafka.serializer.DefaultDecoder
import org.apache.spark.SparkConf
import org.apache.spark.storage.StorageLevel
import org.apache.spark.streaming.kafka.KafkaUtils
import org.apache.spark.streaming.{Seconds, StreamingContext}
import org.apache.log4j.{Level, Logger}

/*
<b>Start Zookeeper & Broker</b>
  bin/zookeeper-server-start.sh config/zookeeper.properties
  bin/kafka-server-start.sh config/server.properties
<b>Start Topic</b>
  bin/kafka-topics.sh --create --zookeeper localhost:2181 --replication-factor 1 --partitions 1 --topic <TOPIC_NAME>
<b>Start Simple Producer</b>
  bin/kafka-console-producer.sh --broker-list localhost:9092 --topic <TOPIC_NAME>
  every line is sent to topic
*/

object KafkaSingleTopic {
  private var ssc: StreamingContext = _
  private val checkPointDirectory: String = "/tmp"
  private val consumerGroup: String = "KafkaSingleTopic_1"

  def streaming(master:String, topicName:String, zookeeper:String) = {
    // Streaming batch interval 10 seconds
    val interval = Seconds(10)
    // Spark configuration
    val sparkConfiguration = {
      val configuration = new SparkConf()
        .setAppName("KafkaSingleTopic")
        .setMaster(master)
        .set("spark.streaming.unpersist", "true")
        .set("spark.serializer", "org.apache.spark.serializer.KryoSerializer")
      configuration
    }
    // Create Streaming Context and configurat checkpoint directory
    ssc = new StreamingContext(sparkConfiguration, interval)
    ssc.checkpoint(checkPointDirectory)
    // Create streams
    val kafkaStream = {
      val kafkaParameters = Map[String, String](
        "zookeeper.connect" -> zookeeper,
        "group.id" -> consumerGroup,
        "auto.offset.reset" -> "smallest",
        "zookeeper.connection.timeout.ms" -> "1000"
      )
      val stream = KafkaUtils.createStream[Array[Byte], Array[Byte], DefaultDecoder, DefaultDecoder](
        ssc,                    // StreamingContext
        kafkaParameters,        // Kafka parameters
        Map(topicName -> 1),    // Partitions for each topic
        storageLevel = StorageLevel.MEMORY_ONLY_SER
      ).map(_._2)
      stream
    }
    // Define the actual data flow of the streaming job
    kafkaStream.foreachRDD(rdd => {
      rdd.foreachPartition(partitionOfRecords => {
        partitionOfRecords.foreach ( x =>
          println(new String(x))
        )
      })
    })

    // Run the streaming job
    ssc.start()
    ssc.awaitTermination()
  }

  /**
   * 1. spark master
   * 2. topic name
   * 3. zookeeper host:port
   */
  def main(args: Array[String]) {

   Logger.getLogger("akka").setLevel(Level.OFF)
   Logger.getLogger("org").setLevel(Level.OFF)
   
   if ( args.length == 3 ) {
      KafkaSingleTopic.streaming(args(0),args(1),args(2))
    } else {
      println("KafkaSingleTopic <spark_master> <topic_name> <zookeeper host:port>")
    }
  }
}
