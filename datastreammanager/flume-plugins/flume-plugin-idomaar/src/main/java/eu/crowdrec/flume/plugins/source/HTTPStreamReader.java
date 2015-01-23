package eu.crowdrec.flume.plugins.source;

import java.net.*;
import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;

public class HTTPStreamReader implements IdomaarStreamReader {

	    private BufferedReader reader;
	    
	    public HTTPStreamReader(URL url) throws IOException {
	        
	          /*URLConnection connection = url.openConnection();
	          reader = new BufferedReader(
	                                  new InputStreamReader(
	                                      connection.getInputStream()));
	          */
	          
	          
	          InputStream inp = url.openStream();
	          reader = new BufferedReader(new InputStreamReader(inp));

	    }

	    public String getData() throws IOException {
	        return reader.readLine();
	    }

	    public void close() throws IOException {
	        reader.close();
	    }
	    
}
