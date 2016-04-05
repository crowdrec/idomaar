package eu.crowdrec.flume.plugins.source;

import com.amazonaws.auth.AWSCredentials;
import com.amazonaws.auth.BasicAWSCredentials;
import org.apache.commons.lang.StringUtils;

public class AwsCreditentialsFactory {

	static AWSCredentials createAWSCreditentials() {
		String accessKey = System.getenv("AWS_ACCESS_KEY_ID");
		if (StringUtils.isBlank(accessKey)) throw new RuntimeException("AWS_ACCESS_KEY_ID environment variable is not set.");
		String secretKey = System.getenv("AWS_SECRET_ACCESS_KEY");
		if (StringUtils.isBlank(secretKey)) throw new RuntimeException("AWS_SECRET_ACCESS_KEY environment variable is not set.");
		return new BasicAWSCredentials(accessKey, secretKey);
	}

}
