import javax.swing.*;
import java.awt.*;
import java.io.*;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.Random;

public class ProducerConsumerGUI extends JFrame {
    private final JTextField bufferSizeField = new JTextField("10", 5);
    private final JButton startButton = new JButton("Start");
    private final JButton stopButton = new JButton("Stop");
    private final JTextArea bufferArea = new JTextArea(16, 30);
    private final JTextArea logArea = new JTextArea(16, 45);

    private Process cBufferProcess;
    private BufferedWriter cInput;
    private BufferedReader cOutput;
    private final Object cLock = new Object();

    private volatile boolean running = false;
    private Thread producerThread;
    private Thread consumerThread;

    private final Random random = new Random();
    private final DateTimeFormatter formatter = DateTimeFormatter.ofPattern("yyyy-MM-dd_HH:mm:ss.SSS");

    public ProducerConsumerGUI() {
        super("Lab8 Producer / Consumer Min Heap Buffer");
        setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
        setLayout(new BorderLayout(8, 8));

        JPanel topPanel = new JPanel(new FlowLayout(FlowLayout.LEFT));
        topPanel.add(new JLabel("Buffer Size:"));
        topPanel.add(bufferSizeField);
        topPanel.add(startButton);
        topPanel.add(stopButton);
        add(topPanel, BorderLayout.NORTH);

        bufferArea.setEditable(false);
        logArea.setEditable(false);
        add(new JSplitPane(JSplitPane.HORIZONTAL_SPLIT,
                new JScrollPane(bufferArea), new JScrollPane(logArea)), BorderLayout.CENTER);

        startButton.addActionListener(e -> startSystem());
        stopButton.addActionListener(e -> stopSystem());
        stopButton.setEnabled(false);

        setSize(900, 520);
        setLocationRelativeTo(null);
    }

    private void startSystem() {
        try {
            int capacity = Integer.parseInt(bufferSizeField.getText().trim());
            if (capacity <= 0) throw new NumberFormatException();

            String exe = System.getProperty("os.name").toLowerCase().contains("win")
                    ? "MinHeapBuffer.exe" : "./MinHeapBuffer";
            cBufferProcess = new ProcessBuilder(exe).redirectErrorStream(true).start();
            cInput = new BufferedWriter(new OutputStreamWriter(cBufferProcess.getOutputStream()));
            cOutput = new BufferedReader(new InputStreamReader(cBufferProcess.getInputStream()));

            sendCommand("INIT " + capacity);
            running = true;
            startButton.setEnabled(false);
            stopButton.setEnabled(true);
            appendLog("System started. Buffer capacity = " + capacity);

            producerThread = new Thread(this::producerLoop, "ProducerThread");
            consumerThread = new Thread(this::consumerLoop, "ConsumerThread");
            producerThread.start();
            consumerThread.start();
        } catch (Exception ex) {
            JOptionPane.showMessageDialog(this, "Start failed: " + ex.getMessage());
        }
    }

    private void stopSystem() {
        running = false;
        try {
            if (producerThread != null) producerThread.interrupt();
            if (consumerThread != null) consumerThread.interrupt();
            if (cInput != null) sendCommand("STOP");
            if (cBufferProcess != null) cBufferProcess.destroy();
        } catch (Exception ignored) { }
        startButton.setEnabled(true);
        stopButton.setEnabled(false);
        appendLog("System stopped.");
    }

    private void producerLoop() {
        while (running) {
            try {
                int id = 100 + random.nextInt(900);
                String time = LocalDateTime.now().format(formatter);
                String result = sendCommand("ADD " + id + " " + time);
                if ("OK".equals(result)) {
                    appendLog("Produced: item{id=" + id + ", time=" + time + "}");
                    refreshBufferDisplay();
                    Thread.sleep(200); // producer period: about 0.2 seconds
                } else if ("FULL".equals(result)) {
                    appendLog("Buffer full. Producer waits...");
                    Thread.sleep(100);
                } else {
                    appendLog("Producer message: " + result);
                }
            } catch (InterruptedException e) {
                break;
            } catch (Exception e) {
                appendLog("Producer error: " + e.getMessage());
            }
        }
    }

    private void consumerLoop() {
        while (running) {
            try {
                Thread.sleep(240); // machine processing time is about 1.2 times producer time
                String result = sendCommand("POP");
                if (result.startsWith("ITEM")) {
                    appendLog("Consumed lowest ID: " + result.substring(5));
                    refreshBufferDisplay();
                } else if (!"EMPTY".equals(result)) {
                    appendLog("Consumer message: " + result);
                }
            } catch (InterruptedException e) {
                break;
            } catch (Exception e) {
                appendLog("Consumer error: " + e.getMessage());
            }
        }
    }

    private String sendCommand(String command) throws IOException {
        synchronized (cLock) {
            cInput.write(command);
            cInput.newLine();
            cInput.flush();
            return cOutput.readLine();
        }
    }

    private void refreshBufferDisplay() {
        synchronized (cLock) {
            try {
                cInput.write("SNAPSHOT");
                cInput.newLine();
                cInput.flush();
                StringBuilder sb = new StringBuilder();
                String line = cOutput.readLine();
                sb.append(line).append('\n');
                while ((line = cOutput.readLine()) != null) {
                    if ("END".equals(line)) break;
                    sb.append(line).append('\n');
                }
                SwingUtilities.invokeLater(() -> bufferArea.setText(sb.toString()));
            } catch (IOException e) {
                appendLog("Snapshot error: " + e.getMessage());
            }
        }
    }

    private void appendLog(String message) {
        SwingUtilities.invokeLater(() -> {
            logArea.append(message + "\n");
            logArea.setCaretPosition(logArea.getDocument().getLength());
        });
    }

    public static void main(String[] args) {
        SwingUtilities.invokeLater(() -> new ProducerConsumerGUI().setVisible(true));
    }
}
