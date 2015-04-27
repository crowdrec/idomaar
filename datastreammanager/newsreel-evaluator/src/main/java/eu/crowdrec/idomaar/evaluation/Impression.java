package eu.crowdrec.idomaar.evaluation;

import java.text.ParseException;
import java.text.SimpleDateFormat;
import java.util.HashMap;
import java.util.Map;

import org.json.simple.JSONObject;
import org.json.simple.JSONValue;

/**
 * An impression object. Should contain userID, itemID, domainID, and timeStamp.
 * Additional values or jSON might also be available.
 * 
 * @author andreas
 *
 */
public class Impression {

	///////////////////////////////////////////////////////////////////////////////////////////
    // define the final constants
	///////////////////////////////////////////////////////////////////////////////////////////

	
	/** The threadLocal simpleDateFormat - typically parsers are not threadsafe, this we define them as thread-local. */
	public static final ThreadLocal<SimpleDateFormat> dateFormatter = new ThreadLocal<SimpleDateFormat>(){
        @Override
        protected SimpleDateFormat initialValue()
        {
        	// the Date pattern used by R (default) //
            return new SimpleDateFormat("yyyy-MM-dd HH:mm:ss");
        }
    };
	
	// access keys - an enumeration  would be nice here 
	public static final Integer USER_ID = 1;
	public static final Integer ITEM_ID = 2;
	public static final Integer DOMAIN_ID = 3;
	public static final Integer TIMESTAMP_ID = 4;
	public static final Integer TARGET_ID = 5;
	public static final Integer TEAM_ID = 6;
	public static final Integer TEXT_ID = 7;
	public static final Integer NUMBER_OF_REQUESTED_RESULTS_ID = 8;
	public static final Integer OPERATING_SYSTEM_ID = 15;
	public static final Integer BROWSER_ID = 16;
	public static final Integer ORGINAL_EVENT_TYPE = 20;
	
	///////////////////////////////////////////////////////////////////////////////////////////
    // settings and member variables
	///////////////////////////////////////////////////////////////////////////////////////////
	
	/** is the date in the csvFile provided as javaScript long value? */
	public static boolean timeStampInCsvIsJavaScriptLong = true;
	
	/** the JSON content, might be null */
	private String json = null;
	
	/** a hashMap storing the impression properties */
	private final Map<Integer, Object> valuesByID = new HashMap<Integer, Object>();
	
	///////////////////////////////////////////////////////////////////////////////////////////
    // Constructors
	///////////////////////////////////////////////////////////////////////////////////////////
	
	/**
	 * Default constructor.
	 */
	private Impression() {
		super();
	}
	
	/**
	 * Convenient constructor.
	 *
	 * @param userID the userID
	 * @param itemID the itemID
	 * @param domainID the domainID
	 * @param timeStamp the timeStamp
	 */
	public Impression(final Long userID, final Long itemID, final Long domainID, final Long timeStamp) {
		this();
		this.valuesByID.put(USER_ID, userID);
		this.valuesByID.put(ITEM_ID, itemID);
		this.valuesByID.put(DOMAIN_ID, domainID);
		this.valuesByID.put(TIMESTAMP_ID, timeStamp);
	}
	
	
	///////////////////////////////////////////////////////////////////////////////////////////
    // setter and getter
	///////////////////////////////////////////////////////////////////////////////////////////
	
	/**
	 * Does the impression contain plain JSON
	 * @return is JSON provided
	 */
	public boolean supportsJSON() {
		return this.json == null;
	}
	
	
	/**
	 * Getter for userID. (convenience)
	 * @return the userID
	 */
	public Long getUserID() {
		return (Long) valuesByID.get(USER_ID);
	}
	
	/**
	 * Getter for itemID. (convenience) 
	 * @return the itemID
	 */
	public Long getItemID() {
		return (Long) valuesByID.get(ITEM_ID);
	}

	/**
	 * Setter for itemID. (convenience) 
	 * @param _itemID the itemID
	 */
	public void setItemID(final Long _itemID) {
		this.valuesByID.put(ITEM_ID, _itemID);
	}

	/**
	 * Getter for domainID. (convenience)
	 * @return the domainID
	 */
	public Long getDomainID() {
		return (Long) valuesByID.get(DOMAIN_ID);
	}
	
	/**
	 * Getter for TimeStamp. (convenience)
	 * @return the timeStamp
	 */
	public Long getTimeStamp() {
		return (Long) valuesByID.get(TIMESTAMP_ID);
	}
	
	/**
	 * Getter for targetID. (convenience)
	 * @return the targetID
	 */
	public Long getTargetID() {
		return (Long) valuesByID.get(TARGET_ID);
	}
	
	/**
	 * Setter for targetID. (convenience)
	 * @param targetID the targetID
	 */
	public void setTargetID(final Long targetID) {
		valuesByID.put(TARGET_ID, targetID);
	}

	/**
	 * Getter for teamID. (convenience)
	 * @return  the teamID
	 */
	public Long getTeamID() {
		return (Long) valuesByID.get(TEAM_ID);
	}
	
	/**
	 * Setter for teamID. (convenience)
	 * @param teamID the the teamID
	 */
	public void setTeamID(final Long teamID) {
		valuesByID.put(TEAM_ID, teamID);
	}

