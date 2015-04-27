package eu.crowdrec.idomaar.evaluation;

import java.io.BufferedWriter;
import java.io.FileWriter;
import java.io.IOException;
import java.text.NumberFormat;
import java.text.SimpleDateFormat;
import java.util.Arrays;
import java.util.HashMap;
import java.util.HashSet;
import java.util.Map;
import java.util.TreeMap;
import java.util.concurrent.BlockingQueue;
import java.util.concurrent.TimeUnit;

import org.apache.commons.math3.stat.descriptive.SummaryStatistics;
import org.json.simple.JSONArray;
import org.json.simple.JSONObject;
import org.json.simple.JSONValue;

import eu.crowdrec.idomaar.evaluation.StreamingLinkedFileCacheDuplicateSupport.CacheEntry;

public class StreamingEvaluator implements Runnable {
	
	////////////////////////////////////////////////////////////////////////////
	///// adapt the following line for enabling a detailed evaluation /////////
	////////////////////////////////////////////////////////////////////////////
	
	/**
	 * the fileName for creating a detailed evaluation analysis, set to null for disabling this feature
	 */
	public static final String fileNameDetailedEvaluation = null;
	
	/**
	 * should the response time histogram be printed? - simply set to true if interested in the distribution
	 */
	public final static boolean printResponseTimeHistogram = false;
	
	////////////////////////////////////////////////////////////////////////////
	////////////////////////////////////////////////////////////////////////////
	////////////////////////////////////////////////////////////////////////////
	
	/**
	 * prevent invalid answers, recommending just everything
	 */
	private static final int MAX_NUMBER_OF_RECOMMENDATIONS = 6;
	
	/**
	 * the set of forbidden items
	 */
	private static final HashSet<Long> blackListedItems = new HashSet<Long>();
	static {
		blackListedItems.add(0L);
	}
	
	/**
	 * aggregate the evaluation results for different domains
	 */
	private final static Map<Long, int[]> resultCount = new HashMap<Long, int[]>();
	
	/**
	 * aggregate the evaluation results for different domains  based on a context specific key
	 */
	private final static Map<String, Map<Long, int[]>> resultCountByContextKey = new TreeMap<String, Map<Long, int[]>>();
	
	/**
	 * the timeStamp to contextKey converter (only relevant, if the detailed evaluation is enabled
	 */
	//private final static SimpleDateFormat sdf01 = new SimpleDateFormat("yy'\t'MM'\t'dd'\t'ww'\t'HH'\t'mm'\t'EE");
	//private final static SimpleDateFormat sdf01 = new SimpleDateFormat("yy'\t'MM'\t'dd'\t'ww'\t'HH'\tmm\t'EE");
	private final static SimpleDateFormat sdf01 = new SimpleDateFormat("yy'\t'MM'\t'dd'\t'ww'\t'HH'\tmm\t'EE'\t'yyy'-'MM'-'dd'-'HH");


	/**
	 * The responseTime statistic.
	 */
	private final static SummaryStatistics responseTimeStatistic = new SummaryStatistics();

	/**
	 * create a histogram for debugging (a detailed response time analysis)
	 */
	private final static int[] histogram = new int [500];

	private BlockingQueue<String> predictionQueue;
	private BlockingQueue<String> outputQueue;
	private BlockingQueue<String> groundTruthQueue;
	
	public StreamingEvaluator(BlockingQueue<String> recommendationResultsQueue, BlockingQueue<String> groundTruthQueue, BlockingQueue<String> outputQueue) {
		this.predictionQueue = recommendationResultsQueue;
		this.groundTruthQueue = groundTruthQueue;
		this.outputQueue = outputQueue;
	}
	
	/**
	 * compute a context key based on a timeStamp
	 */
	private static String computeContextKey(long _timeStamp) {
		String tmp = sdf01.format(_timeStamp);
		long q = _timeStamp / 60000L;
		q %= 60L;
		q /= 15L;
		q = 0;
		return tmp + "-" + q;
	}
	
