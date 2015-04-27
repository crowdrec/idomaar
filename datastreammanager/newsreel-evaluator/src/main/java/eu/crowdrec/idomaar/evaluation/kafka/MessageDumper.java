package eu.crowdrec.idomaar.evaluation.kafka;

import java.io.IOException;
import java.util.Iterator;
import java.util.concurrent.BlockingQueue;
import java.util.concurrent.atomic.AtomicBoolean;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import kafka.message.MessageAndMetadata;

public class MessageDumper implements Runnable {

	private static final Logger log = LoggerFactory.getLogger(MessageDumper.class);

	private final Iterator<MessageAndMetadata<byte[], byte[]>> source;
	private final AtomicBoolean closed = new AtomicBoolean(false);
	private final long maxMessageCount;
	private final BlockingQueue<String> outputQueue;

	public MessageDumper(Iterator<MessageAndMetadata<byte[], byte[]>> iterator, BlockingQueue<String> outputQueue, long maxMessageCount) {
		this.source = iterator;
		this.outputQueue = outputQueue;
		this.maxMessageCount = maxMessageCount;
	}

	public void run() {
		long messageCount = 0;
		while (!closed.get() && source.hasNext()) {
			try {
				byte[] message = source.next().message();
				try {
					outputQueue.put(new String(message, "UTF-8"));
				} catch (InterruptedException exception) {
					throw new RuntimeException(exception);
				}
				messageCount++;
				if (messageCount == maxMessageCount) closed.set(true);
			} catch (IOException exception) {
				//what to do if one topic fails?
				//log.error("Exception occurred.", exception);
				throw new RuntimeException(exception);
			}
			finally {
				//
			}
		};
		log.info("Dumper closed.");
	}

	void flush() {
		//
	}

	void close() {
		closed.set(true);
	}

}