	/**
	 * Getter for text (convenience).
	 * @return the text
	 */
	public String getText() {
		return (String) valuesByID.get(TEXT_ID);
	}
	
	/**
	 * Setter for text. (convenience)
	 * @param text the text.
	 */
	public void setText(final String text) {
		valuesByID.put(TEXT_ID, text);
	}


	/**
	 * Getter for numberOfRequestedResults (convenience).
	 * @return the text
	 */
	public Integer getNumberOfRequestedResults() {
		return (Integer) valuesByID.get(NUMBER_OF_REQUESTED_RESULTS_ID);
	}
	
	/**
	 * Setter for numberOfRequestedResults. (convenience)
	 * @param numberOfRequestedResults the number of requested results.
	 */
	public void setNumberOfRequestedResults(final Integer numberOfRequestedResults) {
		valuesByID.put(NUMBER_OF_REQUESTED_RESULTS_ID, numberOfRequestedResults);
	}
	
	/**
	 * Getter for Operating System (convenience)
	 * @return the operating system
	 */
	public String getOperatingSystem() {
		return (String) this.valuesByID.get(OPERATING_SYSTEM_ID);
	}
	
	/**
	 * Setter for Operating System (convenience)
	 * @param _operatingSystem the value to be set
	 */
	public void setOperatingSystem(final String _operatingSystem) {
		if (_operatingSystem != null) {
			this.valuesByID.put(OPERATING_SYSTEM_ID, _operatingSystem);
		}
	}
	
	/**
	 * Getter for Browser (convenience)
	 * @return the browser
	 */
	public String getBrowser() {
		return (String) this.valuesByID.get(BROWSER_ID);
	}
	
	/**
	 * Setter for Browser (convenience)
	 * @param _operatingSystem the value to be set
	 */
	public void setBrowser(final String _browser) {
		if (_browser != null) {
			this.valuesByID.put(BROWSER_ID, _browser);
		}
	}
	
	/**
	 * Getter for general values. Use the static members as key.
	 * @return the value for the key. Might return null;
	 */
	public Object getValue(Integer key) {
		return valuesByID.get(key);
	}
	
	///////////////////////////////////////////////////////////////////////////////////////////
    // Utility functions
	///////////////////////////////////////////////////////////////////////////////////////////
	
	/**
	 * Create an impression from a 4 column CSV file
	 * @param line the line of a CSV file
	 * @return an Impression
	 * @throws ParseException dateParseExpection
	 * @throws NumberFormatException numberFormatParseException
	 */
	public static Impression createImpressionFrom4CollCSV(String line) throws ParseException, NumberFormatException {
		
		// parse the line
		String[] token = line.split("\t");
		
		// if the line contains only one token, handle the line as plan json
		if (token.length < 4) {
			return createImpressionFromJSON(line);
		}
		
		// extract the relevant information
		String messageType = token[0];
		long messageID = Long.parseLong(token[1]);
		long timeStamp = Long.parseLong(token[2]);
		final JSONObject jOE = (JSONObject) JSONValue.parse(token[4]);

		long userID;
		try {
			userID =  (Long) jOE.get("userID");
		} catch (Exception e) {
			userID = -1;
		}
		
		long itemID;
		try {
			itemID = (Long) jOE.get("itemID");
		} catch (Exception e) {
			itemID = -1;
		}
		final long domainID = (Long) jOE.get("domainID");

		final JSONObject jOET3 = (JSONObject) JSONValue.parse(token[3]);
		final String originalEventType = (String) jOET3.get("event_type");
		
		// create the instance
		Impression result = new Impression();
		result.valuesByID.put(USER_ID, userID);
		result.valuesByID.put(ITEM_ID, itemID);
		result.valuesByID.put(DOMAIN_ID, domainID);
		result.valuesByID.put(TIMESTAMP_ID, timeStamp);
		result.valuesByID.put(ORGINAL_EVENT_TYPE, originalEventType);

		return result;
	}

	/**
	 * Create an impression object from a line of JSON code.
	 * @param line a line containing a JSON object
	 * @return an impression object
	 * @throws ParseException
	 * @throws NumberFormatException
	 */
	public static Impression createImpressionFromJSON(final String line) throws ParseException, NumberFormatException {
		
		// parse the line
		final JSONObject jOE = (JSONObject) JSONValue.parse(line);
		final JSONObject jOContext = (JSONObject) jOE.get("context");
		final JSONObject jOContextSimple = (JSONObject) jOContext.get("simple");

		long userID;
		try {
			userID =  (Long) jOContextSimple.get("57");
		} catch (Exception e) {
			userID = 0;
		}
		
		long itemID;
		try {
			itemID = (Long) jOContextSimple.get("25");
		} catch (Exception e) {
			itemID = 0;
		}
		final long domainID = (Long) jOContextSimple.get("27");
		final long timeStamp = (Long) jOE.get("timestamp");
		final String originalEventType = (String) jOE.get("event_type");

		
		// create the instance
		Impression result = new Impression();
		result.valuesByID.put(USER_ID, userID);
		result.valuesByID.put(ITEM_ID, itemID);
		result.valuesByID.put(DOMAIN_ID, domainID);
		result.valuesByID.put(TIMESTAMP_ID, timeStamp);
		result.valuesByID.put(ORGINAL_EVENT_TYPE, originalEventType);

		return result;
	}

}
