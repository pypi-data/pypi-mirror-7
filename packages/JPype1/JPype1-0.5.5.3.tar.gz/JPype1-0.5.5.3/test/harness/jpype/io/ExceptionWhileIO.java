package jpype.io;

import java.io.FileNotFoundException;
import java.io.IOException;
import java.io.RandomAccessFile;
import java.nio.ByteBuffer;
import java.nio.channels.FileChannel;


public class ExceptionWhileIO {
	RandomAccessFile file;
	ByteBuffer buff;
	
	public ExceptionWhileIO(String filename) throws FileNotFoundException {
		file = new RandomAccessFile(filename, "r");
		buff = ByteBuffer.allocate(8192);
	}
	
	public void read() throws IOException {
		FileChannel channel = file.getChannel();
		int readBytes = 0, count = 0;
		long pos = 0;
		while ((readBytes = channel.read(buff) != 0) {
			System.out.println("read bytes: " + readBytes);
			if (count == 4)
				throw new IOException("expected");
			
			count++;
		}
	}
	
	public static void main(String[] args) throws IOException, FileNotFoundException {
		ExceptionWhileIO io = new ExceptionWhileIO("/tmp/foo");
		io.read();
	}
}