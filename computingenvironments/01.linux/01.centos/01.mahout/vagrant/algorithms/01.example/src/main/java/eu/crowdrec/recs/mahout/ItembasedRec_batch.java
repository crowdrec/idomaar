package eu.crowdrec.recs.mahout;

import java.io.File;
import java.io.IOException;
import java.util.List;

import org.apache.mahout.cf.taste.common.TasteException;
import org.apache.mahout.cf.taste.impl.recommender.GenericItemBasedRecommender;
import org.apache.mahout.cf.taste.impl.similarity.PearsonCorrelationSimilarity;
import org.apache.mahout.cf.taste.model.DataModel;
import org.apache.mahout.cf.taste.recommender.RecommendedItem;
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

	private static final String RECOMMEND_CMD = "RECOMMEND";
	private static final String TRAIN_CMD = "TRAIN";
	private static final String READINPUT_CMD = "READ_INPUT";
	private static final String STOP_CMD = "STOP";


	private static final int TIMEOUT_TRAINING_RELATIONS = 120;
	private static final String TMP_MAHOUT_USERRATINGS_FILENAME = "mahout_ratings.csv";

	private InternalDataModel dataModel;
	
	private String stagedir = null;
	private Socket communication_socket = null;

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
		Socket comm_sock = context.socket(ZMQ.REQ);
		System.out.println("ALGO: ZMQ created context");
		comm_sock.setReceiveTimeOut(10000);
		System.out.println("ALGO: ZMQ setting timeout");
		System.out.println("ALGO: ZMQ connecting to socket");
		comm_sock.connect(comm);
		System.out.println("ALGO: ZMQ connected to socket");

		ItembasedRec_batch ubr = new ItembasedRec_batch(tmpOutDir, comm_sock);
		ubr.run();

		comm_sock.close();
		context.term();
	}

	public ItembasedRec_batch(String stagedir, Socket socket) throws IOException {
		this.stagedir = stagedir;
		this.communication_socket = socket;
		dataModel = new InternalDataModel(stagedir, TMP_MAHOUT_USERRATINGS_FILENAME);


		System.out.println("ALGO: machine started");
	}

	public void run() throws IOException, TasteException {
		Recommender recommender = null;
		boolean stop = false;

		System.out.println("ALGO: sending READY message");
		communication_socket.send(OUTMSG_READY, 0);
		while ( !stop ) {
			ZMsg recvMsg = null;
			while ( recvMsg == null ) {
				recvMsg = ZMsg.recvMsg(this.communication_socket);
			}
			System.out.println("ALGO: received message: " + recvMsg.toString());
			ZFrame command = recvMsg.remove();

			if (command.streq(READINPUT_CMD)) {
				System.out.println("ALGO: running READ INPUT cmd");
				boolean success = cmdReadinput(recvMsg);

				System.out.println(success ? "ALGO: input correctly read" : "ALGO: failing input read");
				communication_socket.send(success ? OUTMSG_OK : OUTMSG_KO);
			} else if (command.streq(TRAIN_CMD)) {
				System.out.println("ALGO: running TRAIN cmd");
				try {
					recommender = createRecommender(stagedir + File.separator + TMP_MAHOUT_USERRATINGS_FILENAME);

					System.out.println("ALGO: recommender created");
					communication_socket.send(OUTMSG_OK);
				} catch (TasteException e) {
					communication_socket.send(OUTMSG_KO);
				}
			} else if (command.streq(RECOMMEND_CMD)) {
				System.out.println("ALGO: running RECOMMEND cmd");
				ZMsg recomms = null;
				boolean success = (recommender != null && (recomms = cmdRecommend(recvMsg, recommender)).size() > 0 ) ;

				System.out.println(success ? "ALGO: recommedation completed correctly" : "ALGO: failure in generating recommendations");
				if (success)
					recomms.addFirst(OUTMSG_OK);
				else
					recomms.addFirst(OUTMSG_KO);

				recomms.send(communication_socket);
			} else if (command.streq(STOP_CMD)) {
				communication_socket.send(OUTMSG_OK);
				stop = true;
			} else {
				System.out.println("ALGO: unknown command");
			}

		}
		System.out.println("shutdown");
	}

	/*
		subject_etype    user
		subject_eid    1001
		request_timestamp    1404910899
		request_properties    {"device":["smartphone", "android"], "location":"home"}
		recomm_properties    { "explanation":"suggested by your close friends"}
		linked_entities    [{"id":"movie:2001","rating":3.8,"rank":3}, {"id":"movie:2002","rating":4.3,"rank":1}, {"id":"movie:2003","rating":4,"rank":2,"explanation":{"reason":"you like","entity":"movie:2004"}}]
	*/
	protected ZMsg cmdRecommend(ZMsg msg, Recommender recommender) throws IOException, TasteException {
		int reclen = Integer.parseInt( msg.remove().toString() );

		ZMsg recomms = new ZMsg();
		for (ZFrame entityIdStr : msg) {
			String[] entityEls = entityIdStr.toString().split(":");
			if ( entityEls.length == 2 ) {
				String etype = entityEls[0];
				long eid = Long.parseLong(entityEls[1]);
				StringBuilder sb = new StringBuilder();
				sb.append(etype).append("\t");
				sb.append(Long.toString(eid)).append("\t");
				sb.append(System.currentTimeMillis()).append("\t");
				sb.append("{}").append("\t");
				sb.append("{\"reclen\":").append(Integer.toString(reclen)).append("}").append("\t");
				sb.append("[");
				List<RecommendedItem> reclist = recommender.recommend(eid, reclen);
				if ( reclist != null && reclist.size() > 0 ) {
					int rank = 0;
					for ( RecommendedItem item : reclist ) {
						rank++;
						if ( rank > 1 ) {
							sb.append(",");
						}
						sb.append("{");
						sb.append("\"id\":\"").append(item.getItemID()).append("\"");
						sb.append(",");
						sb.append("\"rating\":\"").append(item.getValue()).append("\"");
						sb.append(",");
						sb.append("\"rank\":\"").append(Integer.toString(rank)).append("\"");
						sb.append("}");
					}
				} else {
					// do nothing
				}
				sb.append("]");
				recomms.addString(sb.toString());
			} else {
				// TODO: manage error
			}
		}

		return recomms;
	}

	/*
	 * msg contains:
	 * 	- TYPE
	 *  - ZOOKEEPER ADDRESS
	 *  - TOPIC NAME FOR RELATIONS
	 *  - TOPIC NAME FOR ENTITIES
	 */
	protected boolean cmdReadinput(ZMsg msg) throws IOException {
		if (msg.size() != 3) {
			System.out.println("Wrong number of arguments expected 4, received " + msg.size());
			return false;
		}

		String zookeeper_url = msg.remove().toString();
		String entities_topic = msg.remove().toString();
		String relations_topic = msg.remove().toString();

			
		// Init relations topic
		KafkaConsumer k_relations = new KafkaConsumer(zookeeper_url, "A", relations_topic);
		return k_relations.run(1, dataModel, TIMEOUT_TRAINING_RELATIONS);
		
	}

	protected Recommender createRecommender(String filename) throws IOException, TasteException{
		DataModel model = dataModel.getMahoutFileDataModel();
		ItemSimilarity similarity = new PearsonCorrelationSimilarity(model);
		Recommender recommender = new GenericItemBasedRecommender(model, similarity);
		return recommender;
	}

	
}
