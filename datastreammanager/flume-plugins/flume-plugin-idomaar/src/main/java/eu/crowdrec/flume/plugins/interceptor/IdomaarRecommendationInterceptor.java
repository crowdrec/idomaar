package eu.crowdrec.flume.plugins.interceptor;

import java.nio.charset.Charset;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.Map;

import com.google.common.base.Preconditions;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.zeromq.ZMQ;
import org.zeromq.ZMsg;
import org.zeromq.ZMQ.Socket;
import org.apache.flume.Context;
import org.apache.flume.Event;
import org.apache.flume.interceptor.Interceptor;
import zmq.ZError;

public class IdomaarRecommendationInterceptor implements Interceptor {

	private static final Logger logger = LoggerFactory.getLogger(eu.crowdrec.flume.plugins.interceptor.IdomaarRecommendationInterceptor.class);

	private Socket requester;
	private Socket orchestratorConnection;

	private final String _hostname;
	private final String orchestratorHostname;
	private final org.zeromq.ZMQ.Context zmqContext;
	private final String recommendationAgentName;
	private final int timeoutMillis;

	private static String fieldSeparator = "\\t";

	public IdomaarRecommendationInterceptor(String hostname, String orchestratorHostname, String recommendationAgentName, int timeoutMillis) {
		_hostname = hostname;
		this.orchestratorHostname = orchestratorHostname;
		this.recommendationAgentName = recommendationAgentName;
		this.timeoutMillis = timeoutMillis;
		zmqContext = ZMQ.context(1);
		requester = zmqContext.socket(ZMQ.REQ);
		requester.setReceiveTimeOut(timeoutMillis);
		orchestratorConnection = ZMQ.context(1).socket(ZMQ.REQ);
	}

	@Override
	public void initialize() {
		requester.connect(_hostname);
		logger.info("Launched 0MQ client, bind to " + _hostname);
		orchestratorConnection.connect(orchestratorHostname);
		logger.info("Launched 0MQ client to connect to orchestrator, bind to " + orchestratorHostname);
	}

	@Override
	public Event intercept(Event event) {
		String body = new String(event.getBody());
		Map<String, String> headers = event.getHeaders();

		// TODO CALCULATE RESPONSE TIME
		// TODO IF RECEIVED EOF EXIT AGENT

		try {
			// recommendation	46	1362093742	{"reclen":5}    {"subject":"user:27"}
			String[] parsedRequest = parseRequest(body);
			if(parsedRequest[0].equals("EOF")) {
				logger.info("Received end of recommendation file");
				orchestratorConnection.sendMore("FINISHED");
				orchestratorConnection.send(recommendationAgentName, ZMQ.NOBLOCK);
			} else {
				logger.info("Requesting recommendation for event ["+body+"]");
				if(parsedRequest.length < 5) {
					logger.error("Received wrong data format for event ["+body+"]");
				} else {
					requester.sendMore("RECOMMEND");
					logger.info("Sending " + parsedRequest[3] + " to recommendation engine.");
					requester.sendMore(parsedRequest[3]);
					requester.send(parsedRequest[4], ZMQ.NOBLOCK);

					ZMsg reply =  ZMsg.recvMsg(requester);
					if (reply == null) {
						if (requester.base().errno() == ZError.EAGAIN) {
							logger.error("Error while waiting for recommendation results for request {}, possible timeout.", Arrays.toString(parsedRequest));
						}
						else {
							logger.error("Error or no answer to recommendation request {}", Arrays.toString(parsedRequest));
						}
					}
					else {
						logger.info("Received recommendation [" + reply + "]");

						String response = body + fieldSeparator + reply.remove().toString();


						// TODO PARSING RESPONSE AND ADD IT TO RESULT
						event.setBody(response.getBytes(Charset.forName("UTF-8")));
					}
				}
			}
		} catch(Exception ex) {
			logger.error("Exception", ex);
		}

		// Let the enriched event go
		logger.info("Sending event [" + new String(event.getBody()) + "]");
		return event;
	}

	private String[] parseRequest(String message) {
		return message.split(fieldSeparator);
	}

	@Override
	public List<Event> intercept(List<Event> events) {
		List<Event> interceptedEvents = new ArrayList<Event>(events.size());
		for (Event event : events) {
			Event interceptedEvent = intercept(event);
			interceptedEvents.add(interceptedEvent);
		}
		return interceptedEvents;
	}

	@Override
	public void close() {
		//  We never get here but clean up anyhow
		requester.close();
		orchestratorConnection.close();
		zmqContext.term();
	}

	public static class Builder implements Interceptor.Builder {
		private String hostname;
		private String orchestratorHostname;
		private String recommendationManagerName;
		private int timeoutMillis;

		@Override
		public Interceptor build() {
			return new IdomaarRecommendationInterceptor(hostname, orchestratorHostname, recommendationManagerName, timeoutMillis);
		}

		private String retrieveProperty(Context context, String systemPropertyName, String contextPropertyName) {
			String systemProperty = System.getProperty(systemPropertyName);
			if (systemProperty != null) return systemProperty;
			return context.getString(contextPropertyName);
		}

		@Override
		public void configure(Context ctx) {
			this.hostname = retrieveProperty(ctx, "idomaar.recommendation.hostname", "zeromqSocket");
			this.orchestratorHostname = retrieveProperty(ctx, "idomaar.orchestrator.hostname", "orchestratorZeromqSocket");
			this.recommendationManagerName = Preconditions.checkNotNull(retrieveProperty(ctx, "idomaar.recommendation.manager.name", "recommendationManagerName"));
			this.timeoutMillis = Integer.parseInt(retrieveProperty(ctx, "idomaar.recommendation.timeout.millis", "timeoutMillis"));
		}
	}

}
