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
	private Socket recommendationSocket = null;
	
	private static String zeromqBindAddress = "0.0.0.0";
	private static String zeromqBindPort = "5560";
	
	private String zookeeper_url;
	private String topic;
	
	KafkaConsumer k_relations;
	
	private RecommendationEngine recommendationEngine = null;
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

		Context context = ZMQ.context(1);
		System.out.println("ZMQ creating server socket, binding to " + comm + " to receive messages from orchestrator... ");
		Socket orchestratorSocket = context.socket(ZMQ.REP);
		orchestratorSocket.bind(comm);
//		System.out.println("ZMQ created context");
//		orchestratorSocket.setReceiveTimeOut(10000);
//		System.out.println("ZMQ setting timeout");
//		System.out.println("ZMQ connecting to socket");
//		orchestratorSocket.connect(comm);

//		System.out.println("ZMQ connected to socket");

		Socket recommendationSocket = context.socket(ZMQ.REP);
		String recommendationSocketAddress = getZeromqBindAddress();

		System.out.println("Creating recommendation ZMQ socket and binding to " + recommendationSocketAddress);
		recommendationSocket.bind(recommendationSocketAddress);
		
		
		while(true) {
			ItembasedRec_batch ubr = new ItembasedRec_batch(tmpOutDir, orchestratorSocket, recommendationSocket);
			ubr.run();
		}
		
		//socket_req.close();
		//socket_res.close();
		//context.term();
	}
	
	private static String getZeromqBindAddress() {
		return "tcp://" + zeromqBindAddress + ":" + zeromqBindPort;
	}

	public ItembasedRec_batch(String stagedir, Socket orchestratorSocket, Socket recommendationSocket) throws IOException {
		this.stagedir = stagedir;
		this.orchestratorSocket = orchestratorSocket;
		this.recommendationSocket = recommendationSocket;
		dataModel = new InternalDataModel(stagedir, TMP_MAHOUT_USERRATINGS_FILENAME);
		System.out.println("machine started");
	}

	public void run() throws IOException, TasteException {
		System.out.println("Computing environment running ...");
		Recommender recommender = null;
		boolean stop = false;

//		System.out.println("ALGO: sending READY message");
//		orchestratorSocket.send(OUTMSG_READY, 0);

//		ZMsg initialReqeuest =  ZMsg.recvMsg(orchestratorSocket);
//		System.out.println("Received request: ["+recvMsg+"].");

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
					recommender = createRecommender(stagedir + File.separator + TMP_MAHOUT_USERRATINGS_FILENAME);
					System.out.println("ALGO: recommender created");

					startRecommendationServer(recommender);
					System.out.println("ALGO: Started recommendation engine, zeromq bind to " + getZeromqBindAddress());

					orchestratorSocket.sendMore(OUTMSG_OK);
					orchestratorSocket.sendMore(zeromqBindAddress);
					orchestratorSocket.send(zeromqBindPort);
					
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
			else {
				System.out.println("ALGO: unknown command");
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
	
	protected void startRecommendationServer(Recommender recommender) {
		recommendationEngine = new RecommendationEngine(recommendationSocket, recommender);
		
		 Thread t = new Thread(recommendationEngine);
	     t.start();
	}

	private Recommender createRecommender(String filename) throws IOException, TasteException{
		DataModel model = dataModel.getMahoutFileDataModel();
		ItemSimilarity similarity = new PearsonCorrelationSimilarity(model);
		Recommender recommender = new GenericItemBasedRecommender(model, similarity);
		return recommender;
		
	}
	
	
}
