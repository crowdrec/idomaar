package eu.crowdrec.flume.plugins.interceptor;

import java.nio.charset.Charset;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.zeromq.ZMQ;
import org.zeromq.ZMQ.Socket;
import org.apache.flume.Context;
import org.apache.flume.Event;
import org.apache.flume.interceptor.Interceptor;

public class IdomaarRecommendationInterceptor implements Interceptor {

private Socket requester;
private org.zeromq.ZMQ.Context zmqContext;
private static final Logger logger = LoggerFactory
.getLogger(eu.crowdrec.flume.plugins.interceptor.IdomaarRecommendationInterceptor.class);

private static String fieldSeparator = "\\t";

public IdomaarRecommendationInterceptor(String hostname){
 
	
	zmqContext = ZMQ.context(1);
    requester = zmqContext.socket(ZMQ.REQ);
    requester.connect(hostname);
    
    
    System.out.println("Launched 0MQ client, bind to " + hostname);
}

@Override
public void initialize() {
   
}



@Override
public Event intercept(Event event) {

    // This is the event's body
    String body = new String(event.getBody());

    // These are the event's headers
    Map<String, String> headers = event.getHeaders();

    // TODO EXTRACT RECOMMENDATION INFO
    // TODO CALCULATE RESPONSE TIME
    // TODO CREATE RESPONSE EVENT
    // TODO IF RECEIVED EOF EXIT AGENT
    
    
    try {
    	// recommendation	46	1362093742	{"reclen":5}    {"subject":"user:27"}
    	String[] parsedRequest = parseRequest(body);
    	if(parsedRequest[0].equals("EOF")) {
    		logger.info("Received end of recommendation file");
    	} else {
    	    logger.info("Requesting recommendation for event ["+body+"]");
    	    if(parsedRequest.length < 5) {
    	    	logger.error("Received wrong data format for event ["+body+"]");
    	    } else {
        	    requester.sendMore("RECOMMEND");
                requester.sendMore(parsedRequest[3]);
                requester.send(parsedRequest[4]);
               
                String reply = requester.recvStr (0);
                logger.info("Received recommendation [" + reply + "]");

                event.setBody(reply.getBytes(Charset.forName("UTF-8")));
    	    }     	    

    	    
    	}
    	
        
    } catch(Exception ex) {
    	logger.info("Exception", ex);
    }
    
       
    // Let the enriched event go
    return event;
}

private String[] parseRequest(String message) {
		return message.split(fieldSeparator);
}

@Override
public List<Event> intercept(List<Event> events) {

    List<Event> interceptedEvents =
            new ArrayList<Event>(events.size());
    for (Event event : events) {
        // Intercept any event
        Event interceptedEvent = intercept(event);
        interceptedEvents.add(interceptedEvent);
    }

    return interceptedEvents;
}

@Override
public void close() {
    //  We never get here but clean up anyhow
    requester.close();
    zmqContext.term();
}

public static class Builder implements Interceptor.Builder {
	private String hostname;
	private int		recommendationLength;
	
    @Override
    public Interceptor build() {
      return new IdomaarRecommendationInterceptor(hostname);
    }
 
    @Override
    public void configure(Context ctx) {
        // Retrieve property from flume conf

		if(System.getProperty("idomaar.recommendation.hostname") != null) {
			this.hostname = System.getProperty("idomaar.recommendation.hostname");
		} else {
			this.hostname = ctx.getString("zeromqSocket");
		}

    }
  }

}

