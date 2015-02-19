/*
 * Licensed to the Apache Software Foundation (ASF) under one
 * or more contributor license agreements.  See the NOTICE file
 * distributed with this work for additional information
 * regarding copyright ownership.  The ASF licenses this file
 * to you under the Apache License, Version 2.0 (the
 * "License"); you may not use this file except in compliance
 * with the License.  You may obtain a copy of the License at
 *
 * http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing,
 * software distributed under the License is distributed on an
 * "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
 * KIND, either express or implied.  See the License for the
 * specific language governing permissions and limitations
 * under the License.
 */

package eu.crowdrec.flume.plugins.source;

import org.apache.flume.Context;
import org.apache.flume.Event;
import org.apache.flume.EventDrivenSource;
import org.apache.flume.conf.Configurable;
import org.apache.flume.event.EventBuilder;
import org.apache.flume.source.AbstractSource;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.io.IOException;
import java.net.URI;
import java.net.URISyntaxException;
import java.nio.charset.Charset;
import java.util.HashMap;
import java.util.Map;

public class IdomaarSource extends AbstractSource implements EventDrivenSource,
		Configurable {

	private static final Logger logger = LoggerFactory
			.getLogger(eu.crowdrec.flume.plugins.source.IdomaarSource.class);

	// private static SOURCE_TYPES = { "stream", "file" };
	// private static SOURCE_PROTOCOL = ['http', 'https', 'file'];

	private String rowSeparator;
	private String fieldSeparator;

	private int tsField; // THE FIELD NUMBER THAT CONTAINS THE TIMESTAMP
	private Long minimumIntervalBetweenMessages; // milliseconds

	private Charset charset;

	private String url;
	private String type;

	private boolean hasHeader = true;

	private IdomaarStreamReader streamReader;
	private Integer currentLine = 0;

	@Override
	public void configure(Context context) {
		this.rowSeparator = context.getString("rowSeparator", "\\n");
		this.fieldSeparator = context.getString("fieldSeparator", "\\t");
		this.tsField = context.getInteger("tsField", 2);
		this.hasHeader = context.getBoolean("hasHeader", true);

		this.charset = Charset.forName(context.getString("charset", "UTF-8"));

		this.minimumIntervalBetweenMessages = context.getLong(
				"minimumIntervalBetweenMessages", (long) 500);

		
		
		if(System.getProperty("idomaar.url") != null) {
			this.url = System.getProperty("idomaar.url");
		} else {
			this.url = context.getString("url");
		}
	
		if(System.getProperty("idomaar.sourceType") != null) {
			this.type = System.getProperty("idomaar.sourceType");
		} else {
			this.type = context.getString("sourceType");
		}
	
	}
	
	private String getConfigString() {
		return "url=["+url+"] type=["+type+"] minimumIntervalBetweenMessages=["+minimumIntervalBetweenMessages+"] charset=["+charset+"] hasHeader=["+hasHeader+"] tsField=["+tsField+"] fieldSeparator=["+fieldSeparator+"] rowSeparator=["+rowSeparator+"]";
	}

	@Override
    public void start() {
    	 logger.info("Starting Idomaar Source with parameters " + getConfigString());
    	 
    	if(url==null) {
    		logger.error("URL parameters not set, configure that in Flume configuration file or pass it via command line with -Didomaar.url=http://github.com");
    		System.exit(1);
    	} else if(type==null || (!type.equals("stream") && !type.equals("file"))) {
			logger.error("sourceType parameters not set/correct, configure that in Flume configuration file or pass it via command line with -Didomaar.sourceType=file allowed values are 'file' or 'stream'");
    		System.exit(1);
    	} else {
    
    		super.start();
    	
    		
			try {
				startProcessing();
	    		logger.info("Successfully sent " + currentLine + " data ");
	    		stop();
	    		
			} catch (IOException e) {
				logger.error("Unable to execute import", e);
				super.stop();

			} catch (URISyntaxException e) {
				logger.error("Unable to execute import", e);
				super.stop();
			} catch (InterruptedException e) {
				logger.error("Unable to execute import", e);
				super.stop();
			} catch (Exception e) {
				logger.error("Unable to execute import", e);
				super.stop();
			}

            //On successful termination, exit with code 0
			System.exit(0);
			
    	}
    }
	
	public void startProcessing() throws Exception {
		URI uri = new URI(url);
		

		String schema = uri.getScheme();

		//TODO we need to enumerate all the files and foreach file in the directory send it to flume channel
		// currently it use only the specified file
		
		if(schema.equalsIgnoreCase("https") || schema.equalsIgnoreCase("http")) {
			streamReader = new HTTPStreamReader(uri.toURL());
			logger.info("Initialized stream for scheme " + uri.getScheme());
		} else if (schema.equalsIgnoreCase("file")) {
			streamReader = new FileStreamReader(uri.toURL());
			logger.info("Initialized stream for scheme " + uri.getScheme());
		} else {
			logger.error("Unable to read stream for scheme [" + uri.getScheme() + "]");
		}
		
		if(streamReader != null) {
    		 
    		 Long lastTs = (long)-1;
		      Long firstTs = null;
		      
		    			
		      String data = streamReader.getData();
			

    			while ( data != null) {

    				 for(String line:getLines(data)) {
    					 
    					
    					// skip first line if source data has header
    					if(!hasHeader || currentLine>0) {


    					String[] fields = parseLine(line);
    					String eventType = fields[0];

    					if(type.equals("stream")) {
    						
    						Long ts = parseTs(fields);
    						if ( lastTs == -1 ) {	
    							lastTs = ts;
    							firstTs = ts;
    						}

    						logger.debug("field0=["+fields[0]+"] field1=["+fields[1]+"] field2=["+fields[2]+"]");
    						
    						
    						if ( (ts-lastTs)>10) {
    							if( (ts - lastTs) < minimumIntervalBetweenMessages ) {
    								logger.debug("waiting " + (ts-lastTs));
    								Thread.sleep(ts - lastTs);
    							} else {
    								logger.debug("waiting " + minimumIntervalBetweenMessages);
    								Thread.sleep(minimumIntervalBetweenMessages);
    							}

    						}
    						
    						lastTs = ts;
   					 	
    						logger.debug( "absoluteTs=" + ts.toString() + " relativeTs="+ (ts-firstTs) + " currentLine="+currentLine + " fields="+fields);

    					}
    					
    					Map<String, String> headers = new HashMap<String,String>();
    					headers.put("eventType", eventType);

    					Event ev = EventBuilder.withBody(line, charset, headers);
    					
    					getChannelProcessor().processEvent(ev);
    					logger.debug("CurrentLine=["+currentLine+"] line=[" + line + "] eventType=["+eventType+"]");
 

    					} else {
    						logger.debug("CurrentLine=["+currentLine+"] header=[" + line + "]");
    						logger.debug("CurrentLine=["+currentLine+"] headerParsedLength=[" + parseLine(line).length + "]");

    					}

    					currentLine++;

    				}

    				data = streamReader.getData();
    			}
		} else {
			logger.error("Source streams not initialized");
			throw new Exception("Unable to start import for url=["+url+"]");
		}
	}

	@Override
	public void stop() {
		logger.info("Stopping Idomaar Source with type: {}, url: {}", type, url);

		try {
			streamReader.close();
		} catch (IOException e) {
			logger.error("Unable to stop import", e);
		}
		super.stop();

	}

	public Long parseTs(String[] fields) {
		try {
			return Long.parseLong(fields[tsField]);
		} catch (ArrayIndexOutOfBoundsException e) {
			logger.error("Unable to find timestamp in column=["+tsField+"] arrayLength=[" + fields.length + "]");
			throw e;
		}
	}

	public String[] parseLine(String line) {
			return line.split(fieldSeparator);
	}

	public String[] getLines(String data) {
		return data.split(rowSeparator);
	}

}