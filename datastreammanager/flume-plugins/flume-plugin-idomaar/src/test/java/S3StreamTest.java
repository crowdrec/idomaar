

import org.junit.Test;

import eu.crowdrec.flume.plugins.source.S3StreamReader;
import static org.junit.Assert.*;

import java.io.IOException;
import java.net.URI;
import java.net.URISyntaxException;

public class S3StreamTest {
    @Test
    public void testDownloadPublic() throws URISyntaxException, IOException {
    	URI u = new URI("s3://idomaar-test/test.csv");
    	S3StreamReader reader = new S3StreamReader(u);

    	String data = reader.getData();
    	reader.close();
    	
        assertEquals("1,2,3,4", data);

    }
}