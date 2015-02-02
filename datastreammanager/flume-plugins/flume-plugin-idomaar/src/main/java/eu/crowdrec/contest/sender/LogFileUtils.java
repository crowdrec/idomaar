package eu.crowdrec.contest.sender;

import org.json.simple.JSONObject;
import org.json.simple.JSONValue;

/**
 * Provide utility functions needed by several different classes.
 * 
 * @author andreas
 *
 */
public class LogFileUtils {
	
	/**
	 * extractEvaluationRelevantDataFromInputLine
	 * @param inputLine
	 * @return new String[]{requestID, userID, itemID, domainID, timeStamp}; if an error has been detected, null
	 */
	public static String[] extractEvaluationRelevantDataFromInputLine(final String inputLine) {
		
		try {
			// detect the data format
			String[] token = inputLine.split("\t");
			if (token.length > 4) {
				
				// idomaar data format
				String relationshipID = token[1];
				String timestamp = token[2];
				
				String tmp = token[4];
				if (tmp.contains("user")) {
					final JSONObject tmpJsonObject = (JSONObject) JSONValue.parse(tmp);
					String userID = "" + tmpJsonObject.get("userID");
					String itemID = "" + tmpJsonObject.get("itemID");
					String domainID = "" + tmpJsonObject.get("domainID");
					return new String[]{relationshipID, userID, itemID, domainID, timestamp};
				}
				
				final JSONObject tmpJsonObject = (JSONObject) JSONValue.parse(token[3]);
				final JSONObject jsonObjectContext = (JSONObject) tmpJsonObject.get("context");
				final JSONObject jsonObjectSimple = (JSONObject) jsonObjectContext.get("simple");
				String userID = "" + jsonObjectSimple.get("userId");
				String itemID = "" + jsonObjectSimple.get("itemId");
				String domainID = "" + jsonObjectSimple.get("domainId");
				return new String[]{relationshipID, userID, itemID, domainID, timestamp};
			} else {
				
				// raw plista data
				final JSONObject tmpJsonObject = (JSONObject) JSONValue.parse(inputLine);
				
				// parse JSON structure to obtain "context.simple"
				JSONObject jsonObjectContext = (JSONObject) tmpJsonObject.get("context");
				JSONObject jsonObjectContextSimple = (JSONObject) jsonObjectContext.get("simple");
				Long domainID = -3L;
				try {
					domainID = Long.valueOf(jsonObjectContextSimple.get("27").toString());
				} catch (Exception ignored) {
					ignored.printStackTrace();
				}	
				Long itemID = null;
				try {
					itemID = Long.valueOf(jsonObjectContextSimple.get("25").toString());
				} catch (Exception ignored) {
					System.err.println("[Exception] no itemID found in " + tmpJsonObject);
				}

				Long userID = -2L;
				try {
					userID = Long.valueOf(jsonObjectContextSimple.get("57").toString());
				} catch (Exception ignored) {
					System.err.println("[Exception] no userID found in " + tmpJsonObject);
				}
			
				String timestamp = "" + tmpJsonObject.get("timestamp");
				return new String[]{timestamp, userID+"", itemID+"", domainID+"", timestamp};
			}
		} catch (Exception e) {
			e.printStackTrace();
			return null;
		}
	}
}
