package eu.crowdrec.recs.mahout;


import java.io.IOException;

import kafka.consumer.ConsumerIterator;
import kafka.consumer.KafkaStream;


	public class KafkaConsumerRelationTask implements Runnable {
	    private KafkaStream m_stream;
	    private int m_threadNumber;
	    private InternalDataModel m_dataModel;
	 
	    public KafkaConsumerRelationTask(KafkaStream a_stream, int a_threadNumber, InternalDataModel a_dataModel) {
	        m_threadNumber = a_threadNumber;
	        m_stream = a_stream;
	        m_dataModel = a_dataModel;
	        
	    }
	 
	    public void run() {
	    	int lines=0;
	    	ConsumerIterator<byte[], byte[]> it = m_stream.iterator();
	    	boolean shutdown = false;
	        while (!shutdown && it.hasNext() ) {
	        	try {
					boolean isEof = !m_dataModel.writeRelation(it.next().message());
					lines++;
					if(isEof) {
				        System.out.println("Received EOF, readed " + lines + " messages ");
				        
				        shutdown = true;
					}
					
				} catch (NumberFormatException e) {
					// TODO Auto-generated catch block
					e.printStackTrace();
				} catch (IOException e) {
					// TODO Auto-generated catch block
					e.printStackTrace();
				}   	
	        }
	        System.out.println("Shutting down Thread: " + m_threadNumber);
	        
	    }
	}
