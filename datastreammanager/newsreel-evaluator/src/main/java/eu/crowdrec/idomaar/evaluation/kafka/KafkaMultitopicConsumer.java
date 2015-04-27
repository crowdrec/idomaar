package eu.crowdrec.idomaar.evaluation.kafka;

import java.io.File;
import java.io.UnsupportedEncodingException;
import java.util.ArrayList;
import java.util.Collections;
import java.util.Iterator;
import java.util.List;
import java.util.Timer;
import java.util.TimerTask;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.locks.ReadWriteLock;
import java.util.concurrent.locks.ReentrantReadWriteLock;
import java.util.regex.Pattern;

import kafka.message.MessageAndMetadata;
import kafka.utils.ZkUtils;

import org.I0Itec.zkclient.ZkClient;
import org.I0Itec.zkclient.exception.ZkMarshallingError;
import org.I0Itec.zkclient.exception.ZkNoNodeException;
import org.I0Itec.zkclient.serialize.ZkSerializer;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class KafkaMultitopicConsumer {
	
	private static final Logger log = LoggerFactory.getLogger(KafkaMultitopicConsumer.class);
	
	private final KafkaConsumerConfig config;
	private final List<MessageDumper> messageDumpers = new ArrayList<>();

	KafkaMultitopicConsumer(KafkaConsumerConfig config) {
		this.config = config;
	}

	void run() {
		log.info("Running with config {}", config);
		File outputDirectory = new File(config.outputDirectory);
		ZkClient zkClient = new ZkClient(config.zkServersString, config.zkSessionTimeout, config.zkConnectionTimeout, new Utf8Serializer());
		List<String> allTopics = convert(ZkUtils.getAllTopics(zkClient));
		Collections.sort(allTopics);
		log.info("All topics retrieved {}", allTopics);
		
		checkOtherConsumer(zkClient);
		List<String> filteredTopics = config.topicRegex == null ? allTopics : filter(allTopics, config.topicRegex);
		log.info("Filtered topics {}", filteredTopics);
		
		long startTime = System.currentTimeMillis();
		
		final ConsumerStreams consumerStreams = new ConsumerStreams(config);
		
		final CountDownLatch latch = new CountDownLatch(filteredTopics.size());
		
		List<Iterator<MessageAndMetadata<byte[], byte[]>>> iterators = consumerStreams.subscribe(filteredTopics);
		
		final ReadWriteLock commitLock = new ReentrantReadWriteLock();
		for (int index = 0; index < filteredTopics.size(); index++) {
			String topic = filteredTopics.get(index);
			Iterator<MessageAndMetadata<byte[], byte[]>> iterator = iterators.get(index);
//			RollingTopicWriter topicWriter 
//				= new RollingTopicWriter(outputDirectory, topic, config.separatorString, config.rolloverFrequency, config.appendNewLine);
//			topicWriter.initialize();
			MessageDumper messageDumper = null;
//			new MessageDumper(iterator, topicWriter, config.maxMessageCount, new Runnable() {
//				@Override
//				public void run() {
//					latch.countDown();
//				}
//			}, commitLock.readLock());
			messageDumpers.add(messageDumper);
		}
		log.info("Starting dumpers ...");
		for (MessageDumper dumper : messageDumpers) {
			new Thread(dumper).start();
		}
		Timer timer = new Timer("Periodic flush&commit", true);
		long flushPeriod = config.commitIntervalMs;
		TimerTask task = new TimerTask() {
			@Override
			public void run() {
				log.info("Flushing and committing ...");
				long beforeAcquire = System.currentTimeMillis();
				commitLock.writeLock().lock();
				log.info("Was waiting for write lock for {}, lock acquired", System.currentTimeMillis() - beforeAcquire);
				long startTime = System.currentTimeMillis(); 
				try {
					flush();
					consumerStreams.commit();
				}
				finally {
					commitLock.writeLock().unlock();
				}
				log.info("Committed, took {}", System.currentTimeMillis() - startTime);
			}
		};
		
		timer.schedule(task, flushPeriod, flushPeriod);
		
		try {
			latch.await();
		} catch (InterruptedException exception) {
			throw new RuntimeException(exception);
		}
		task.cancel();
		consumerStreams.close();
		log.info("Took {}", System.currentTimeMillis() - startTime);
	}
	
	void flush() {
		for (MessageDumper dumper: messageDumpers) {
			dumper.flush();
		}
	}
	
	void close() {
		for (MessageDumper dumper: messageDumpers) {
			dumper.close();
		}		
	}
	
	private void checkOtherConsumer(ZkClient zkClient) {
		String idsPath = config.kafkaRootZkPath + "/consumers/" + config.consumerGroupId + "/ids";
		List<String> children;
		try {
			children = zkClient.getChildren(idsPath);
		}
		catch (ZkNoNodeException noNodeException) {
			log.info("No node {} at all.", idsPath);
			children = Collections.emptyList();
		}
		log.info("Children at {}: {}", idsPath, children);
		if (!children.isEmpty()) {
			throw new RuntimeException("Consumer with groupId " + config.consumerGroupId + " is already registered in Zookeeper (so probably running now)."); 
		}
	}
	
	private List<String> filter(List<String> allTopics, String topicRegex) {
		Pattern topicPattern = Pattern.compile(topicRegex);
		List<String> filteredList = new ArrayList<>();
		for (String topic : allTopics) if (topicPattern.matcher(topic).matches()) filteredList.add(topic);
		return filteredList;
	}

	private List<String> convert(scala.collection.Seq<String> seq) {
	    return scala.collection.JavaConversions.seqAsJavaList(seq);
	}

	/**
	 *	Adapted from Kafka's ZKStringSerializer 
	 *
	 */
	private static class Utf8Serializer implements ZkSerializer {

		@Override
		public byte[] serialize(Object data) throws ZkMarshallingError {
			try {
				return ((String)(data)).getBytes("UTF-8");
			} catch (UnsupportedEncodingException exception) {
				throw new RuntimeException(exception);
			}
		}

		@Override
		public Object deserialize(byte[] bytes) throws ZkMarshallingError {
			try {
				return bytes == null ? null : new String(bytes, "UTF-8");
			} catch (UnsupportedEncodingException exception) {
				throw new RuntimeException(exception);
			}
		}

	}

}
