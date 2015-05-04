import org.apache.spark.SparkContext
import org.apache.spark.streaming.StreamingContext
import org.apache.spark.streaming.Duration
import org.apache.spark.streaming.kafka._
import java.util.HashMap
import java.util.UUID
import org.apache.spark.storage.StorageLevel
import java.util.Properties
import scala.collection.JavaConversions._
import kafka.serializer.StringDecoder
import org.apache.commons.lang3.StringUtils
import kafka.producer.Producer
import kafka.producer.ProducerConfig
import java.util.concurrent.atomic.AtomicReference
import kafka.producer.KeyedMessage
import org.apache.spark.streaming.dstream.DStream
import com.google.common.base.Preconditions
import org.apache.spark.streaming.Seconds

case class StreamingTestConfig(zookeeperConnection: String, kafkaConnection: String, inputTopicName: String, recommendationRequestsTopicName: String,
    groundTruthTopicName: String) {
  def empty(name: String, string: String) = if (StringUtils.isEmpty(string)) throw new Exception("No " + name + " set.") 
  empty("ZK connection", zookeeperConnection)
  empty("Kafka connection", kafkaConnection)
  empty("Input topic name", inputTopicName)
  empty("Recommendation requests topic name", recommendationRequestsTopicName)
  empty("Ground truth topic name", groundTruthTopicName)
}
    
object TestConfigHolder {
  val config = StreamingTestConfig(zookeeperConnection = "192.168.22.5:2181", kafkaConnection="192.168.22.5:9092", inputTopicName = "test",
      recommendationRequestsTopicName = "new-test-reco", groundTruthTopicName = "new-test-ground-truth")
}
    
case object KafkaProducerHolder {
  
  private val producerReference = new AtomicReference[Producer[String,String]](null)
  
  def init(kafkaConnection: String) = {
    val props = new Properties()
    props.put("metadata.broker.list", kafkaConnection)
    props.put("serializer.class", "kafka.serializer.StringEncoder")
    props.put("partitioner.class", "kafka.producer.DefaultPartitioner")
    props.put("request.required.acks", "1")
    val config = new ProducerConfig(props)
    val newProducer = new Producer[String,String](config)
    producerReference.set(newProducer)
    newProducer
  }
  
  def producer(kafkaConnection: String) = {
    val producer = producerReference.get
    if (producer != null) producer else init(kafkaConnection) 
  }
  
}

case class StreamingTask(config: StreamingTestConfig) {
  
  def run(stream: DStream[(String, String)]) = {
    stream.foreachRDD(_.foreachPartition { partition =>
        val producer = KafkaProducerHolder.producer(config.kafkaConnection)
        partition.foreach{ record =>
          val message = record._2
          print("Printed message: " + message)
          val recommendationRequestKeyedMessage = new KeyedMessage[String,String](config.recommendationRequestsTopicName, message)
          producer.send(recommendationRequestKeyedMessage)
          val groundTruthKeyedMessage = new KeyedMessage[String,String](config.groundTruthTopicName, message)
          producer.send(groundTruthKeyedMessage)
        }
    })
  }
}

case class StreamingTest(sparkContext: SparkContext, config: StreamingTestConfig) {
  
  val streamingContext = new StreamingContext(sparkContext, Seconds(1))
  streamingContext.checkpoint("/tmp")
  
  def run() = { 
    val topicPartitionMap = Map(config.inputTopicName -> 1)
    val randomGroupId = "evaluator-test-consumer-" + UUID.randomUUID().toString()
    
    val kafkaParams = Map("zookeeper.connect" -> config.zookeeperConnection, "group.id" -> randomGroupId,
      "zookeeper.connection.timeout.ms" -> "10000", "auto.offset.reset" -> "smallest")
    val kafkaStream = org.apache.spark.streaming.kafka.KafkaUtils.createStream[String, String, StringDecoder, StringDecoder](streamingContext, kafkaParams, topicPartitionMap, StorageLevel.MEMORY_ONLY_SER)
    kafkaStream.print()
//    val streamingTask = StreamingTask(config)
//    streamingTask.run(kafkaStream)
    streamingContext.start()
//    streamingContext.stop()
  }
  
  def stop() = { streamingContext.stop(false) }

}
  
