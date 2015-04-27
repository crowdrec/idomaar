package eu.crowdrec.idomaar.evaluation.kafka;

import java.io.File;
import java.io.FileReader;
import java.io.IOException;
import java.util.Properties;

public class SimpleKafkaConsumerApp {
	
	private KafkaConsumerConfig loadConfig(String propertiesFileName) {
		Properties properties = new Properties();
		try {
			properties.load(new FileReader(new File(propertiesFileName)));
		} catch (IOException exception) {
			throw new RuntimeException(exception);
		}
		KafkaConsumerConfig config = new KafkaConsumerConfig();
		config.parseFrom(properties);
		return config;
	}
	
	public static void main(String[] args) {
		if (args.length != 1) {
			throw new RuntimeException("Provide a single properties file name.");
		}
		SimpleKafkaConsumerApp application = new SimpleKafkaConsumerApp();
		KafkaConsumerConfig config = application.loadConfig(args[0]);
		final KafkaMultitopicConsumer consumer = new KafkaMultitopicConsumer(config);
		Runtime.getRuntime().addShutdownHook(new Thread() {
			@Override
			public void run() {
				consumer.close();
			}
		});
		consumer.run();
	}

}