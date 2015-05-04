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

case class SocketStreamTest(sparkContext: SparkContext) {
  
  val streamingContext = new StreamingContext(sparkContext, Seconds(1))
  streamingContext.checkpoint("/tmp")
  
  def run() = { 
    val stream = streamingContext.socketTextStream("10.0.2.2", 9999, StorageLevel.MEMORY_ONLY)
    stream.print()
    streamingContext.start()
  }
  
  def stop() = { streamingContext.stop(false) }

}
  
