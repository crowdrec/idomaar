
import java.util.UUID
import org.apache.spark.SparkContext
import org.apache.spark.storage.StorageLevel
import org.apache.spark.streaming.Seconds
import org.apache.spark.streaming.StreamingContext

case class TextFileStreamTest(sparkContext: SparkContext) {
  
  val streamingContext = new StreamingContext(sparkContext, Seconds(1))
  
  def run() = {
    
    val fileStream = streamingContext.textFileStream("/tmp/data")
    fileStream.print()
    streamingContext.start()
//    streamingContext.stop()
  }
  
  def stop() = { streamingContext.stop(false) }

}