package eu.crowdrec.idomaar.evaluation.kafka;

import java.util.Properties;

public class KafkaProducerConfig {
	
	public String brokerHostPorts;
	private final int retryBackoffSecs = 1;
	private final int batchSize = 200;
	private final int bufferQueueSize = 1000;
	private final int requiredAcks = 1;
	private final String clientId = "evaluator-producer";
	
	public Properties toProperties() {
		Properties props = new Properties();
		props.put("producer.type", "async");
		props.put("metadata.broker.list", brokerHostPorts);
		props.put("serializer.class", "kafka.serializer.StringEncoder");
		props.put("request.required.acks", Integer.toString(requiredAcks));
		props.put("retry.backoff.ms", Integer.toString(retryBackoffSecs*1000));
		props.put("batch.num.messages", Integer.toString(batchSize));
		//Do not block at all when offering new messages to buffer queue
		props.put("queue.enqueue.timeout.ms", "0");
		//Max message count in buffer queue, default 10000
		props.put("queue.buffering.max.messages", Integer.toString(bufferQueueSize));

		//If no new messages are arrive for this long, the current batch is submitted
		props.put("queue.buffering.max.ms", "5000");
		props.put("client.id", clientId);
		return props;
	}


}
