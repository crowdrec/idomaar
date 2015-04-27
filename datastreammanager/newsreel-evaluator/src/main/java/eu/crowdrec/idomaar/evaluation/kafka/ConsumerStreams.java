package eu.crowdrec.idomaar.evaluation.kafka;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.Iterator;
import java.util.List;
import java.util.Map;
import java.util.Properties;

import kafka.consumer.Consumer;
import kafka.consumer.ConsumerConfig;
import kafka.consumer.KafkaStream;
import kafka.javaapi.consumer.ConsumerConnector;
import kafka.message.MessageAndMetadata;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class ConsumerStreams {
	
	private static final Logger log = LoggerFactory.getLogger(ConsumerStreams.class);
	
	private final ConsumerConnector consumerConnector;
	
	public ConsumerStreams(KafkaConsumerConfig consumerConfig) {
		consumerConnector = Consumer.createJavaConsumerConnector(createConsumerConnectorConfig(consumerConfig));
	}
	
	private ConsumerConfig createConsumerConnectorConfig(KafkaConsumerConfig config) {
		Properties properties = new Properties();
//	    props.put("socket.receive.buffer.bytes", options.valueOf(socketBufferSizeOpt).toString)
//	    props.put("socket.timeout.ms", options.valueOf(socketTimeoutMsOpt).toString)
//	    props.put("fetch.message.max.bytes", options.valueOf(fetchSizeOpt).toString)
//	    props.put("fetch.min.bytes", options.valueOf(minFetchBytesOpt).toString)
//	    props.put("fetch.wait.max.ms", options.valueOf(maxWaitMsOpt).toString)
//	    props.put("auto.offset.reset", if(options.has(resetBeginningOpt)) "smallest" else "largest")
//	    props.put("consumer.timeout.ms", options.valueOf(consumerTimeoutMsOpt).toString)
		
		properties.put("auto.offset.reset", config.restart ? "smallest" : "largest");
		properties.put("group.id", config.consumerGroupId);
	    properties.put("auto.commit.enable", "false");
	    properties.put("zookeeper.connect", config.zkServersString);
	    properties.put("refresh.leader.backoff.ms", "1000");
		return new ConsumerConfig(properties);
	}
	
	public List<Iterator<MessageAndMetadata<byte[], byte[]>>> subscribe(List<String> topics) {
		log.info("Subscribing to {}", topics);
		List<Iterator<MessageAndMetadata<byte[], byte[]>>> iterators = new ArrayList<>();
		Map<String, Integer> topicCountMap = new HashMap<>();
		for (String topic: topics) topicCountMap.put(topic, 1);
		Map<String, List<KafkaStream<byte[], byte[]>>> streams = consumerConnector.createMessageStreams(topicCountMap);
		for (String topic : topics) {
			iterators.add(streams.get(topic).get(0).iterator());
		}
		return iterators;
	}
	
	public Iterator<MessageAndMetadata<byte[], byte[]>> subscribe(String topic) {
		log.info("Subscribing to {}", topic);
		Map<String, Integer> topicCountMap = new HashMap<>();
		topicCountMap.put(topic, 1);
		Map<String, List<KafkaStream<byte[], byte[]>>> streams = consumerConnector.createMessageStreams(topicCountMap);
		return streams.get(topic).get(0).iterator();
	}
	
	
	void commit() {
		consumerConnector.commitOffsets();
	}
	
	public void close() {
		commit();
		consumerConnector.shutdown();
	}

}
