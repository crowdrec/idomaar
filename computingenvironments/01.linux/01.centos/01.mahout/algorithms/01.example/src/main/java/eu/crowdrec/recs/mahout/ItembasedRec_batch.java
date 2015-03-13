package eu.crowdrec.recs.mahout;

import java.io.File;
import java.io.IOException;

import org.apache.mahout.cf.taste.common.TasteException;
import org.apache.mahout.cf.taste.impl.recommender.GenericItemBasedRecommender;
import org.apache.mahout.cf.taste.impl.similarity.PearsonCorrelationSimilarity;
import org.apache.mahout.cf.taste.model.DataModel;
import org.apache.mahout.cf.taste.recommender.Recommender;
import org.apache.mahout.cf.taste.similarity.ItemSimilarity;
import org.zeromq.ZMQ;
import org.zeromq.ZMQ.Socket;
import org.zeromq.ZMQ.Context;
import org.zeromq.ZMsg;
import org.zeromq.ZFrame;

public class ItembasedRec_batch {

	private static final String OUTMSG_READY = "READY";
	private static final String OUTMSG_OK = "OK";
	private static final String OUTMSG_KO = "KO";

	private static final String HELLO = "HELLO";
	private static final String TRAIN_CMD = "TRAIN";
	private static final String RECOMMEND_CMD = "TEST";

	private static final int TIMEOUT_TRAINING_RELATIONS = 120;
	private static final String TMP_MAHOUT_USERRATINGS_FILENAME = "mahout_ratings.csv";

	private InternalDataModel dataModel;
	
	private String stagedir = null;
	private Socket orchestratorSocket = null;
	private String ipAddressToThisHost;

	private String zookeeper_url;
	private String topic;
	
	KafkaConsumer k_relations;
	
	/**
	 *
	 * @param args
	 * $0: stage directory: directory where the algorithm can persist data (e.g., temp files, models,..)
	 * $1: communication directory: directory reserved to communication messages
	 * @throws IOException
	 * @throws NumberFormatException
	 * @throws TasteException
	 */
	public static void main(String[] args) throws NumberFormatException, IOException, TasteException {

		if ( args.length < 2 ) {
			System.out.println("missing parameters");
			return;
		}

		String tmpOutDir = args[0];
		String comm = args[1];

		String ipAddressToThisHost = args[2];

		Context context = ZMQ.context(1);
		System.out.println("ZMQ creating server socket, binding to " + comm + " to receive messages from orchestrator... ");
		Socket orchestratorSocket = context.socket(ZMQ.REP);
		orchestratorSocket.bind(comm);

		while(true) {
			ItembasedRec_batch ubr = new ItembasedRec_batch(tmpOutDir, orchestratorSocket, ipAddressToThisHost);
			ubr.run();
		}
		
		//socket_req.close();
		//socket_res.close();
		//context.term();
	}

	public ItembasedRec_batch(String stagedir, Socket orchestratorSocket, String ipAddressToThisHost) throws IOException {
		this.stagedir = stagedir;
		this.orchestratorSocket = orchestratorSocket;
		this.ipAddressToThisHost = ipAddressToThisHost;
		dataModel = new InternalDataModel(stagedir, TMP_MAHOUT_USERRATINGS_FILENAME);
		System.out.println("machine started");
	}

	public void run() throws IOException, TasteException {
		System.out.println("Computing environment running ...");
		boolean stop = false;

		while ( !stop ) {
			ZMsg recvMsg = null;
			while ( recvMsg == null ) {
				System.out.println("Waiting for message ...");
				recvMsg = ZMsg.recvMsg(this.orchestratorSocket);
			}
			System.out.println("Message from orchestrator: " + recvMsg.toString());
			ZFrame command = recvMsg.remove();

			if (command.streq(HELLO)) {
				orchestratorSocket.send(OUTMSG_READY);
				System.out.println("Sent " + OUTMSG_READY + " to orchestrator.");
			}
			else if (command.streq(TRAIN_CMD)) {
				System.out.println("Running READ INPUT cmd");
				boolean success = cmdReadinput(recvMsg);

				if(success) {
					Recommender recommender = createRecommender(stagedir + File.separator + TMP_MAHOUT_USERRATINGS_FILENAME);
					System.out.println("ALGO: recommender created");

					RecommendationEngine recommendationEngine = startRecommendationServer(recommender);
					String recommendationEndpoint = recommendationEngine.getAddress(ipAddressToThisHost);
					System.out.println("ALGO: Started recommendation engine, zeromq last endpoint to " + recommendationEndpoint);

					orchestratorSocket.sendMore(OUTMSG_OK);
					orchestratorSocket.send(recommendationEndpoint);

				} else {
					orchestratorSocket.send(OUTMSG_KO);
					System.out.println("ALGO: error in receiving input");
					stop = true;
					
				}
			}
			else if (command.streq(RECOMMEND_CMD)) {
				// I NEED TO WAIT THE EOF MESSAGE
				// IN THIS IMPLEMENTATION I DON'T TAKE INTO ACCOUNT ANY STREAM/TEST DATA
			
				System.out.println("ALGO: received "+ RECOMMEND_CMD +" message attaching to queue and waiting for EOF");
				
				
				k_relations.run(1, dataModel, TIMEOUT_TRAINING_RELATIONS, false);

				System.out.println("ALGO: sending ack");
			
				orchestratorSocket.send(OUTMSG_OK, 0);
				stop = true;
			}
			else if (command.streq("STOP")) {
				System.out.println("Received STOP message, shutting down.");
				orchestratorSocket.send("OK");
				System.exit(0);
			}
			else {
				System.out.println("ALGO: unknown command");
				orchestratorSocket.send("UNKNOWN");
			}
		}
		System.out.println("shutdown");
	}

	

	/*
	 * msg contains:
	 * 	- TYPE
	 *  - ZOOKEEPER ADDRESS
	 *  - TOPIC NAME FOR RELATIONS
	 *  - TOPIC NAME FOR ENTITIES
	 */
	protected boolean cmdReadinput(ZMsg msg) throws IOException {
		if (msg.size() != 2) {
			System.out.println("Wrong number of arguments expected 2, received " + msg.size());
			return false;
		}

		zookeeper_url = msg.remove().toString();
		topic = msg.remove().toString();
		k_relations = new KafkaConsumer(zookeeper_url, "A", topic, 1);
			
		return k_relations.run(1, dataModel, TIMEOUT_TRAINING_RELATIONS, true);
		
	}
	
	protected RecommendationEngine startRecommendationServer(Recommender recommender) {
		RecommendationEngine recommendationEngine = new RecommendationEngine(recommender);
		new Thread(recommendationEngine).start();
		return recommendationEngine;
	}

	private Recommender createRecommender(String filename) throws IOException, TasteException{
		DataModel model = dataModel.getMahoutFileDataModel();
		ItemSimilarity similarity = new PearsonCorrelationSimilarity(model);
		Recommender recommender = new GenericItemBasedRecommender(model, similarity);
		return recommender;
		
	}
	
	
}
