package eu.crowdrec.flume.plugins.source;

import com.amazonaws.AmazonClientException;
import com.amazonaws.auth.AWSCredentials;
import com.amazonaws.auth.BasicAWSCredentials;
import com.amazonaws.auth.profile.ProfileCredentialsProvider;
import com.amazonaws.services.s3.AmazonS3;
import com.amazonaws.services.s3.AmazonS3Client;
import com.amazonaws.services.s3.AmazonS3URI;
import com.amazonaws.services.s3.model.GeneratePresignedUrlRequest;
import org.apache.commons.lang.StringUtils;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.net.URI;
import java.net.URL;

public class S3StreamReader implements IdomaarStreamReader {

	private BufferedReader reader;

	public S3StreamReader(URI uri) throws IOException {
		AmazonS3 s3 = new AmazonS3Client(AwsCreditentialsFactory.createAWSCreditentials());
		AmazonS3URI amazonURI = new AmazonS3URI(uri);
		GeneratePresignedUrlRequest request = new GeneratePresignedUrlRequest(amazonURI.getBucket(), amazonURI.getKey());
		URL httpUrl = s3.generatePresignedUrl(request);
		InputStream inp = httpUrl.openStream();
		reader = new BufferedReader(new InputStreamReader(inp));
	}

	public String getData() throws IOException {
		return reader.readLine();
	}

	public void close() throws IOException {
		reader.close();
	}

}
