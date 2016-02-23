package eu.crowdrec.flume.plugins.source;

import java.net.*;
import java.io.BufferedReader;
import java.io.FileInputStream;
import java.io.IOException;
import java.io.InputStreamReader;

public class FileStreamReader implements IdomaarStreamReader {

	    private BufferedReader reader;
	    
	    public FileStreamReader(URL url) throws IOException {
	        
	    	FileInputStream inp = new FileInputStream(url.getPath()); 
	         reader = new BufferedReader(new InputStreamReader(inp));
	    }

	    public String getData() throws IOException {
	        return reader.readLine();
	    }

	    public void close() throws IOException {
	        reader.close();
	    }
	    
}