	/**
	 * Write a detailed analysis based on the collected context keys to a file.
	 * @param _fileName
	 */
	private static void writeDetailedStatistic(final String _fileName) {
		BufferedWriter bw = null;
		final long[] keys = {596L, 694L, 1677L};
		try {
			bw = new BufferedWriter(new FileWriter(_fileName));
			bw.write("year\tmonth\tday\tweek\thour\tminute\tweekday\tquarter");
			for (long domainID : keys) {
				bw.write("\tA" + domainID );
				bw.write("\tB" + domainID );
				bw.write("\tC" + domainID );
				bw.write("\tD" + domainID );
				bw.write("\tS" + domainID );
			}
			bw.newLine();
			
			for (Map.Entry<String, Map<Long, int[]>> entry : resultCountByContextKey.entrySet()) {
				bw.write(entry.getKey() + "\t");
				for (long domainID : keys) {
					int[] values = entry.getValue().get(domainID);
					if (values == null) {
						bw.write("0\t0\t0\t0\t");
					} else {
						bw.write(values[0] + "\t" + values[1] + "\t" + values[2] + "\t" + ((double)values[0] / (values[0] + values[1] + 6 * values[2])) + "\t" + (values[0] + values[1] + 6 * values[2]) + "\t");
					}
				}
				bw.newLine();
			}
			
		} catch (Exception e) {
			e.printStackTrace();
		} finally {
			if (bw != null) {
				try {
					bw.close();
				} catch (Exception e) {
					e.printStackTrace();
				}
			}
		}
	}

	/**
	 * Return the log entry for the requested context key an the domain.
	 * @param _contextKey typically a timeStamp
	 * @param _domainID the domainID
	 * @return int-array a log entry 
	 */
	private static int[] getResultCountEntry(final long _contextKey, final Long _domainID) {
		String contextKey = computeContextKey(_contextKey);
		Map<Long, int[]> countEntryForContext = resultCountByContextKey.get(contextKey);
		if (countEntryForContext == null) {
			resultCountByContextKey.put(contextKey, new HashMap<Long, int[]>());
			countEntryForContext = resultCountByContextKey.get(contextKey);
		}
		int[] countEntryForDomainAndContext = countEntryForContext.get(_domainID);
		if (countEntryForDomainAndContext == null) {
			countEntryForContext.put(_domainID, new int[3]);
			countEntryForDomainAndContext = countEntryForContext.get(_domainID);
		}
		return countEntryForDomainAndContext;
	}
	
	private void printAndSend(String message) {
//		System.out.println(message);
		try {
			outputQueue.put(message);
		} catch (InterruptedException exception) {
			throw new RuntimeException(exception);
		}
	}
  
