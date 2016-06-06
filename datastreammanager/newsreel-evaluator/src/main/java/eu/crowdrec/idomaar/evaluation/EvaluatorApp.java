package eu.crowdrec.idomaar.evaluation;

import java.util.UUID;
import java.util.concurrent.BlockingQueue;
import java.util.concurrent.LinkedBlockingQueue;

import org.apache.log4j.BasicConfigurator;
import org.apache.log4j.ConsoleAppender;
import org.apache.log4j.Level;
import org.apache.log4j.Logger;
import org.apache.log4j.PatternLayout;

import eu.crowdrec.idomaar.evaluation.kafka.ConsumerStreams;
import eu.crowdrec.idomaar.evaluation.kafka.KafkaConsumerConfig;
import eu.crowdrec.idomaar.evaluation.kafka.KafkaProducerConfig;
import eu.crowdrec.idomaar.evaluation.kafka.MessageDumper;
import kafka.javaapi.producer.Producer;
import kafka.producer.KeyedMessage;
import kafka.producer.ProducerConfig;

/**
 * Reads ground truth and recommendation results from Kafka topics and writes evaluation results back to Kafka. 
 *
 */
public class EvaluatorApp {

	private Producer<String, String> createProducer(KafkaProducerConfig config) {
		ProducerConfig producerConfig = new ProducerConfig(config.toProperties());
		return new Producer<>(producerConfig);
	}
	
	private void run(String[] args) throws Exception {
		String zookeeperConnection = args[0];
		String kafkaConnection = args[1];
		String recommendationResultsTopic = args[2];
		String groundTruthTopic = args[3];
		String outputTopic = args[4];

		KafkaConsumerConfig config = new KafkaConsumerConfig();
		config.restart = true;
		config.consumerGroupId = UUID.randomUUID().toString();
		config.zkServersString = zookeeperConnection;
		ConsumerStreams consumerStreams = new ConsumerStreams(config);
		ConsumerStreams groundTruthConsumerStreams = new ConsumerStreams(config);

		BlockingQueue<String> recommendationResultsQueue = new LinkedBlockingQueue<String>(2000);
		MessageDumper recommendationResultDumper = new MessageDumper(consumerStreams.subscribe(recommendationResultsTopic), 
				recommendationResultsQueue, config.maxMessageCount);

		BlockingQueue<String> groundTruthQueue = new LinkedBlockingQueue<String>(2000);
		MessageDumper groundTruthDumper = new MessageDumper(groundTruthConsumerStreams.subscribe(groundTruthTopic), 
				groundTruthQueue, config.maxMessageCount);

		new Thread(recommendationResultDumper).start();
		new Thread(groundTruthDumper).start();

		KafkaProducerConfig producerConfig = new KafkaProducerConfig();
		producerConfig.brokerHostPorts = kafkaConnection;
		Producer<String, String> producer = createProducer(producerConfig);
		
		BlockingQueue<String> outputQueue = new LinkedBlockingQueue<String>(2000);
		StreamingEvaluator evaluator = new StreamingEvaluator(recommendationResultsQueue, groundTruthQueue, outputQueue);
		new Thread(evaluator).start();

		while (true) {
			String message = outputQueue.take();
			if (message.equals("<END>")) System.exit(0);
			producer.send(new KeyedMessage<String, String>(outputTopic, message));
			System.out.println(message);
		}

	}

	public static void main(String[] args) throws Exception {
		Logger root = Logger.getRootLogger();
	    root.addAppender(new ConsoleAppender(new PatternLayout(PatternLayout.TTCC_CONVERSION_PATTERN)));
	    root.setLevel(Level.WARN);
		new EvaluatorApp().run(args);
		
	}

}
