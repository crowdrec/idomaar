package eu.crowdrec.flume.plugins.source;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;

import org.apache.flume.Event;
import org.apache.flume.interceptor.Interceptor;

public class IdomaarRecommendationInterceptor implements Interceptor {

private String hostValue;
private String hostHeader;

public IdomaarRecommendationInterceptor(String hostHeader){
    this.hostHeader = hostHeader;
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

    // Enrich header with hostname
    headers.put(hostHeader, hostValue);

    // Let the enriched event go
    return event;
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
    // At interceptor shutdown
}


}

