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
	
	private static final String TRAIN_CMD = "TRAIN";
	private static final String RECOMMEND_CMD = "TEST";

	private static final int TIMEOUT_TRAINING_RELATIONS = 120;
	private static final String TMP_MAHOUT_USERRATINGS_FILENAME = "mahout_ratings.csv";

	private InternalDataModel dataModel;
	
	private String stagedir = null;
	private Socket socket_request = null;
	private Socket socket_response = null;
	
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

		System.out.println("ALGO: ZMQ creating context");
		Context context = ZMQ.context(1);
		System.out.println("ALGO: ZMQ created context");
		System.out.println("ALGO: ZMQ creating socket");
		Socket socket_req = context.socket(ZMQ.REQ);
		System.out.println("ALGO: ZMQ created context");
		socket_req.setReceiveTimeOut(10000);
		System.out.println("ALGO: ZMQ setting timeout");
		System.out.println("ALGO: ZMQ connecting to socket");
		socket_req.connect(comm);
		System.out.println("ALGO: ZMQ connected to socket");

		Socket socket_res = context.socket(ZMQ.REP);
		String localSocket = getZeromqBindAddress();
		
		
		System.out.println("Creating zeromq socket " + localSocket);
		socket_res.bind(localSocket);
		
		
		while(true) {
			ItembasedRec_batch ubr = new ItembasedRec_batch(tmpOutDir, socket_req, socket_res);
			ubr.run();
		}
		
		//socket_req.close();
		//socket_res.close();
		//context.term();
	}
	
	private static String getZeromqBindAddress() {
		return "tcp://" + zeromqBindAddress + ":" + zeromqBindPort;
	}

	public ItembasedRec_batch(String stagedir, Socket socket_req, Socket socket_rep) throws IOException {
		this.stagedir = stagedir;
		this.socket_request = socket_req;
		this.socket_response = socket_rep;
		
		
		dataModel = new InternalDataModel(stagedir, TMP_MAHOUT_USERRATINGS_FILENAME);


		System.out.println("ALGO: machine started");
	}

	public void run() throws IOException, TasteException {
		Recommender recommender = null;
		boolean stop = false;

		System.out.println("ALGO: sending READY message");
		socket_request.send(OUTMSG_READY, 0);
		
		while ( !stop ) {
			ZMsg recvMsg = null;
			while ( recvMsg == null ) {
				recvMsg = ZMsg.recvMsg(this.socket_request);
			}
			System.out.println("ALGO: received message: " + recvMsg.toString());
			ZFrame command = recvMsg.remove();

			if (command.streq(TRAIN_CMD)) {
				System.out.println("ALGO: running READ INPUT cmd");
				boolean success = cmdReadinput(recvMsg);

				if(success) {
					recommender = createRecommender(stagedir + File.separator + TMP_MAHOUT_USERRATINGS_FILENAME);
					System.out.println("ALGO: recommender created");

					startRecommendationServer(recommender);
					System.out.println("ALGO: Started recommendation engine, zeromq bind to " + getZeromqBindAddress());

					socket_request.sendMore(OUTMSG_OK);
					socket_request.sendMore(zeromqBindAddress);
					socket_request.send(zeromqBindPort);
					
				} else {
					socket_request.send(OUTMSG_KO);
					System.out.println("ALGO: error in receiving input");
					stop = true;
					
				}
				
			
			} else if (command.streq(RECOMMEND_CMD)) {
				// I NEED TO WAIT THE EOF MESSAGE
				// IN THIS IMPLEMENTATION I DON'T TAKE INTO ACCOUNT ANY STREAM/TEST DATA
			
				System.out.println("ALGO: received "+ RECOMMEND_CMD +" message attaching to queue and waiting for EOF");
				
				
				k_relations.run(1, dataModel, TIMEOUT_TRAINING_RELATIONS, false);

				System.out.println("ALGO: sending ack");
			
				socket_request.send(OUTMSG_OK, 0);
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
		recommendationEngine = new RecommendationEngine(socket_response, recommender);
		
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
