package eu.crowdrec.flume.plugins.source;

import java.io.IOException;

public interface IdomaarStreamReader {
	  public String getData() throws IOException;
	  public void close() throws IOException;
}
