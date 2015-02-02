package eu.crowdrec.flume.plugins.interceptor;

import java.io.IOException;
import java.io.UnsupportedEncodingException;
import java.net.URLEncoder;
import java.nio.charset.Charset;
import java.util.ArrayList;
import java.util.List;

import org.apache.commons.httpclient.HttpClient;
import org.apache.commons.httpclient.HttpConnectionManager;
import org.apache.commons.httpclient.MultiThreadedHttpConnectionManager;
import org.apache.commons.httpclient.methods.PostMethod;
import org.apache.commons.httpclient.methods.StringRequestEntity;
import org.apache.commons.httpclient.params.HttpConnectionManagerParams;
import org.apache.flume.Context;
import org.apache.flume.Event;
import org.apache.flume.interceptor.Interceptor;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import eu.crowdrec.contest.sender.LogFileUtils;

/**
 * This class integrates a http service into to flume based stream.
 * 
 * @author andreas
 *
 */
public class IdomaarHTTPRecommendationInterceptor implements Interceptor {

	/**
	 * define a http client supporting multiple connections 
	 */
	private final static HttpConnectionManager httpConnectionManager = new MultiThreadedHttpConnectionManager();
	static {

		final HttpConnectionManagerParams httpConnectionManagerParams = new HttpConnectionManagerParams();
		httpConnectionManagerParams.setDefaultMaxConnectionsPerHost(100);
		httpConnectionManagerParams.setMaxTotalConnections(100);
		httpConnectionManager.setParams(httpConnectionManagerParams);
	}
	final static HttpClient httpClient = new HttpClient(httpConnectionManager);

	
	/**
	 * the default logger
	 */
	private static final Logger logger = LoggerFactory.getLogger(IdomaarHTTPRecommendationInterceptor.class);

	
	/**
	 * hostName and port as string 
	 */
	private String _hostnameAndPort;

	/**
	 * The constructor
	 * 
	 * @param _hostnameAndPort hostName:port
	 */
	public IdomaarHTTPRecommendationInterceptor(String _hostnameAndPort) {
		this._hostnameAndPort = _hostnameAndPort;
	}

	/**
	 * Initialize the component.
	 * @see org.apache.flume.interceptor.Interceptor#initialize()
	 */
	@Override
	public void initialize() {
		logger.info("Launched httpClient client, connecting to " + _hostnameAndPort);
	}

	/** 
	 * create a http request based on a message, send the received answer.
	 * @see org.apache.flume.interceptor.Interceptor#intercept(org.apache.flume.Event)
	 */
	@Override
	public Event intercept(Event event) {
		
		// initialize the result string
		String response = null;
		
		try {
			// extract the message body
			String body = new String(event.getBody());
			
			// split the logLine into several token
			String[] token = body.split("\t");

			// extract the relevant token
			String type = token[0];
			String property = token[3];
			String entity = token[4];
			
			// encode the content as HTTP URL parameters.
			String urlParameters = "";
			try {
				urlParameters = String.format("type=%s&properties=%s&entities=%s",
						URLEncoder.encode(type, "UTF-8"),
						URLEncoder.encode(property, "UTF-8"),
						URLEncoder.encode(entity, "UTF-8"));
			} catch (UnsupportedEncodingException e1) {
				System.err.println(e1.toString());
			}
			
			// end the http request and wait for a response
			PostMethod postMethod = null;
			try {
				StringRequestEntity requestEntity = new StringRequestEntity(
						urlParameters, "application/x-www-form-urlencoded", "UTF-8");

				postMethod = new PostMethod("http://" + _hostnameAndPort);
				postMethod.setParameter("useCache", "false");
				postMethod.setRequestEntity(requestEntity);

				int statusCode = httpClient.executeMethod(postMethod);
				response = postMethod.getResponseBodyAsString();

				response = response.trim();
			} catch (IOException e) {
				logger.info("problems during handling the http connection, ignored.");
			} finally {
				if (postMethod != null) {
					postMethod.releaseConnection();
				}
			}
			
			
			// create a log line for the evaluator
			boolean answerExpected = false;
			if (body.contains("\"event_type\": \"recommendation_request\"")) {
				answerExpected = true;
			}
			if (answerExpected) {
				logger.debug("serverResponse: " + response);
				
				// extract the most relevant information from the request for preparing the log for the evaluator 
				String[] data = LogFileUtils.extractEvaluationRelevantDataFromInputLine(body);
				String requestId = data[0];
				String userId = data[1];
				String itemId = data[2];
				String domainId = data[3];
				String timeStamp = data[4];

				String responseLogLine = 
					"prediction\t" + requestId + "\t" + timeStamp + "\t" + itemId+ "\t" + userId + "\t" + domainId + "\t" + response;
				
				event.setBody(responseLogLine.getBytes(Charset.forName("UTF-8")));	

			}
			
			// PARSING RESPONSE AND ADD IT TO RESULT
			event.setBody(response.getBytes(Charset.forName("UTF-8")));

		} catch (Exception ex) {
			logger.error("Exception", ex);
		}

		// Let the enriched event go
		logger.info("Sending event [" + new String(event.getBody()) + "]");
		return event;
	}

	@Override
	public List<Event> intercept(List<Event> events) {

		List<Event> interceptedEvents = new ArrayList<Event>(events.size());
		for (Event event : events) {
			// Intercept any event
			Event interceptedEvent = intercept(event);
			interceptedEvents.add(interceptedEvent);
		}

		return interceptedEvents;
	}

	@Override
	public void close() {
		// We never get here but clean up anyhow

	}

	public static class Builder implements Interceptor.Builder {
		private String _hostnameAndPort;

		@Override
		public Interceptor build() {
			return new IdomaarHTTPRecommendationInterceptor(
					this._hostnameAndPort);
		}

		@Override
		public void configure(Context ctx) {
			// Retrieve property from flume conf

			if (System.getProperty("idomaar.recommendation.hostname") != null) {
				this._hostnameAndPort = System
						.getProperty("idomaar.recommendation.hostname");
			} else {
				this._hostnameAndPort = ctx.getString("httpSocket");
			}

		}
	}
}
