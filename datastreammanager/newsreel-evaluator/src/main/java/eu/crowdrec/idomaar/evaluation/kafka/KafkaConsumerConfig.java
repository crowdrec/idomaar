package eu.crowdrec.idomaar.evaluation.kafka;

import java.util.ArrayList;
import java.util.List;
import java.util.Properties;

import org.apache.commons.lang3.builder.ToStringBuilder;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class KafkaConsumerConfig {
	
	private static final Logger log = LoggerFactory.getLogger(KafkaConsumerConfig.class);
	
	public String zkServersString;
	public String topicRegex;
	public String outputDirectory;
	public String separatorString;
	public int commitIntervalMs;
	public boolean restart;
	public long maxMessageCount = -1;
	public String consumerGroupId;
	public String kafkaRootZkPath;
	public boolean appendNewLine;
	public int zkSessionTimeout;
	public int zkConnectionTimeout;

//	RolloverFrequency rolloverFrequency;

	
	List<String> validate() {
		ArrayList<String> messages = new ArrayList<>();
		if (zkServersString == null) messages.add("No zk servers specified.");
		if (outputDirectory == null) messages.add("No output directory.");
		if (consumerGroupId == null || consumerGroupId.contains("/")) messages.add("Consumer group id must be specified and shouldn't "
				+ "contain slashes (/).");
		if (topicRegex == null) log.warn("No topic pattern specified, matching all topics.");
		
		return messages;
	};
	
	void parseFrom(Properties properties) {
		zkServersString = properties.getProperty("zookeeper.servers");
		topicRegex = properties.getProperty("topic.regex");
		outputDirectory = properties.getProperty("output.directory");
		consumerGroupId = properties.getProperty("consumer.group.id");
		maxMessageCount = Long.parseLong(properties.getProperty("max.message.count", "-1"));
		separatorString = properties.getProperty("separator.string", "---");
		kafkaRootZkPath = parseKafkaRootZkPath(zkServersString);
		restart = Boolean.parseBoolean(properties.getProperty("restart", "false"));
		appendNewLine = Boolean.parseBoolean(properties.getProperty("append.newline", "false"));
		zkSessionTimeout = Integer.parseInt(properties.getProperty("zookeeper.session.timeout", "30000"));
		zkConnectionTimeout = Integer.parseInt(properties.getProperty("zookeeper.connection.timeout", "30000"));
		commitIntervalMs = Integer.parseInt(properties.getProperty("commit.interval.ms", "1500"));
		List<String> validationMessages = validate();
		if (!validationMessages.isEmpty()) throw new RuntimeException(validationMessages.toString());
	}
	
	private String parseKafkaRootZkPath(String zkServers) {
		int separatorIndex = zkServers.indexOf('/');
		if (separatorIndex == -1) return "";
		String path = zkServers.substring(separatorIndex);
		log.info("Kafka root path parsed as {}", path);
		return path;
	}
	
	@Override
	public String toString() {
		return ToStringBuilder.reflectionToString(this);
	}
	
}