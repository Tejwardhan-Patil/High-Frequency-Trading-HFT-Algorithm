#include <iostream>
#include <fstream>
#include <mutex>
#include <string>
#include <thread>
#include <chrono>
#include <sstream>
#include <ctime>
#include <iomanip>
#include <queue>
#include <condition_variable>
#include <map>
#include <filesystem>

namespace fs = std::filesystem;

// Log levels
enum LogLevel {
    DEBUG = 0,
    INFO,
    WARNING,
    ERROR,
    FATAL
};

// Utility to get current time formatted as a string
std::string getCurrentTime() {
    auto now = std::chrono::system_clock::now();
    std::time_t currentTime = std::chrono::system_clock::to_time_t(now);
    std::tm timeInfo;
#ifdef _WIN32
    localtime_s(&timeInfo, &currentTime);  // Windows-specific localtime
#else
    localtime_r(&currentTime, &timeInfo);  // POSIX-specific localtime
#endif
    std::ostringstream oss;
    oss << std::put_time(&timeInfo, "%Y-%m-%d %H:%M:%S");
    return oss.str();
}

// Logger Class
class Logger {
public:
    static Logger& getInstance() {
        static Logger instance;
        return instance;
    }

    // Disable copy constructors for singleton
    Logger(const Logger&) = delete;
    void operator=(const Logger&) = delete;

    // Set the log file
    void setLogFile(const std::string& filename, std::size_t maxSizeInMB = 5, int maxBackupFiles = 3) {
        std::lock_guard<std::mutex> lock(fileMutex);
        logFileName = filename;
        maxFileSize = maxSizeInMB * 1024 * 1024;
        maxBackupCount = maxBackupFiles;

        logFile.open(logFileName, std::ios::app);
        if (!logFile.is_open()) {
            throw std::runtime_error("Failed to open log file");
        }
        checkLogRotation();
    }

    // Log messages of various levels
    void log(LogLevel level, const std::string& message) {
        std::lock_guard<std::mutex> lock(queueMutex);
        logQueue.push(formatLogMessage(level, message));
        queueCondition.notify_one();
    }

    // Set the logging level to filter messages
    void setLogLevel(LogLevel level) {
        std::lock_guard<std::mutex> lock(levelMutex);
        currentLogLevel = level;
    }

    // Stop the logging thread
    void stop() {
        running = false;
        queueCondition.notify_all();
        if (logThread.joinable()) {
            logThread.join();
        }
    }

private:
    Logger() : running(true), logThread(&Logger::processLogQueue, this), currentLogLevel(INFO) {}

    ~Logger() {
        stop();
        if (logFile.is_open()) {
            logFile.close();
        }
    }

    std::string formatLogMessage(LogLevel level, const std::string& message) {
        if (level < currentLogLevel) {
            return "";  // Skip log messages below the set log level
        }

        std::ostringstream oss;
        oss << "[" << getCurrentTime() << "] ";
        switch (level) {
            case DEBUG: oss << "[DEBUG] "; break;
            case INFO: oss << "[INFO] "; break;
            case WARNING: oss << "[WARNING] "; break;
            case ERROR: oss << "[ERROR] "; break;
            case FATAL: oss << "[FATAL] "; break;
        }
        oss << message;
        return oss.str();
    }

    // Process log queue in a separate thread
    void processLogQueue() {
        while (running) {
            std::unique_lock<std::mutex> lock(queueMutex);
            queueCondition.wait(lock, [this] { return !logQueue.empty() || !running; });

            while (!logQueue.empty()) {
                std::string logMessage = logQueue.front();
                logQueue.pop();
                lock.unlock();
                if (!logMessage.empty()) {
                    writeToLogFile(logMessage);
                }
                lock.lock();
            }
        }
    }

    // Write log message to file
    void writeToLogFile(const std::string& logMessage) {
        std::lock_guard<std::mutex> lock(fileMutex);

        if (logFile.is_open()) {
            logFile << logMessage << std::endl;
            currentFileSize += logMessage.size();
            checkLogRotation();
        } else {
            std::cerr << "Log file not open. Logging to console: " << logMessage << std::endl;
        }
    }

    // Rotate log files if needed
    void checkLogRotation() {
        if (currentFileSize > maxFileSize) {
            logFile.close();
            rotateLogFiles();
            logFile.open(logFileName, std::ios::out);  // Start a new log file
            currentFileSize = 0;
        }
    }

    // Rotate the log files (backup old logs)
    void rotateLogFiles() {
        for (int i = maxBackupCount - 1; i > 0; --i) {
            std::string oldFile = logFileName + "." + std::to_string(i);
            std::string newFile = logFileName + "." + std::to_string(i + 1);

            if (fs::exists(oldFile)) {
                fs::rename(oldFile, newFile);
            }
        }
        std::string backupFile = logFileName + ".1";
        fs::rename(logFileName, backupFile);
    }

    std::mutex queueMutex;
    std::mutex fileMutex;
    std::mutex levelMutex;
    std::condition_variable queueCondition;
    std::queue<std::string> logQueue;
    std::ofstream logFile;

    std::size_t maxFileSize;
    std::size_t currentFileSize = 0;
    int maxBackupCount;

    std::string logFileName;
    bool running;
    LogLevel currentLogLevel;
    std::thread logThread;
};

int main() {
    // Initialize the logger
    Logger& logger = Logger::getInstance();
    logger.setLogFile("system.log", 10, 5);  // Log file size of 10MB, max 5 backup files
    logger.setLogLevel(DEBUG);  // Set logging level to DEBUG

    // Log messages of different severity
    logger.log(DEBUG, "Debugging system initialization.");
    logger.log(INFO, "System initialization complete.");
    logger.log(WARNING, "Potential issue detected.");
    logger.log(ERROR, "Error connecting to database.");
    logger.log(FATAL, "Critical system failure.");

    // Simulate delay
    std::this_thread::sleep_for(std::chrono::seconds(2));

    // Stop the logger
    logger.stop();

    return 0;
}