	/**
	 * Run the evaluation process. Ensure that enough heap is available for caching.
	 * The amount of required memory is linear in the number of cached lines / the size of the time window
	 *   considered in the evaluation.
	 *     
	 * @param args the files used in the evaluation.
	 * @throws IOException indicates a problem while searching or opening the ground truth file(s)
	 */
	@Override
	public void run() {
		// define the default window size
		long windowSizeInMillis = 5L * 60L * 1000L;
		
		System.out.println("windowSizeInMillis= " + windowSizeInMillis);
		
		// initialize the groundTruth linked list
		StreamingLinkedFileCacheDuplicateSupport lfc = new StreamingLinkedFileCacheDuplicateSupport();
		try {
			lfc.initialize(groundTruthQueue, windowSizeInMillis);
		} catch (IOException exception) {
			throw new RuntimeException(exception);
		}

		try {
			while (true) {
				String line = predictionQueue.poll(60, TimeUnit.SECONDS);
				if (line == null) {
					System.out.println("Evaluator: no recommendations received for 60 secs, stopping.");
					break;
				}
				if (line.trim().contains("END")) {
					System.out.println("Evaluator received END sign, stopping.");
					break;
				}
				try {
					// ignore comments and invalid lines
					if (line.length() < 2 || line.startsWith("#")) {
						continue;
					}
					// try to parse the prediction line
					String[] token = line.split("\t");
					
					long messageID = Long.parseLong(token[1]);
					long timeStamp = Long.parseLong(token[2]);
					long responseTime = Long.parseLong(token[3]);
					responseTimeStatistic.addValue(responseTime);
					int tmpResponseTime = (int) (responseTime/10);
					if (tmpResponseTime >= histogram.length) {
						tmpResponseTime = histogram.length-1;
					}
					histogram[tmpResponseTime]++;
					//long itemID = Long.parseLong(token[4]);
					
					long userID = -1;
					try {
						userID = Long.parseLong(token[5]);
					} catch (Exception ignored) {
					}
					
					long domainID = Long.parseLong(token[6]);
					
					boolean recommendationAvailable = token.length > 7;
					if (recommendationAvailable) {
						try {
							String recommendations = token[7];
							final JSONObject jsonObj = (JSONObject) JSONValue.parse(recommendations);
							
							JSONObject recs = (JSONObject) jsonObj.get("recs");
							JSONObject recsInts = (JSONObject) recs.get("ints");
							JSONArray itemIds = (JSONArray) recsInts.get("3");
							if (itemIds != null) {
								for (int i = 0;  i < MAX_NUMBER_OF_RECOMMENDATIONS; i++) {
									Long itemID = 
										i < itemIds.size() 
										? Long.parseLong(itemIds.get(i) + "")
										: 0L;
									
									// check the IDs
									eu.crowdrec.idomaar.evaluation.StreamingLinkedFileCacheDuplicateSupport.CacheEntry ce = new CacheEntry(userID, itemID, domainID, timeStamp);
									boolean valid = lfc.checkPrediction(ce, blackListedItems);
									
									//System.out.println("checking:\t" + timeStamp + "\t" + userID + "\t" + domainID + "\t" + itemID + "\t:" + valid) ;
		
									int[] countEntry = resultCount.get(domainID);
									if (countEntry == null) {
										resultCount.put(domainID, new int[3]);
										countEntry = resultCount.get(domainID);
									}

									int[] countEntryForDomainAndContext = getResultCountEntry(timeStamp, domainID);
									if (valid) {
										countEntry[0]++;
										countEntryForDomainAndContext[0]++;
									} else {
										countEntry[1]++;
										countEntryForDomainAndContext[1]++;
									}
								}
							}
						} catch (Exception e) {
							// we assume that no valid recommendation has been provided
							recommendationAvailable = false;
						}
					} // end recommendation available
					if (!recommendationAvailable) {
						//System.out.println("recommendation missing for domain " + domainID);
						int[] countEntry = resultCount.get(domainID);
						if (countEntry == null) {
							resultCount.put(domainID, new int[3]);
							countEntry = resultCount.get(domainID);
						}
						// we count the number of invalid responses
						countEntry[2]++;
						
						int[] countEntryForDomainAndContext = getResultCountEntry(timeStamp, domainID);
						countEntryForDomainAndContext[2]++;
					}

				} catch (Exception e) {
					e.printStackTrace();
					System.err.println("invalid line: " + line);
				}

			}
		} catch (Exception e) {
			e.printStackTrace();
		} 
		// close and cleanup
		try {
			lfc.close();
		} catch (IOException ignored) {
		}
		
		// printout the results
		int[] overall = new int[3];
		final String DELIM = "\t"; 
		printAndSend("\nEvaluation results\n==================");
		for (Map.Entry<Long, int[]> entry: resultCount.entrySet()) {
			int[] values = entry.getValue();
			printAndSend(entry.getKey() + DELIM + Arrays.toString(values) + DELIM + NumberFormat.getInstance().format(1000*values[0] / (values[0]+values[1]+MAX_NUMBER_OF_RECOMMENDATIONS*values[2])) + " o/oo");
			for (int i = 0; i < values.length; i++) {
				overall[i] += values[i];
			}
		}
		printAndSend("all" + DELIM + Arrays.toString(overall) + DELIM + NumberFormat.getInstance().format(1000*overall[0] / (overall[0]+overall[1]+MAX_NUMBER_OF_RECOMMENDATIONS*overall[2])) + " o/oo");
		printAndSend(
				"mean/min/max/stdDev/n" + DELIM + 
				responseTimeStatistic.getMean() + DELIM + 
				responseTimeStatistic.getMin() + DELIM + 
				responseTimeStatistic.getMax() + DELIM + 
				responseTimeStatistic.getStandardDeviation() + DELIM + 
				responseTimeStatistic.getN());
		
		// write a context-key specific evaluation file
		if (fileNameDetailedEvaluation != null) {
			writeDetailedStatistic(fileNameDetailedEvaluation);
		}
		
		// print the histogram for the response time statistic
		if (printResponseTimeHistogram) {
			printAndSend("'==Histogram==");
			for (int i = 0; i < histogram.length; i++) {
				printAndSend((i*10) + DELIM + histogram[i]);
			}
		}
		printAndSend("<END>");
	}
}
