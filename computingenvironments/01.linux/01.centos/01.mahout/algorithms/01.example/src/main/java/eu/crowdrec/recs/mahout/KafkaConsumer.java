package eu.crowdrec.recs.mahout;

import kafka.consumer.ConsumerConfig;
import kafka.consumer.KafkaStream;
import kafka.javaapi.consumer.ConsumerConnector;

import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Properties;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;

public class KafkaConsumer {
	private final ConsumerConnector consumer;
	private final String topic;
	private ExecutorService executor;
	private  List<KafkaStream<byte[], byte[]>> streams;
	
	private int numThreads;

	public KafkaConsumer(String a_zookeeper, String a_groupId, String a_topic, int a_numThreads) {
		consumer = kafka.consumer.Consumer
				.createJavaConsumerConnector(createConsumerConfig(a_zookeeper,
						a_groupId));
		this.topic = a_topic;
		this.numThreads = a_numThreads;
	}

	public void shutdown() {
		if (executor != null)
			executor.shutdown();
	}

	public boolean run(int a_numThreads, InternalDataModel dataModel, int timeoutSeconds, boolean writeData) {
		
		if(streams == null) {
			Map<String, Integer> topicCountMap = new HashMap<String, Integer>();
			topicCountMap.put(topic, new Integer(numThreads));
			Map<String, List<KafkaStream<byte[], byte[]>>> consumerMap	= consumer.createMessageStreams(topicCountMap);
			streams = consumerMap.get(topic);
		}
			
		 
		 

		// now launch all the threads
		//
		executor = Executors.newFixedThreadPool(a_numThreads);

		int threadNumber = 0;
		for (final KafkaStream stream : streams) {
			executor.submit(new KafkaConsumerRelationTask(stream, threadNumber, dataModel, writeData));
			threadNumber++;
		}
		executor.shutdown();
		
		try {
			if(!executor.awaitTermination(timeoutSeconds, TimeUnit.SECONDS)){
				executor.shutdownNow();
				
				
				 if (!executor.awaitTermination(60, TimeUnit.SECONDS)) {
			           System.err.println("Pool did not terminate");
				 } else {
					 System.out.println("Timeout in receiving relations");
				 }
				 
				return false;
			}
		} catch (InterruptedException e) {
			e.printStackTrace();
			
			executor.shutdownNow();
			 Thread.currentThread().interrupt();
			
			return false;
		}
		
		return true;
	}

	private static ConsumerConfig createConsumerConfig(String a_zookeeper,
			String a_groupId) {
		Properties props = new Properties();
		props.put("zookeeper.connect", a_zookeeper);
		props.put("group.id", a_groupId);
		props.put("zookeeper.session.timeout.ms", "400");
		props.put("zookeeper.sync.time.ms", "200");
		props.put("auto.commit.interval.ms", "1000");

		return new ConsumerConfig(props);
	}


}
